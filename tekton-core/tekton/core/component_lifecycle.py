#!/usr/bin/env python3
"""
Component Lifecycle Module

This module provides enhanced component state management and lifecycle control
to prevent deadlocks during the startup process.
"""

import os
import json
import time
import uuid
import asyncio
import logging
from typing import Dict, List, Any, Optional, Set, Callable, Awaitable, Tuple, TypedDict

from .lifecycle import (
    ComponentState,
    ReadinessCondition,
    ComponentRegistration,
    PersistentMessageQueue
)
from .dependency import DependencyResolver
from .registry import (
    _load_registrations,
    _save_registrations,
    register_component,
    update_component_state,
    get_component_info,
    monitor_component_health
)
from .readiness import (
    register_readiness_condition,
    check_readiness_conditions,
    mark_component_ready,
    wait_for_component_ready,
    wait_for_dependencies
)

logger = logging.getLogger("tekton.component_lifecycle")


class ComponentRegistry:
    """
    Registry for tracking component registrations and instances.
    
    Manages component registrations, detects duplicate instances, and 
    handles component lifecycle state transitions.
    """
    
    def __init__(self, data_dir: Optional[str] = None):
        """
        Initialize the component registry.
        
        Args:
            data_dir: Optional directory for persistent storage
        """
        self.data_dir = data_dir or os.path.expanduser("~/.tekton/registry")
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Internal storage
        self.components: Dict[str, ComponentRegistration] = {}
        self.instances: Dict[str, Dict[str, Any]] = {}
        self.readiness_conditions: Dict[str, Dict[str, ReadinessCondition]] = {}
        
        self.lock = asyncio.Lock()
        
        # Load registrations from disk if available
        self.components, self.instances = _load_registrations(self.data_dir)
    
    async def register_component(self, registration: ComponentRegistration) -> Tuple[bool, str]:
        """
        Register a component with the registry.
        
        Args:
            registration: ComponentRegistration object
            
        Returns:
            Tuple of (success, message)
        """
        async with self.lock:
            return await register_component(
                self.components, 
                self.instances, 
                registration, 
                self.data_dir
            )
    
    async def update_component_state(self, 
                                 component_id: str, 
                                 instance_uuid: str,
                                 state: str,
                                 metadata: Optional[Dict[str, Any]] = None) -> Tuple[bool, str]:
        """
        Update the state of a component.
        
        Args:
            component_id: Component ID
            instance_uuid: Instance UUID
            state: ComponentState value
            metadata: Optional additional metadata
            
        Returns:
            Tuple of (success, message)
        """
        async with self.lock:
            return await update_component_state(
                self.components,
                self.instances,
                component_id,
                instance_uuid,
                state,
                metadata,
                self.data_dir
            )
    
    async def register_readiness_condition(self,
                                     component_id: str,
                                     condition_name: str,
                                     check_func: Callable[[], Awaitable[bool]],
                                     description: Optional[str] = None,
                                     timeout: Optional[float] = 60.0) -> Tuple[bool, str]:
        """
        Register a readiness condition for a component.
        
        Args:
            component_id: Component ID
            condition_name: Condition name
            check_func: Async function that returns True if condition is satisfied
            description: Optional description
            timeout: Optional timeout in seconds
            
        Returns:
            Tuple of (success, message)
        """
        async with self.lock:
            # Check if component is registered
            if component_id not in self.components:
                return False, "Component not registered"
            
            return await register_readiness_condition(
                self.readiness_conditions,
                component_id,
                condition_name,
                check_func,
                description,
                timeout
            )
    
    async def check_readiness_conditions(self, component_id: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Check all readiness conditions for a component.
        
        Args:
            component_id: Component ID
            
        Returns:
            Tuple of (all_satisfied, condition_results)
        """
        async with self.lock:
            return await check_readiness_conditions(self.readiness_conditions, component_id)
    
    async def mark_component_ready(self, 
                             component_id: str, 
                             instance_uuid: str,
                             metadata: Optional[Dict[str, Any]] = None) -> Tuple[bool, str]:
        """
        Mark a component as ready after checking all readiness conditions.
        
        Args:
            component_id: Component ID
            instance_uuid: Instance UUID
            metadata: Optional additional metadata
            
        Returns:
            Tuple of (success, message)
        """
        async with self.lock:
            return await mark_component_ready(
                self.components,
                self.instances,
                self.readiness_conditions,
                component_id,
                instance_uuid,
                metadata,
                self.data_dir
            )
    
    async def wait_for_component_ready(self, 
                                  component_id: str, 
                                  timeout: float = 60.0,
                                  check_interval: float = 0.5) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Wait for a component to become ready.
        
        Args:
            component_id: Component ID to wait for
            timeout: Timeout in seconds
            check_interval: Interval between checks
            
        Returns:
            Tuple of (success, component_info)
        """
        # Initial check with lock
        async with self.lock:
            if component_id in self.components:
                state = self.components[component_id].state
                if state == ComponentState.READY.value:
                    return True, await self.get_component_info(component_id)
        
        # Periodic checking without holding lock for the entire duration
        start_time = time.time()
        while time.time() - start_time < timeout:
            # Check with lock
            async with self.lock:
                if component_id in self.components:
                    state = self.components[component_id].state
                    if state == ComponentState.READY.value:
                        return True, await self.get_component_info(component_id)
                    elif state == ComponentState.FAILED.value:
                        return False, await self.get_component_info(component_id)
            
            # Wait without holding lock
            await asyncio.sleep(check_interval)
            
            # Increase check interval with a cap
            check_interval = min(check_interval * 1.5, 5)
        
        # Final check with lock
        async with self.lock:
            return False, await self.get_component_info(component_id)
    
    async def wait_for_dependencies(self, 
                              dependencies: List[str], 
                              timeout: float = 60.0,
                              check_interval: float = 0.5) -> Tuple[bool, List[str]]:
        """
        Wait for multiple dependencies to become ready.
        
        Args:
            dependencies: List of component IDs to wait for
            timeout: Timeout in seconds
            check_interval: Interval between checks
            
        Returns:
            Tuple of (all_ready, failed_dependencies)
        """
        # Fast path for no dependencies
        if not dependencies:
            return True, []
        
        # Initial check with lock
        async with self.lock:
            components_copy = self.components.copy()
        
        # Use the copied state to minimize lock contention
        return await wait_for_dependencies(
            components_copy,
            dependencies,
            timeout,
            check_interval
        )
    
    async def process_heartbeat(self, 
                          component_id: str, 
                          instance_uuid: str, 
                          sequence: int,
                          state: Optional[str] = None,
                          metadata: Optional[Dict[str, Any]] = None) -> Tuple[bool, str]:
        """
        Process a heartbeat from a component.
        
        Args:
            component_id: Component ID
            instance_uuid: Instance UUID
            sequence: Heartbeat sequence number
            state: Optional current state
            metadata: Optional additional metadata
            
        Returns:
            Tuple of (success, message)
        """
        async with self.lock:
            # Check if component is registered
            if component_id not in self.components:
                return False, "Component not registered"
                
            # Check if instance UUID matches
            if self.components[component_id].instance_uuid != instance_uuid:
                return False, "Instance UUID mismatch"
                
            # Update last heartbeat time
            self.instances[component_id]["last_heartbeat"] = time.time()
            
            # Check and update sequence number
            last_sequence = self.instances[component_id].get("last_sequence", -1)
            
            if sequence <= last_sequence and sequence != 0:
                logger.warning(f"Out-of-order heartbeat for {component_id}: {sequence} <= {last_sequence}")
                
            self.instances[component_id]["last_sequence"] = sequence
            
            # Update state if provided
            if state and state != self.components[component_id].state:
                # Validate state transition
                current_state = self.components[component_id].state
                
                if ComponentState.validate_transition(current_state, state):
                    self.components[component_id].state = state
                    self.instances[component_id]["state"] = state
                    logger.info(f"Updated component {component_id} state from heartbeat: {current_state} -> {state}")
                else:
                    logger.warning(f"Invalid state transition in heartbeat: {current_state} -> {state}")
            
            # Update metadata if provided
            if metadata:
                self.instances[component_id].setdefault("metadata", {}).update(metadata)
                
            return True, "Heartbeat processed"
    
    async def get_component_info(self, component_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a component.
        
        Args:
            component_id: Component ID
            
        Returns:
            Component information or None if not found
        """
        async with self.lock:
            return await get_component_info(self.components, self.instances, component_id)
    
    async def get_all_components(self) -> List[Dict[str, Any]]:
        """
        Get information about all components.
        
        Returns:
            List of component information dictionaries
        """
        async with self.lock:
            result = []
            
            for component_id in self.components:
                info = await get_component_info(self.components, self.instances, component_id)
                if info:
                    result.append(info)
                    
            return result
    
    async def monitor_components(self, heartbeat_timeout: int = 30) -> None:
        """
        Monitor component health and mark failed components.
        
        Args:
            heartbeat_timeout: Timeout in seconds before marking a component as failed
        """
        while True:
            try:
                # Monitor health without holding lock for too long
                async with self.lock:
                    components_copy = self.components.copy()
                    instances_copy = self.instances.copy()
                
                # Check components
                failed = await monitor_component_health(
                    components=components_copy,
                    instances=instances_copy,
                    heartbeat_timeout=heartbeat_timeout
                )
                
                # Update core components if any failed
                if failed:
                    async with self.lock:
                        # Perform state updates with lock
                        for component_id in failed:
                            if component_id in self.components:
                                component = self.components[component_id]
                                # Only update if still active (might have changed)
                                if component.state in [ComponentState.READY.value, ComponentState.DEGRADED.value]:
                                    await self.update_component_state(
                                        component_id=component_id,
                                        instance_uuid=component.instance_uuid,
                                        state=ComponentState.FAILED.value,
                                        metadata={
                                            "error": "Missed heartbeats",
                                            "failure_reason": "heartbeat_timeout"
                                        }
                                    )
            
            except Exception as e:
                logger.error(f"Error in component monitor: {e}")
            
            # Wait before next check
            await asyncio.sleep(5)
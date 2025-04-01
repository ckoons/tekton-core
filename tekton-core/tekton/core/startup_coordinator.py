#!/usr/bin/env python3
"""
Tekton StartUpCoordinator Module

This module provides the StartUpCoordinator class to manage dependency-based
component launching and coordination.
"""

import os
import asyncio
import logging
import time
from typing import Dict, List, Any, Callable, Optional, Set

from tekton.core.startup_instructions import StartUpInstructions
from tekton.core.startup_process import StartUpProcess

logger = logging.getLogger("tekton.startup_coordinator")


class StartUpCoordinator:
    """
    Coordinates the startup of multiple Tekton components based on dependencies.
    
    This class handles dependency resolution, topological sorting, and
    orchestrated launching of components.
    """
    
    def __init__(self, startup_process: Optional[StartUpProcess] = None):
        """
        Initialize the startup coordinator.
        
        Args:
            startup_process: Optional StartUpProcess instance
        """
        self.startup_process = startup_process
        
    async def initialize(self) -> bool:
        """
        Initialize the coordinator.
        
        Returns:
            True if successful
        """
        # Create startup process if not provided
        if not self.startup_process:
            self.startup_process = StartUpProcess()
            
        # Initialize the startup process
        return await self.startup_process.initialize()
        
    async def start_component(self, 
                            component_id: str, 
                            start_func: Callable[[], Any],
                            dependencies: List[str] = None,
                            timeout: int = 30) -> bool:
        """
        Start a component with the given start function.
        
        Args:
            component_id: Component ID
            start_func: Function to start the component
            dependencies: List of component dependencies
            timeout: Timeout in seconds
            
        Returns:
            True if component started successfully
        """
        if not self.startup_process:
            await self.initialize()
            
        # Set component status to starting
        await self.startup_process.set_component_status(
            component_id=component_id,
            status="starting",
            dependencies=dependencies or []
        )
        
        # Check dependencies if provided
        if dependencies:
            missing_deps = [d for d in dependencies if d not in self.startup_process.running_components]
            if missing_deps:
                logger.warning(f"Component {component_id} has unmet dependencies: {missing_deps}")
                # Don't fail yet, dependencies might start during the timeout period
        
        # Start timeout timer
        start_time = time.time()
        
        # Wait for dependencies to be ready
        while dependencies and not all(d in self.startup_process.running_components for d in dependencies):
            if time.time() - start_time > timeout:
                await self.startup_process.set_component_status(
                    component_id=component_id,
                    status="failed",
                    error=f"Timeout waiting for dependencies: {missing_deps}"
                )
                logger.error(f"Timeout waiting for dependencies: {missing_deps}")
                return False
                
            # Wait and check again
            await asyncio.sleep(1)
            
        # Start the component
        try:
            # Call the start function
            result = start_func()
            
            # Handle async functions
            if asyncio.iscoroutine(result):
                result = await result
                
            # Update status based on result
            if result:
                await self.startup_process.set_component_status(
                    component_id=component_id,
                    status="running"
                )
                logger.info(f"Component {component_id} started successfully")
                return True
            else:
                await self.startup_process.set_component_status(
                    component_id=component_id,
                    status="failed",
                    error="Start function returned False"
                )
                logger.error(f"Component {component_id} start function returned False")
                return False
        except Exception as e:
            await self.startup_process.set_component_status(
                component_id=component_id,
                status="failed",
                error=str(e)
            )
            logger.error(f"Error starting component {component_id}: {e}")
            return False
            
    def topological_sort(self, dependency_graph: Dict[str, List[str]]) -> List[str]:
        """
        Perform a topological sort of components based on dependencies.
        
        Args:
            dependency_graph: Dictionary mapping component IDs to dependencies
            
        Returns:
            List of component IDs in topological order
        """
        # Build a set of all components
        components = set(dependency_graph.keys())
        
        # Add dependencies to the components set
        for deps in dependency_graph.values():
            components.update(deps)
            
        # Initialize results list and visited/temp visited sets
        result = []
        visited = set()
        temp_visited = set()
        
        # Define DFS function
        def dfs(component):
            if component in temp_visited:
                # Circular dependency detected
                logger.warning(f"Circular dependency detected involving {component}")
                return
                
            if component in visited:
                return
                
            temp_visited.add(component)
            
            # Visit dependencies
            for dependency in dependency_graph.get(component, []):
                dfs(dependency)
                
            temp_visited.remove(component)
            visited.add(component)
            result.append(component)
            
        # Run DFS for each component
        for component in sorted(components):
            if component not in visited:
                dfs(component)
                
        # Reverse to get topological order
        return list(reversed(result))
        
    async def start_components(self, 
                            component_map: Dict[str, Dict[str, Any]],
                            ordered: bool = True) -> Dict[str, bool]:
        """
        Start multiple components in dependency order.
        
        Args:
            component_map: Dictionary mapping component IDs to config
            ordered: Whether to start in dependency order or parallel
            
        Returns:
            Dictionary mapping component IDs to success status
        """
        if not self.startup_process:
            await self.initialize()
            
        results = {}
        
        if ordered:
            # Calculate dependency graph and topological order
            dependency_graph = {}
            for component_id, config in component_map.items():
                dependency_graph[component_id] = config.get("dependencies", [])
                
            # Start components in topological order
            start_order = self.topological_sort(dependency_graph)
            
            for component_id in start_order:
                if component_id in component_map:
                    config = component_map[component_id]
                    success = await self.start_component(
                        component_id=component_id,
                        start_func=config.get("start_func"),
                        dependencies=config.get("dependencies", []),
                        timeout=config.get("timeout", 30)
                    )
                    results[component_id] = success
        else:
            # Start components in parallel
            tasks = []
            for component_id, config in component_map.items():
                tasks.append(
                    self.start_component(
                        component_id=component_id,
                        start_func=config.get("start_func"),
                        dependencies=config.get("dependencies", []),
                        timeout=config.get("timeout", 30)
                    )
                )
                
            # Wait for all components to start
            start_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            for i, (component_id, _) in enumerate(component_map.items()):
                if isinstance(start_results[i], Exception):
                    results[component_id] = False
                    logger.error(f"Exception starting {component_id}: {start_results[i]}")
                else:
                    results[component_id] = start_results[i]
                    
        return results
        
    async def wait_for_component(self, 
                            component_id: str, 
                            timeout: int = 30,
                            check_interval: float = 0.5) -> bool:
        """
        Wait for a component to be in the running state.
        
        Args:
            component_id: Component ID to wait for
            timeout: Timeout in seconds
            check_interval: Interval between status checks
            
        Returns:
            True if component is running, False if timeout or failure
        """
        if not self.startup_process:
            await self.initialize()
            
        start_time = time.time()
        
        while True:
            # Check if component is running
            if component_id in self.startup_process.running_components:
                return True
                
            # Check if component has failed
            if component_id in self.startup_process.failed_components:
                logger.error(f"Component {component_id} failed to start")
                return False
                
            # Check if timeout has elapsed
            if time.time() - start_time > timeout:
                logger.error(f"Timeout waiting for component {component_id}")
                return False
                
            # Wait before checking again
            await asyncio.sleep(check_interval)
            
    async def handle_startup_instructions(self, 
                                    instructions: StartUpInstructions,
                                    component_map: Dict[str, Dict[str, Any]]) -> bool:
        """
        Handle startup instructions for a component.
        
        Args:
            instructions: Startup instructions
            component_map: Map of component IDs to config dictionaries
            
        Returns:
            True if handled successfully
        """
        if not self.startup_process:
            await self.initialize()
            
        component_id = instructions.component_id
        
        # Check if we have a handler for this component
        if component_id not in component_map:
            logger.warning(f"No handler for component {component_id}")
            return False
            
        config = component_map[component_id]
        
        # Handle different activation modes
        if instructions.activation_mode == "immediate":
            # Start immediately
            success = await self.start_component(
                component_id=component_id,
                start_func=config.get("start_func"),
                dependencies=instructions.dependencies,
                timeout=instructions.timeout
            )
            return success
        elif instructions.activation_mode == "trigger":
            # Store the instructions for later triggering
            trigger = instructions.activation_trigger
            if not trigger:
                logger.error(f"No activation trigger specified for {component_id}")
                return False
                
            # Subscribe to the trigger topic if using message bus
            if self.startup_process.use_message_bus and self.startup_process.message_bus:
                try:
                    # Create a handler for this specific trigger
                    async def trigger_handler(message):
                        await self.start_component(
                            component_id=component_id,
                            start_func=config.get("start_func"),
                            dependencies=instructions.dependencies,
                            timeout=instructions.timeout
                        )
                        
                    # Subscribe to the trigger topic
                    await self.startup_process.message_bus.subscribe(trigger, trigger_handler)
                    logger.info(f"Subscribed to trigger {trigger} for {component_id}")
                    return True
                except Exception as e:
                    logger.error(f"Error subscribing to trigger: {e}")
                    return False
            else:
                logger.warning(f"Message bus not available for trigger mode")
                return False
        elif instructions.activation_mode == "manual":
            # Do nothing, component will be started manually
            logger.info(f"Component {component_id} set to manual activation")
            return True
        else:
            logger.error(f"Unknown activation mode: {instructions.activation_mode}")
            return False
            
    async def listen_for_startup_instructions(self, 
                                        component_map: Dict[str, Dict[str, Any]],
                                        timeout: Optional[int] = None) -> None:
        """
        Listen for startup instructions and handle them.
        
        Args:
            component_map: Map of component IDs to config dictionaries
            timeout: Optional timeout in seconds
        """
        if not self.startup_process:
            await self.initialize()
            
        if not self.startup_process.use_message_bus or not self.startup_process.message_bus:
            logger.warning("Message bus not available for listening")
            return
            
        # Subscribe to the startup instructions topic
        try:
            async def handle_instruction_message(message):
                try:
                    instructions = StartUpInstructions.from_dict(message)
                    await self.handle_startup_instructions(instructions, component_map)
                except Exception as e:
                    logger.error(f"Error handling startup instructions: {e}")
                    
            # Subscribe to both general and specific topics
            await self.startup_process.message_bus.subscribe(
                "tekton.component.startup",
                handle_instruction_message
            )
            
            # Subscribe to specific topics for each component
            for component_id in component_map:
                topic = f"tekton.component.{component_id}.startup"
                await self.startup_process.message_bus.subscribe(
                    topic,
                    handle_instruction_message
                )
                
            logger.info(f"Listening for startup instructions for {len(component_map)} components")
            
            # Wait until timeout or forever
            if timeout:
                await asyncio.sleep(timeout)
            else:
                # Run indefinitely
                while True:
                    await asyncio.sleep(3600)  # Sleep for an hour at a time
        except Exception as e:
            logger.error(f"Error listening for startup instructions: {e}")
            
    async def resolve_dependencies(self, components: Dict[str, StartUpInstructions]) -> List[str]:
        """
        Resolve dependencies among components and determine startup order.
        
        Args:
            components: Dictionary mapping component IDs to startup instructions
            
        Returns:
            List of component IDs in dependency order
        """
        # Build dependency graph
        dependency_graph = {}
        for component_id, instructions in components.items():
            dependency_graph[component_id] = instructions.dependencies
            
        # Sort topologically
        return self.topological_sort(dependency_graph)
        
    async def synchronize_with_hermes(self) -> bool:
        """
        Synchronize component status with Hermes service registry.
        
        Returns:
            True if successful
        """
        if not self.startup_process:
            await self.initialize()
            
        if not self.startup_process.use_message_bus or not self.startup_process.service_registry:
            logger.warning("Service registry not available for synchronization")
            return False
            
        try:
            # Get all services from registry
            services = await self.startup_process.service_registry.get_all_services()
            
            # Update component status based on registry
            for service_id, service_info in services.items():
                component_id = service_info.get("metadata", {}).get("component")
                if not component_id:
                    continue
                    
                # Update component status
                await self.startup_process.set_component_status(
                    component_id=component_id,
                    status="running",
                    endpoint=service_info.get("endpoint"),
                    hostname=service_info.get("metadata", {}).get("hostname")
                )
                
            logger.info(f"Synchronized with Hermes service registry")
            return True
        except Exception as e:
            logger.error(f"Error synchronizing with Hermes: {e}")
            return False
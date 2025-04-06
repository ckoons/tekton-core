#!/usr/bin/env python3
"""
Component Health Check Module

This module provides functionality for monitoring component health 
and handling heartbeats from components.
"""

import os
import time
import logging
from typing import Dict, List, Any, Optional, Set, Tuple

from ..lifecycle import ComponentState
from ..registry import _save_registrations

logger = logging.getLogger("tekton.component_lifecycle.healthcheck")


async def monitor_component_health(
    components: Dict[str, Any],
    instances: Dict[str, Dict[str, Any]],
    heartbeat_timeout: int = 30
) -> List[str]:
    """
    Monitor component health and identify components that have missed heartbeats.
    
    Args:
        components: Component registrations
        instances: Component instances
        heartbeat_timeout: Timeout in seconds
        
    Returns:
        List of component IDs that have missed heartbeats
    """
    failed_components = []
    current_time = time.time()
    
    for component_id, instance_data in instances.items():
        # Skip components that are not in active states
        if component_id not in components:
            continue
            
        component = components[component_id]
        if not ComponentState.is_active(component.state):
            continue
            
        # Check last heartbeat
        last_heartbeat = instance_data.get("last_heartbeat", 0)
        if last_heartbeat > 0 and current_time - last_heartbeat > heartbeat_timeout:
            logger.warning(f"Component {component_id} has missed heartbeats (last: {current_time - last_heartbeat:.1f}s ago)")
            failed_components.append(component_id)
            
    return failed_components


async def process_heartbeat(
    components: Dict[str, Any],
    instances: Dict[str, Dict[str, Any]],
    component_id: str,
    instance_uuid: str,
    sequence: int,
    state: Optional[str] = None,
    health_metrics: Optional[Dict[str, float]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    reason: Optional[str] = None,
    details: Optional[str] = None,
    data_dir: Optional[str] = None
) -> Tuple[bool, str]:
    """
    Process a heartbeat from a component with enhanced health metrics.
    
    Args:
        components: Component registrations
        instances: Component instances
        component_id: Component ID
        instance_uuid: Instance UUID
        sequence: Heartbeat sequence number
        state: Optional current state
        health_metrics: Optional health metrics (CPU, memory, latency, etc.)
        metadata: Optional additional metadata
        reason: Optional reason for state change
        details: Optional details about component status
        data_dir: Optional directory for persistent storage
        
    Returns:
        Tuple of (success, message)
    """
    # Check if component is registered
    if component_id not in components:
        return False, "Component not registered"
        
    # Check if instance UUID matches
    if components[component_id].instance_uuid != instance_uuid:
        return False, "Instance UUID mismatch"
        
    # Get component registration
    component = components[component_id]
    
    # Update last heartbeat time
    instances[component_id]["last_heartbeat"] = time.time()
    
    # Check and update sequence number
    last_sequence = instances[component_id].get("last_sequence", -1)
    
    if sequence <= last_sequence and sequence != 0:
        logger.warning(f"Out-of-order heartbeat for {component_id}: {sequence} <= {last_sequence}")
        
    instances[component_id]["last_sequence"] = sequence
    
    # Update health metrics if provided
    if health_metrics:
        # Update component health metrics
        component.update_health_metrics(health_metrics)
        
        # Store in instance data
        instances[component_id].setdefault("health_metrics", {}).update(health_metrics)
        
        # Check for automatic state transition based on metrics
        if _should_degrade_from_metrics(component_id, components, health_metrics):
            if component.state == ComponentState.READY.value or component.state == ComponentState.ACTIVE.value:
                # Auto-transition to DEGRADED due to metrics
                auto_reason = "degradation.metric_threshold"
                auto_details = "Automatic transition to DEGRADED based on health metrics"
                success = component.update_state(ComponentState.DEGRADED.value, auto_reason, auto_details)
                
                if success:
                    instances[component_id]["state"] = ComponentState.DEGRADED.value
                    logger.warning(f"Auto-degraded {component_id} based on health metrics")
    
    # Update state if provided
    if state and state != component.state:
        # Use the component's state transition method
        success = component.update_state(state, reason, details)
        
        if success:
            instances[component_id]["state"] = state
            logger.info(f"Updated component {component_id} state from heartbeat: {component.state} -> {state}")
            
            # Persist state update
            if data_dir:
                await _save_registrations(components, data_dir)
        else:
            logger.warning(f"Invalid state transition in heartbeat: {component.state} -> {state}")
    
    # Update metadata if provided
    if metadata:
        component.metadata.update(metadata)
        instances[component_id].setdefault("metadata", {}).update(metadata)
        
    return True, "Heartbeat processed"


def _should_degrade_from_metrics(
    component_id: str,
    components: Dict[str, Any],
    health_metrics: Dict[str, float]
) -> bool:
    """
    Determine if a component should be degraded based on health metrics.
    
    Args:
        component_id: Component ID
        components: Component registrations
        health_metrics: Health metrics
        
    Returns:
        True if component should be degraded
    """
    # Define thresholds for auto-degradation
    thresholds = {
        "cpu_usage": 0.9,        # 90% CPU usage
        "memory_usage": 0.85,    # 85% memory usage
        "error_rate": 0.1,       # 10% error rate
        "request_latency": 2000  # 2000ms latency
    }
    
    # Get component type-specific thresholds
    component_type = components[component_id].component_type
    
    type_thresholds = {
        "compute": {"cpu_usage": 0.95, "memory_usage": 0.9},
        "database": {"cpu_usage": 0.8, "memory_usage": 0.8},
        "api": {"request_latency": 1000, "error_rate": 0.05},
        "web": {"request_latency": 3000, "error_rate": 0.15}
    }
    
    # Override default thresholds with type-specific ones
    if component_type in type_thresholds:
        for metric, value in type_thresholds[component_type].items():
            thresholds[metric] = value
    
    # Check if any threshold is exceeded
    for metric, threshold in thresholds.items():
        if metric in health_metrics and health_metrics[metric] > threshold:
            logger.info(f"Component {component_id} exceeds {metric} threshold: {health_metrics[metric]} > {threshold}")
            return True
            
    return False


async def attempt_component_recovery(
    components: Dict[str, Any],
    instances: Dict[str, Dict[str, Any]],
    component_id: str,
    max_attempts: int = 3,
    recovery_strategy: str = "restart",
    data_dir: Optional[str] = None
) -> bool:
    """
    Attempt to recover a failed or degraded component.
    
    Args:
        components: Component registrations
        instances: Component instances
        component_id: Component ID
        max_attempts: Maximum recovery attempts
        recovery_strategy: Recovery strategy (restart, reset, failover)
        data_dir: Optional directory for persistent storage
        
    Returns:
        True if recovery was successful
    """
    # Check if component is registered
    if component_id not in components:
        logger.error(f"Cannot recover unregistered component: {component_id}")
        return False
        
    component = components[component_id]
    
    # Check if component is in a state that needs recovery
    if not ComponentState.is_degraded(component.state) and component.state != ComponentState.FAILED.value:
        logger.info(f"Component {component_id} does not need recovery (state: {component.state})")
        return True
        
    # Check if exceeded max recovery attempts
    if component.recovery_attempts >= max_attempts:
        logger.warning(f"Component {component_id} exceeded maximum recovery attempts ({max_attempts})")
        return False
        
    # Record recovery attempt
    component.record_recovery_attempt(f"Recovery strategy: {recovery_strategy}")
    
    # Implement recovery strategy
    if recovery_strategy == "restart":
        # Transition to RESTARTING
        component.update_state(ComponentState.RESTARTING.value, 
                              "recovery.restart", 
                              f"Recovery attempt {component.recovery_attempts}")
                              
        # Save state change
        instances[component_id]["state"] = ComponentState.RESTARTING.value
        if data_dir:
            await _save_registrations(components, data_dir)
        
        # TODO: Implement actual restart logic here
        # This would involve sending a restart signal to the component
        # or invoking its restart handler
        
        # For now, we'll just transition to INITIALIZING as if restart was triggered
        component.update_state(ComponentState.INITIALIZING.value,
                              "recovery.restarting",
                              "Component is initializing after restart")
                              
        instances[component_id]["state"] = ComponentState.INITIALIZING.value
        if data_dir:
            await _save_registrations(components, data_dir)
            
        logger.info(f"Recovery restart initiated for component {component_id}")
        return True
        
    elif recovery_strategy == "reset":
        # Reset component state without full restart
        component.update_state(ComponentState.INITIALIZING.value,
                              "recovery.reset",
                              "Component state reset for recovery")
                              
        instances[component_id]["state"] = ComponentState.INITIALIZING.value
        if data_dir:
            await _save_registrations(components, data_dir)
            
        logger.info(f"Recovery reset performed for component {component_id}")
        return True
        
    elif recovery_strategy == "failover":
        # TODO: Implement failover logic
        logger.warning(f"Failover recovery not implemented for {component_id}")
        return False
        
    else:
        logger.error(f"Unknown recovery strategy: {recovery_strategy}")
        return False
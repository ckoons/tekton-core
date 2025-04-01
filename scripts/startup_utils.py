#!/usr/bin/env python3
"""
Startup Utilities - Utilities for Tekton component startup

This module provides utilities for Tekton component startup and coordination.
"""

import os
import logging
import asyncio
from typing import Dict, List, Any, Optional, Set, Union

# Configure logging
logger = logging.getLogger("tekton_launcher.utils")

# Import Tekton modules
try:
    from tekton.core.startup_instructions import StartUpInstructions
    from tekton.core.heartbeat_monitor import HeartbeatMonitor
except ImportError:
    logger.error("Failed to import Tekton core modules. Make sure tekton-core is properly installed.")
    raise

# Import local modules
from component_registry import create_startup_instructions
from component_starter import start_component


async def start_components_with_startup_process(components: List[str], 
                                            use_subprocess: bool = True,
                                            hermes_url: Optional[str] = None) -> Dict[str, bool]:
    """
    Start components using the StartUpProcess for coordination.
    
    Args:
        components: List of component names to start
        use_subprocess: Whether to start components in subprocesses
        hermes_url: URL of the Hermes API
        
    Returns:
        Dictionary mapping component names to startup status
    """
    results = {}
    
    # Set up heartbeat monitor for tracking component status
    monitor = HeartbeatMonitor(hermes_url=hermes_url)
    await monitor.start()
    
    # Create instructions for each component
    instructions_map = {}
    for component in components:
        instructions = await create_startup_instructions(component)
        if hermes_url:
            instructions.hermes_url = hermes_url
        instructions_map[component] = instructions
    
    # Determine dependency order
    dependency_graph = {}
    for component, instructions in instructions_map.items():
        dependency_graph[component] = set(
            dep.split(".")[0] for dep in instructions.dependencies if dep
        )
    
    # Function to find components with no dependencies
    def find_roots(graph):
        return [node for node, deps in graph.items() if not deps]
    
    # Start components in dependency order
    while dependency_graph:
        # Find components with no dependencies
        next_components = find_roots(dependency_graph)
        if not next_components:
            logger.error("Circular dependency detected in components")
            break
        
        # Start these components
        for component in next_components:
            instructions = instructions_map[component]
            result = await start_component(component, instructions, use_subprocess)
            results[component] = result
            
            # Remove from dependency graph
            del dependency_graph[component]
            
            # Remove this component from other components' dependencies
            for deps in dependency_graph.values():
                if component.lower() in deps:
                    deps.remove(component.lower())
        
        # Wait briefly between component groups
        await asyncio.sleep(2)
    
    return results


async def shutdown_handler(sig, monitor: HeartbeatMonitor):
    """
    Handle shutdown signal.
    
    Args:
        sig: Signal that triggered shutdown
        monitor: HeartbeatMonitor instance
    """
    logger.info(f"Received signal {sig.name}, shutting down")
    await monitor.stop()
    
    # Exit after a short delay
    loop = asyncio.get_event_loop()
    loop.stop()
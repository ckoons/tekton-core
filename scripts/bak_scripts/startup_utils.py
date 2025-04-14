#!/usr/bin/env python3
"""
Startup Utilities - Utilities for Tekton component startup

This module provides utilities for Tekton component startup and coordination with
enhanced dependency handling and heartbeat monitoring.
"""

import os
import json
import logging
import asyncio
import tempfile
import subprocess
import signal
from typing import Dict, List, Any, Optional, Set, Union, Callable, Tuple

# Configure logging
logger = logging.getLogger("tekton_launcher.utils")

# Import Tekton modules
try:
    from tekton.core.startup_instructions import StartUpInstructions
    from tekton.core.heartbeat import HeartbeatMonitor, ComponentHeartbeat
    from tekton.core.startup_coordinator import StartUpCoordinator
    from tekton.core.component_registration import ComponentRegistration
except ImportError:
    logger.error("Failed to import Tekton core modules. Make sure tekton-core is properly installed.")
    raise

# Import local modules
from component_registry import create_startup_instructions, get_component_dependencies
from component_starter import start_component, create_virtual_environment


# Component dependency map
DEPENDENCY_MAP = {
    "Engram": [],
    "Hermes": [],
    "Athena": ["Hermes"],
    "Sophia": ["Hermes"],
    "Prometheus": ["Athena"],
    "Synthesis": ["Prometheus"],
    "Harmonia": ["Hermes"],
    "Rhetor": ["Sophia"],
    "Telos": ["Rhetor"]
}

# Standard startup order
STANDARD_ORDER = [
    "Engram",    # Memory services first (no dependencies)
    "Hermes",    # Message bus and database services (depends on: none)
    "Athena",    # Knowledge graph (depends on: Hermes)
    "Sophia",    # Machine learning (depends on: Hermes)
    "Prometheus", # Planning (depends on: Athena)
    "Synthesis", # Execution (depends on: Prometheus)
    "Harmonia",  # Workflow (depends on: Hermes)
    "Rhetor",    # Communication (depends on: Sophia)
    "Telos",     # User interface (depends on: Rhetor)
]


class ComponentLauncher:
    """
    Manages component launching and dependency resolution for Tekton components.
    
    This class provides a centralized way to coordinate component startup, handle
    dependencies, and monitor component health.
    """
    
    def __init__(self, 
                base_dir: str = None, 
                hermes_url: str = None,
                use_direct: bool = False,
                restart_mode: bool = False):
        """
        Initialize the component launcher.
        
        Args:
            base_dir: Base directory for Tekton components
            hermes_url: URL of the Hermes API
            use_direct: Whether to start components directly (not in subprocesses)
            restart_mode: Whether to enable automatic restart of components
        """
        self.base_dir = base_dir or os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        self.hermes_url = hermes_url or os.environ.get("HERMES_URL", "http://localhost:5000/api")
        self.use_direct = use_direct
        self.restart_mode = restart_mode
        
        # Component status tracking
        self.running_components: Set[str] = set()
        self.failed_components: Set[str] = set()
        self.component_processes: Dict[str, subprocess.Popen] = {}
        
        # Monitoring
        self.coordinator = None
        self.heartbeat_monitor = None
        
        # Component event callbacks
        self.on_component_start: Optional[Callable[[str, bool], None]] = None
        self.on_component_fail: Optional[Callable[[str, str], None]] = None
        
        logger.info(f"ComponentLauncher initialized with base_dir={self.base_dir}")
    
    async def initialize(self) -> bool:
        """
        Initialize the launcher.
        
        Returns:
            True if initialization was successful
        """
        # Create startup coordinator
        self.coordinator = StartUpCoordinator()
        success = await self.coordinator.initialize()
        
        if not success:
            logger.error("Failed to initialize startup coordinator")
            return False
        
        # Create heartbeat monitor if restart mode is enabled
        if self.restart_mode:
            self.heartbeat_monitor = HeartbeatMonitor(hermes_url=self.hermes_url)
            # Start the monitor
            await self.heartbeat_monitor.start()
            
        return True
    
    def discover_components(self) -> Dict[str, Dict[str, Any]]:
        """
        Discover available Tekton components.
        
        Returns:
            Dictionary mapping component names to metadata
        """
        components = {}
        
        # Check for standard components
        for component in STANDARD_ORDER:
            component_dir = os.path.join(self.base_dir, component)
            if os.path.exists(component_dir) and os.path.isdir(component_dir):
                # Check for component directory
                if os.path.exists(os.path.join(component_dir, component.lower())):
                    # Get dependencies
                    dependencies = DEPENDENCY_MAP.get(component, [])
                    
                    components[component] = {
                        "dir": component_dir,
                        "dependencies": dependencies,
                        "has_venv": os.path.exists(os.path.join(component_dir, "venv"))
                    }
                    logger.debug(f"Discovered component: {component}")
                    
        logger.info(f"Discovered {len(components)} components")
        return components
    
    def _resolve_dependencies(self, components: List[str]) -> List[str]:
        """
        Resolve dependencies between components and return launch order.
        
        Args:
            components: List of component names
            
        Returns:
            List of component names in dependency order
        """
        # Create dependency graph
        dependency_graph = {}
        for component in components:
            dependency_graph[component] = set(DEPENDENCY_MAP.get(component, []))
        
        # Function to find components with no dependencies
        def find_roots(graph):
            return [node for node, deps in graph.items() if not deps]
        
        # Resolve in topological order
        result = []
        while dependency_graph:
            # Find components with no dependencies
            next_components = find_roots(dependency_graph)
            if not next_components:
                logger.error("Circular dependency detected in components")
                # Add remaining components in standard order
                for component in STANDARD_ORDER:
                    if component in dependency_graph and component not in result:
                        result.append(component)
                break
            
            # Sort by standard order
            next_components.sort(key=lambda c: STANDARD_ORDER.index(c) if c in STANDARD_ORDER else 999)
            
            # Add components to result
            for component in next_components:
                result.append(component)
                # Remove from dependency graph
                del dependency_graph[component]
                # Remove this component from other components' dependencies
                for deps in dependency_graph.values():
                    if component in deps:
                        deps.remove(component)
        
        return result
    
    async def prepare_component(self, component: str, component_info: Dict[str, Any]) -> bool:
        """
        Prepare a component for launch by ensuring its virtual environment exists.
        
        Args:
            component: Component name
            component_info: Component information
            
        Returns:
            True if preparation was successful
        """
        component_dir = component_info["dir"]
        
        # Check if virtual environment already exists
        if component_info.get("has_venv", False):
            logger.debug(f"Component {component} already has a virtual environment")
            return True
        
        # Create virtual environment
        logger.info(f"Creating virtual environment for {component}")
        success = await create_virtual_environment(component, component_dir)
        
        if success:
            component_info["has_venv"] = True
            logger.info(f"Virtual environment for {component} created successfully")
        else:
            logger.error(f"Failed to create virtual environment for {component}")
            
        return success
    
    async def launch_component(self, component: str, component_info: Dict[str, Any]) -> bool:
        """
        Launch a component.
        
        Args:
            component: Component name
            component_info: Component information
            
        Returns:
            True if launch was successful
        """
        # Check if component is already running
        if component in self.running_components:
            logger.info(f"Component {component} is already running")
            return True
        
        # Check if component previously failed
        if component in self.failed_components:
            logger.warning(f"Component {component} previously failed to start")
            
        # Prepare component
        if not await self.prepare_component(component, component_info):
            self.failed_components.add(component)
            if self.on_component_fail:
                self.on_component_fail(component, "Failed to prepare component")
            return False
        
        # Check if dependencies are running
        dependencies = component_info["dependencies"]
        missing_deps = [dep for dep in dependencies if dep not in self.running_components]
        if missing_deps:
            logger.warning(f"Component {component} has unmet dependencies: {missing_deps}")
            self.failed_components.add(component)
            if self.on_component_fail:
                self.on_component_fail(component, f"Unmet dependencies: {missing_deps}")
            return False
        
        # Create startup instructions
        instructions = await create_startup_instructions(component)
        if self.hermes_url:
            instructions.hermes_url = self.hermes_url
        
        # Launch component
        logger.info(f"Launching component: {component}")
        success = await start_component(component, instructions, not self.use_direct)
        
        if success:
            self.running_components.add(component)
            if component in self.failed_components:
                self.failed_components.remove(component)
            logger.info(f"Component {component} started successfully")
            if self.on_component_start:
                self.on_component_start(component, True)
                
            # Register component with heartbeat monitor if enabled
            if self.restart_mode and self.heartbeat_monitor:
                # TODO: Register component for monitoring
                pass
                
        else:
            self.failed_components.add(component)
            logger.error(f"Failed to start component {component}")
            if self.on_component_fail:
                self.on_component_fail(component, "Failed to start component")
                
        return success
    
    async def launch_components(self, components: List[str], all_components: bool = False) -> Dict[str, bool]:
        """
        Launch multiple components respecting dependencies.
        
        Args:
            components: List of component names
            all_components: Whether to launch all discovered components
            
        Returns:
            Dictionary mapping component names to success status
        """
        # Initialize
        if not self.coordinator:
            await self.initialize()
            
        # Discover available components
        discovered = self.discover_components()
        
        # Determine which components to launch
        if all_components:
            to_launch = list(discovered.keys())
        else:
            to_launch = [c for c in components if c in discovered]
            
        if not to_launch:
            logger.warning("No components to launch")
            return {}
            
        # Resolve dependencies
        launch_order = self._resolve_dependencies(to_launch)
        logger.info(f"Launch order: {', '.join(launch_order)}")
        
        # Launch components
        results = {}
        for component in launch_order:
            if component in discovered:
                success = await self.launch_component(component, discovered[component])
                results[component] = success
                
                # Delay between component launches
                await asyncio.sleep(2)
                
        return results
    
    async def setup_component_monitoring(self) -> None:
        """Set up monitoring of component health."""
        if not self.restart_mode:
            return
            
        # Ensure heartbeat monitor is initialized
        if not self.heartbeat_monitor:
            self.heartbeat_monitor = HeartbeatMonitor(hermes_url=self.hermes_url)
            await self.heartbeat_monitor.start()
            
        # Register the launcher with Hermes
        heartbeat = ComponentHeartbeat(
            component_id="tekton.launcher",
            component_name="Tekton Launcher",
            hermes_url=self.hermes_url,
            capabilities=[{
                "name": "component_management",
                "description": "Manages Tekton component lifecycle",
                "parameters": {
                    "component": "string",
                    "action": "string"
                }
            }],
            metadata={
                "running_components": list(self.running_components),
                "failed_components": list(self.failed_components)
            }
        )
        
        await heartbeat.start()
        logger.info("Component monitoring enabled")
    
    async def monitor_processes(self) -> None:
        """Monitor subprocess components and restart them if they fail."""
        if not self.restart_mode:
            return
            
        logger.info("Starting component process monitoring")
        
        try:
            while True:
                # Check each process
                for component, process in list(self.component_processes.items()):
                    if process.poll() is not None:
                        # Process has exited
                        logger.warning(f"Component {component} process exited with code {process.returncode}")
                        self.running_components.discard(component)
                        
                        # Try to restart
                        logger.info(f"Attempting to restart component: {component}")
                        discovered = self.discover_components()
                        if component in discovered:
                            await self.launch_component(component, discovered[component])
                            
                # Wait before next check
                await asyncio.sleep(10)
                
        except asyncio.CancelledError:
            logger.info("Process monitoring cancelled")
    
    async def shutdown(self) -> None:
        """Shutdown the launcher and all components."""
        logger.info("Shutting down ComponentLauncher")
        
        # Stop heartbeat monitor
        if self.heartbeat_monitor:
            await self.heartbeat_monitor.stop()
            
        # Stop component processes
        for component, process in self.component_processes.items():
            logger.info(f"Stopping component: {component}")
            try:
                # Attempt graceful shutdown
                process.terminate()
                
                # Wait briefly for termination
                for _ in range(10):
                    if process.poll() is not None:
                        break
                    await asyncio.sleep(0.5)
                    
                # Force kill if needed
                if process.poll() is None:
                    logger.warning(f"Forcing kill of component: {component}")
                    process.kill()
                    
            except Exception as e:
                logger.error(f"Error stopping component {component}: {e}")
                
        logger.info("Shutdown complete")


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
    # Create launcher
    launcher = ComponentLauncher(
        hermes_url=hermes_url,
        use_direct=not use_subprocess
    )
    
    # Launch components
    return await launcher.launch_components(components)


async def shutdown_handler(sig, monitor: Optional[HeartbeatMonitor] = None):
    """
    Handle shutdown signal.
    
    Args:
        sig: Signal that triggered shutdown
        monitor: Optional HeartbeatMonitor instance
    """
    logger.info(f"Received signal {sig.name}, shutting down")
    
    if monitor:
        await monitor.stop()
    
    # Exit after a short delay
    loop = asyncio.get_event_loop()
    loop.stop()
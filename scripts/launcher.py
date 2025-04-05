"""
Tekton enhanced component launcher implementation.

This module provides the Enhanced Component Launcher class with deadlock
avoidance and improved lifecycle management.
"""

import asyncio
import logging
import time
import uuid
from typing import Dict, List, Any, Optional, Tuple

from tekton.core.heartbeat_monitor import HeartbeatMonitor, ComponentHeartbeat
from tekton.core.lifecycle import (
    ComponentState, 
    ComponentRegistration
)
from tekton.core.dependency import DependencyResolver
from tekton.core.component_lifecycle import ComponentRegistry

from startup_utils import ComponentLauncher

logger = logging.getLogger("tekton.launcher")


# Event handlers for component status reporting
def on_component_start(component, success):
    """
    Handle component start events.
    
    Args:
        component: Component name
        success: Whether the component started successfully
    """
    if success:
        logger.info(f"✅ Component {component} started successfully")
    else:
        logger.error(f"❌ Component {component} start failed")


def on_component_fail(component, reason):
    """
    Handle component failure events.
    
    Args:
        component: Component name
        reason: Reason for failure
    """
    logger.error(f"❌ Component {component} failed: {reason}")


class EnhancedComponentLauncher(ComponentLauncher):
    """
    Enhanced component launcher with deadlock avoidance and improved lifecycle management.
    
    This class extends the base ComponentLauncher with additional features:
    - Component registration with UUID tracking
    - Message persistence for recovery
    - Dependency cycle detection and resolution
    - State transition validation
    - Timeout handling for all operations
    """
    
    def __init__(self, 
                base_dir: str = None, 
                hermes_url: str = None,
                use_direct: bool = False,
                restart_mode: bool = False,
                timeout: int = 120):
        """
        Initialize the enhanced component launcher.
        
        Args:
            base_dir: Base directory for Tekton components
            hermes_url: URL of the Hermes API
            use_direct: Whether to start components directly (not in subprocesses)
            restart_mode: Whether to enable automatic restart of components
            timeout: Default timeout for component operations (in seconds)
        """
        super().__init__(base_dir, hermes_url, use_direct, restart_mode)
        
        # Enhanced state tracking
        self.component_states: Dict[str, ComponentState] = {}
        self.component_registrations: Dict[str, ComponentRegistration] = {}
        self.component_registry = None
        self.dependency_resolver = None
        self.message_queue = None
        self.default_timeout = timeout
        
        # Instance identifier
        self.instance_id = str(uuid.uuid4())
        self.startup_time = time.time()
        
        logger.info(f"EnhancedComponentLauncher initialized with instance_id={self.instance_id}")
    
    async def initialize(self) -> bool:
        """
        Initialize the enhanced launcher.
        
        Returns:
            True if initialization was successful
        """
        # Initialize our components
        # Create component registry
        self.component_registry = ComponentRegistry()
        
        # Create dependency resolver
        self.dependency_resolver = DependencyResolver()
        
        # Add standard components and dependencies to resolver
        for component, deps in self._get_dependency_map().items():
            await self.dependency_resolver.add_component(component, deps)
        
        # Check for dependency cycles
        cycles = await self.dependency_resolver.detect_cycles()
        if cycles:
            logger.warning(f"Dependency cycles detected: {cycles}")
            logger.info("Auto-resolving dependency cycles by breaking lowest priority edges")
            await self.dependency_resolver.resolve_cycles()
        
        # Create heartbeat monitor if restart mode is enabled
        if self.restart_mode:
            self.heartbeat_monitor = HeartbeatMonitor(hermes_url=self.hermes_url)
            
            # Add callbacks for heartbeat events
            self.heartbeat_monitor.on_heartbeat_received = self._on_heartbeat_received
            self.heartbeat_monitor.on_heartbeat_missed = self._on_heartbeat_missed
                
            # Start the monitor
            await self.heartbeat_monitor.start()
            
        return True
    
    def _get_dependency_map(self) -> Dict[str, List[str]]:
        """Get the component dependency map with ordered priority."""
        # Use the dependency map from startup_utils
        from startup_utils import DEPENDENCY_MAP
        return DEPENDENCY_MAP
    
    async def _on_heartbeat_received(self, component_id: str, heartbeat: Dict[str, Any]) -> None:
        """
        Handle heartbeat received from a component.
        
        Args:
            component_id: ID of the component
            heartbeat: Heartbeat data
        """
        # Extract component name from ID
        component_name = heartbeat.get("component_name", component_id.split(".")[-1])
        
        # Update component state
        if component_name in self.component_states:
            # Update to READY if it was previously degraded or initializing
            current_state = self.component_states[component_name]
            if current_state in [ComponentState.INITIALIZING, ComponentState.DEGRADED]:
                self.component_states[component_name] = ComponentState.READY
                logger.info(f"Component {component_name} transitioned to READY state")
        else:
            # Add to running components
            self.component_states[component_name] = ComponentState.READY
            self.running_components.add(component_name)
            logger.info(f"Added component {component_name} to tracking with READY state")
    
    async def _on_heartbeat_missed(self, component_id: str, missed_count: int) -> None:
        """
        Handle missed heartbeats from a component.
        
        Args:
            component_id: ID of the component
            missed_count: Number of consecutive missed heartbeats
        """
        # Extract component name from ID
        component_parts = component_id.split(".")
        component_name = component_parts[-1]
        
        # Update component state based on missed count
        if component_name in self.component_states:
            if missed_count >= 5:
                # Consider failed after 5 missed heartbeats
                self.component_states[component_name] = ComponentState.FAILED
                logger.warning(f"Component {component_name} marked as FAILED after {missed_count} missed heartbeats")
                
                # Try to restart if in restart mode
                if self.restart_mode and component_name not in self.failed_components:
                    logger.info(f"Attempting to restart component: {component_name}")
                    self.failed_components.add(component_name)
                    self.running_components.discard(component_name)
                    
                    # Schedule restart with jitter to prevent thundering herd
                    jitter = (hash(component_name) % 10) / 10.0  # 0.0 to 0.9
                    await asyncio.sleep(5 + jitter)
                    
                    discovered = self.discover_components()
                    if component_name in discovered:
                        asyncio.create_task(self.launch_component(component_name, discovered[component_name]))
            
            elif missed_count >= 2:
                # Consider degraded after 2 missed heartbeats
                self.component_states[component_name] = ComponentState.DEGRADED
                logger.warning(f"Component {component_name} marked as DEGRADED after {missed_count} missed heartbeats")
    
    async def register_component(self, component: str, metadata: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Register a component with the registry.
        
        Args:
            component: Component name
            metadata: Component metadata
            
        Returns:
            (success, error_message) tuple
        """
            
        # Create registration with UUID
        registration = ComponentRegistration(
            component_id=component,
            component_name=component,
            component_type="component",
            metadata=metadata
        )
        
        # Register the component
        success, message = await self.component_registry.register_component(registration)
        if success:
            self.component_registrations[component] = registration
            logger.info(f"Component {component} registered with instance_id={registration.instance_uuid}")
            return True, None
        else:
            logger.error(f"Failed to register component {component}")
            return False, "Registration failed"
    
    async def prepare_component(self, component: str, component_info: Dict[str, Any]) -> bool:
        """
        Prepare a component for launch with enhanced lifecycle management.
        
        Args:
            component: Component name
            component_info: Component information
            
        Returns:
            True if preparation was successful
        """
        # Update component state
        self.component_states[component] = ComponentState.INITIALIZING
        
        # Register component
        success, error = await self.register_component(component, component_info)
        if not success:
            logger.error(f"Failed to register component {component}: {error}")
            return False
        
        # Call base implementation
        return await super().prepare_component(component, component_info)
    
    async def launch_component(self, component: str, component_info: Dict[str, Any]) -> bool:
        """
        Launch a component with enhanced lifecycle management.
        
        Args:
            component: Component name
            component_info: Component information
            
        Returns:
            True if launch was successful
        """
        # Check if dependencies are satisfied
        dependencies = component_info["dependencies"]
        
        # Check dependency satisfaction with timeout
        try:
            dependency_check = asyncio.create_task(
                self.dependency_resolver.check_dependencies_satisfied(
                    component, 
                    dependencies, 
                    [c for c in self.running_components if self.component_states.get(c) == ComponentState.READY]
                )
            )
            satisfied, missing = await asyncio.wait_for(dependency_check, timeout=5)
            
            if not satisfied:
                logger.warning(f"Component {component} has unmet dependencies: {missing}")
                
                # Add more information about why dependencies are not satisfied
                missing_details = []
                for dep in missing:
                    if dep not in self.running_components:
                        state = "not running"
                    else:
                        state = str(self.component_states.get(dep, ComponentState.UNKNOWN))
                    missing_details.append(f"{dep} ({state})")
                
                if self.on_component_fail:
                    self.on_component_fail(component, f"Unmet dependencies: {', '.join(missing_details)}")
                
                # Check if any dependencies are in FAILED state
                failed_deps = [dep for dep in dependencies if self.component_states.get(dep) == ComponentState.FAILED]
                if failed_deps:
                    logger.error(f"Dependencies {failed_deps} are in FAILED state, cannot start {component}")
                    self.failed_components.add(component)
                    self.component_states[component] = ComponentState.FAILED
                    return False
                
                # Check if any dependencies are in INITIALIZING or DEGRADED state and can be waited for
                waiting_deps = [dep for dep in dependencies if self.component_states.get(dep) in [ComponentState.INITIALIZING, ComponentState.DEGRADED]]
                if waiting_deps:
                    logger.info(f"Dependencies {waiting_deps} are starting up, will retry {component} later")
                    return False
                
                # Otherwise, dependencies are truly missing
                self.failed_components.add(component)
                return False
            
        except asyncio.TimeoutError:
            logger.error(f"Dependency check for {component} timed out")
            return False
        
        # Launch with timeout
        try:
            launch_task = asyncio.create_task(super().launch_component(component, component_info))
            success = await asyncio.wait_for(launch_task, timeout=self.default_timeout)
            
            # Update component state
            if success:
                self.component_states[component] = ComponentState.READY
            else:
                self.component_states[component] = ComponentState.FAILED
            
            return success
        except asyncio.TimeoutError:
            logger.error(f"Component {component} launch timed out after {self.default_timeout}s")
            self.component_states[component] = ComponentState.FAILED
            self.failed_components.add(component)
            if self.on_component_fail:
                self.on_component_fail(component, f"Launch timed out after {self.default_timeout}s")
            return False
    
    async def monitor_processes(self) -> None:
        """Monitor subprocess components with enhanced lifecycle tracking."""
        if not self.restart_mode:
            return
            
        logger.info("Starting enhanced component process monitoring")
        
        try:
            while True:
                # Check for orphaned components
                # Get all registered components
                all_components = await self.component_registry.get_all_components()
                orphaned = []
                for comp_info in all_components:
                    comp_id = comp_info["component_id"]
                    if (comp_id not in self.running_components and
                        time.time() - comp_info["start_time"] > 300):  # 5 minute threshold
                        orphaned.append(comp_id)
                    
                # Report orphaned components
                if orphaned:
                    logger.warning(f"Detected orphaned components: {orphaned}")
                
                # Check each process
                for component, process in list(self.component_processes.items()):
                    if process.poll() is not None:
                        # Process has exited
                        logger.warning(f"Component {component} process exited with code {process.returncode}")
                        self.running_components.discard(component)
                        
                        # Update state
                        self.component_states[component] = ComponentState.FAILED
                        
                        # Try to restart
                        logger.info(f"Attempting to restart component: {component}")
                        discovered = self.discover_components()
                        if component in discovered:
                            # Add jitter to prevent thundering herd
                            jitter = (hash(component) % 10) / 10.0  # 0.0 to 0.9
                            await asyncio.sleep(2 + jitter)
                            
                            # Launch the component
                            await self.launch_component(component, discovered[component])
                            
                # Send heartbeat with component states
                if self.heartbeat_monitor:
                    heartbeat = ComponentHeartbeat(
                        component_id="tekton.launcher",
                        component_name="Tekton Launcher",
                        hermes_url=self.hermes_url,
                        metadata={
                            "running_components": list(self.running_components),
                            "failed_components": list(self.failed_components),
                            "component_states": {comp: state.value for comp, state in self.component_states.items()},
                            "instance_id": self.instance_id
                        }
                    )
                    await heartbeat.send()
                
                # Wait before next check
                await asyncio.sleep(10)
                
        except asyncio.CancelledError:
            logger.info("Process monitoring cancelled")
    
    async def resolve_deadlocks(self) -> None:
        """
        Check for and resolve potential deadlocks in the component system.
        """
            
        logger.info("Checking for potential deadlocks...")
        
        # Check for dependency cycles
        cycles = await self.dependency_resolver.detect_cycles()
        if cycles:
            logger.warning(f"Dependency cycles detected: {cycles}")
            logger.info("Resolving dependency cycles...")
            await self.dependency_resolver.resolve_cycles()
        
        # Check for stuck components
        stuck_components = [
            comp for comp, state in self.component_states.items()
            if state == ComponentState.INITIALIZING and 
               comp in self.component_registrations and
               time.time() - self.component_registrations[comp].start_time > 120  # 2 minutes threshold
        ]
        
        if stuck_components:
            logger.warning(f"Detected stuck components: {stuck_components}")
            
            # Attempt to restart stuck components
            for comp in stuck_components:
                logger.info(f"Attempting to restart stuck component: {comp}")
                self.component_states[comp] = ComponentState.RESTARTING
                
                # Terminate existing process if it exists
                if comp in self.component_processes:
                    process = self.component_processes[comp]
                    try:
                        process.terminate()
                        await asyncio.sleep(1)
                        if process.poll() is None:
                            process.kill()
                    except Exception as e:
                        logger.error(f"Error terminating process for {comp}: {e}")
                
                # Relaunch the component
                discovered = self.discover_components()
                if comp in discovered:
                    # Create a fresh registration
                    registration = ComponentRegistration(
                        component_id=comp,
                        component_name=comp,
                        component_type="component",
                        metadata=discovered[comp]
                    )
                    self.component_registrations[comp] = registration
                    
                    # Launch the component
                    await self.launch_component(comp, discovered[comp])
    
    async def shutdown(self) -> None:
        """Shutdown the launcher and all components with graceful state transitions."""
        logger.info("Shutting down EnhancedComponentLauncher")
        
        # Update states to STOPPING
        for component in self.running_components:
            self.component_states[component] = ComponentState.STOPPING
        
        # Call base implementation
        await super().shutdown()
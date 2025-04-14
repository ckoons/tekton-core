#!/usr/bin/env python3
"""
Component Deployment Script

This script deploys and launches Tekton components in dependency order,
ensuring proper startup sequence and validation.
"""

import os
import sys
import time
import json
import asyncio
import logging
import argparse
import subprocess
from typing import Dict, List, Any, Optional, Set, Tuple

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tekton.core.lifecycle import ComponentState
from tekton.core.component_lifecycle import ComponentRegistry
from tekton.core.dependency import DependencyResolver
from tekton.core.logging_integration import get_logger, LogCategory

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Get logger
logger = get_logger("tekton.deployment")


class ComponentDeployer:
    """Handles component deployment and startup."""
    
    def __init__(self, 
                config_path: str,
                data_dir: Optional[str] = None,
                hermes_url: Optional[str] = None):
        """
        Initialize component deployer.
        
        Args:
            config_path: Path to component configuration
            data_dir: Optional data directory for component registry
            hermes_url: Optional URL of Hermes service
        """
        self.config_path = config_path
        self.data_dir = data_dir or os.path.expanduser("~/.tekton/registry")
        self.hermes_url = hermes_url
        self.registry = None
        self.config = None
        self.processes = {}
        
    async def initialize(self) -> bool:
        """
        Initialize the deployer.
        
        Returns:
            True if successful
        """
        # Create data directory
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Create component registry
        self.registry = ComponentRegistry(data_dir=self.data_dir)
        
        # Load component configuration
        try:
            with open(self.config_path) as f:
                self.config = json.load(f)
                logger.info(f"Loaded configuration with {len(self.config['components'])} components")
                return True
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            return False
            
    async def deploy_components(self) -> bool:
        """
        Deploy components in dependency order.
        
        Returns:
            True if all components were deployed successfully
        """
        if not self.config:
            logger.error("No configuration loaded")
            return False
            
        # Build dependency graph
        dependency_graph = {}
        for component in self.config["components"]:
            component_id = component["component_id"]
            dependencies = component.get("dependencies", [])
            dependency_graph[component_id] = dependencies
            
        # Resolve dependencies
        ordered_components, cycles = DependencyResolver.resolve_dependencies(dependency_graph)
        
        if cycles:
            logger.warning(f"Dependency cycles detected: {cycles}")
            
        # Start components in order
        launched_count = 0
        for component_id in ordered_components:
            # Find component config
            component_config = next((c for c in self.config["components"] if c["component_id"] == component_id), None)
            if not component_config:
                logger.warning(f"No configuration found for component {component_id}")
                continue
                
            # Launch component
            success = await self._launch_component(component_config)
            if success:
                launched_count += 1
                
                # Wait for component to be ready
                await self._wait_for_component_ready(component_id)
            else:
                logger.error(f"Failed to launch component {component_id}")
                
        logger.info(f"Deployed {launched_count}/{len(ordered_components)} components")
        return launched_count == len(ordered_components)
            
    async def _launch_component(self, component_config: Dict[str, Any]) -> bool:
        """
        Launch a component process.
        
        Args:
            component_config: Component configuration
            
        Returns:
            True if component was launched successfully
        """
        component_id = component_config["component_id"]
        launch_command = component_config.get("launch_command")
        
        if not launch_command:
            logger.error(f"No launch command specified for component {component_id}")
            return False
            
        try:
            # Launch component process
            logger.info(f"Launching component {component_id}: {launch_command}")
            
            # Set up environment variables
            env = os.environ.copy()
            env["TEKTON_COMPONENT_ID"] = component_id
            env["TEKTON_DATA_DIR"] = self.data_dir
            if self.hermes_url:
                env["HERMES_URL"] = self.hermes_url
                
            # Add component-specific environment variables
            for key, value in component_config.get("environment", {}).items():
                env[key] = str(value)
                
            # Launch process
            process = subprocess.Popen(
                launch_command,
                shell=True,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            
            # Store process
            self.processes[component_id] = process
            
            # Start log monitoring
            asyncio.create_task(self._monitor_process_logs(component_id, process))
            
            logger.info(f"Component {component_id} launched with PID {process.pid}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to launch component {component_id}: {e}")
            return False
            
    async def _monitor_process_logs(self, component_id: str, process: subprocess.Popen) -> None:
        """
        Monitor process logs.
        
        Args:
            component_id: Component ID
            process: Process to monitor
        """
        try:
            # Create log files
            stdout_file = open(f"{self.data_dir}/{component_id}.stdout.log", "w")
            stderr_file = open(f"{self.data_dir}/{component_id}.stderr.log", "w")
            
            # Monitor stdout
            while process.poll() is None:
                stdout_line = process.stdout.readline()
                if stdout_line:
                    stdout_file.write(stdout_line)
                    stdout_file.flush()
                    
                stderr_line = process.stderr.readline()
                if stderr_line:
                    stderr_file.write(stderr_line)
                    stderr_file.flush()
                    
                await asyncio.sleep(0.1)
                
            # Get remaining output
            stdout, stderr = process.communicate()
            if stdout:
                stdout_file.write(stdout)
            if stderr:
                stderr_file.write(stderr)
                
            # Close files
            stdout_file.close()
            stderr_file.close()
            
            # Log process exit
            logger.info(f"Component {component_id} process exited with code {process.returncode}")
            
        except Exception as e:
            logger.error(f"Error monitoring logs for component {component_id}: {e}")
            
    async def _wait_for_component_ready(self, component_id: str, timeout: float = 60.0) -> bool:
        """
        Wait for a component to be ready.
        
        Args:
            component_id: Component ID
            timeout: Timeout in seconds
            
        Returns:
            True if component became ready
        """
        logger.info(f"Waiting for component {component_id} to be ready (timeout: {timeout}s)")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            # Check component status
            component_info = await self.registry.get_component_info(component_id)
            if component_info:
                state = component_info.get("state")
                if state == ComponentState.READY.value:
                    logger.info(f"Component {component_id} is ready")
                    return True
                elif state == ComponentState.FAILED.value:
                    logger.error(f"Component {component_id} failed to start")
                    return False
                    
            # Wait before checking again
            await asyncio.sleep(1.0)
            
        logger.warning(f"Timeout waiting for component {component_id} to be ready")
        return False
        
    async def shutdown_components(self) -> None:
        """Shutdown all components in reverse dependency order."""
        if not self.config:
            return
            
        # Build dependency graph
        dependency_graph = {}
        for component in self.config["components"]:
            component_id = component["component_id"]
            dependencies = component.get("dependencies", [])
            dependency_graph[component_id] = dependencies
            
        # Resolve dependencies
        ordered_components, _ = DependencyResolver.resolve_dependencies(dependency_graph)
        
        # Reverse order for shutdown
        ordered_components.reverse()
        
        # Shutdown components
        for component_id in ordered_components:
            if component_id in self.processes:
                process = self.processes[component_id]
                
                # Check if process is still running
                if process.poll() is None:
                    logger.info(f"Shutting down component {component_id}")
                    
                    # Send SIGTERM to process
                    process.terminate()
                    
                    # Wait for process to exit
                    try:
                        process.wait(timeout=10)
                    except subprocess.TimeoutExpired:
                        # Force kill
                        logger.warning(f"Force killing component {component_id}")
                        process.kill()
                        
                # Remove from processes
                del self.processes[component_id]
                
    async def verify_deployment(self) -> bool:
        """
        Verify all components are running properly.
        
        Returns:
            True if all components are running properly
        """
        if not self.config:
            return False
            
        # Check all components
        all_ready = True
        for component in self.config["components"]:
            component_id = component["component_id"]
            
            # Check component status
            component_info = await self.registry.get_component_info(component_id)
            if component_info:
                state = component_info.get("state")
                if state != ComponentState.READY.value and state != ComponentState.ACTIVE.value:
                    logger.warning(f"Component {component_id} is not ready: {state}")
                    all_ready = False
            else:
                logger.warning(f"Component {component_id} not found in registry")
                all_ready = False
                
        return all_ready


async def main() -> int:
    """Main function."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Deploy Tekton components")
    parser.add_argument("--config", required=True, help="Path to component configuration")
    parser.add_argument("--data-dir", help="Data directory for component registry")
    parser.add_argument("--hermes-url", help="URL of Hermes service")
    args = parser.parse_args()
    
    # Create deployer
    deployer = ComponentDeployer(
        config_path=args.config,
        data_dir=args.data_dir,
        hermes_url=args.hermes_url
    )
    
    try:
        # Initialize deployer
        success = await deployer.initialize()
        if not success:
            return 1
            
        # Deploy components
        success = await deployer.deploy_components()
        if not success:
            logger.error("Failed to deploy all components")
            return 1
            
        # Verify deployment
        success = await deployer.verify_deployment()
        if not success:
            logger.warning("Not all components are ready")
            
        logger.info("Deployment completed")
        
        # Wait for user to press Ctrl+C
        logger.info("Press Ctrl+C to shutdown")
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Shutting down components")
        await deployer.shutdown_components()
        return 0
    except Exception as e:
        logger.exception(f"Deployment error: {e}")
        return 1
        

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.info("Deployment interrupted by user")
    except Exception as e:
        logger.exception(f"Deployment failed: {e}")
        sys.exit(1)
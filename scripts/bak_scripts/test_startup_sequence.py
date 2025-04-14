#!/usr/bin/env python3
"""
Test Startup Sequence - Validates the Tekton component startup process

This script tests the complete Tekton startup sequence, including:
1. Component dependency resolution
2. Registration with Hermes
3. Heartbeat monitoring and reconnection
4. Virtual environment isolation

Usage:
    python test_startup_sequence.py [--components COMP1,COMP2,...] [--hermes-url URL]
"""

import argparse
import asyncio
import logging
import os
import signal
import subprocess
import sys
import time
from typing import Dict, List, Optional, Set

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("startup_test")

# Add Tekton directories to Python path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TEKTON_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
sys.path.insert(0, TEKTON_DIR)
sys.path.insert(0, os.path.join(TEKTON_DIR, "tekton-core"))

try:
    from tekton.core.component_registration import StartUpInstructions, ComponentRegistration, StartUpProcess
    from tekton.core.heartbeat_monitor import HeartbeatMonitor, ComponentHeartbeat
except ImportError:
    logger.error("Failed to import Tekton core modules. Make sure tekton-core is properly installed.")
    sys.exit(1)


async def test_hermes_restart(hermes_url: str, components: List[str]) -> bool:
    """
    Test Hermes restart handling.
    
    Args:
        hermes_url: URL of the Hermes API
        components: List of components to test
        
    Returns:
        Success status
    """
    logger.info("Testing Hermes restart handling...")
    
    # Create a heartbeat monitor
    monitor = HeartbeatMonitor(hermes_url=hermes_url)
    await monitor.start()
    
    # Register test components
    registrations = {}
    for i, component in enumerate(components):
        component_id = f"test.{component.lower()}"
        component_name = f"Test {component}"
        
        # Create a registration
        registration = ComponentRegistration(
            component_id=component_id,
            component_name=component_name,
            hermes_url=hermes_url,
            capabilities=[{
                "name": "test_capability",
                "description": "Test capability",
                "parameters": {
                    "param1": "string",
                    "param2": "number"
                }
            }],
            metadata={
                "description": f"Test component for {component}",
                "version": "0.1.0",
                "test": True
            }
        )
        
        # Register with Hermes
        result = await registration.register()
        if not result:
            logger.error(f"Failed to register {component_id} with Hermes")
            continue
            
        logger.info(f"Successfully registered {component_id} with Hermes")
        registrations[component_id] = registration
        
        # Register with heartbeat monitor
        monitor.register_component(registration)
    
    if not registrations:
        logger.error("No components registered, cannot test restart handling")
        await monitor.stop()
        return False
    
    # Simulate Hermes restart by killing and restarting Hermes
    logger.info("Simulating Hermes restart...")
    
    # Find Hermes processes
    hermes_pid = None
    try:
        # Find Hermes PID
        result = subprocess.run(
            ["pgrep", "-f", "hermes.*database_manager"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            hermes_pid = result.stdout.strip()
            
            if hermes_pid:
                logger.info(f"Found Hermes process: {hermes_pid}")
                
                # Stop Hermes
                logger.info("Stopping Hermes...")
                subprocess.run(["kill", hermes_pid])
                
                # Wait for Hermes to stop
                time.sleep(2)
                
                # Restart Hermes
                logger.info("Restarting Hermes...")
                subprocess.Popen(
                    ["/bin/bash", os.path.join(TEKTON_DIR, "scripts", "tekton_launch"), 
                     "--components", "hermes", "--memory-only", "--non-interactive"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                
                # Wait for Hermes to start
                time.sleep(5)
                
                # Check if heartbeat monitor reconnected
                logger.info("Checking if heartbeat monitor reconnected...")
                
                # Wait for reconnection
                for i in range(10):
                    # Check connectivity
                    hermes_available = await monitor._check_hermes_availability()
                    if hermes_available:
                        logger.info("Hermes is available again")
                        break
                        
                    logger.info(f"Waiting for Hermes to become available (attempt {i+1}/10)...")
                    await asyncio.sleep(1)
                
                if not hermes_available:
                    logger.error("Hermes did not become available within the timeout")
                    await monitor.stop()
                    return False
                
                # Wait for reconnection
                logger.info("Waiting for components to reconnect...")
                await asyncio.sleep(10)
                
                # Verify all components reconnected
                success = True
                for component_id, registration in registrations.items():
                    # Check if registration is active
                    try:
                        response = await registration.check_registration()
                        if response:
                            logger.info(f"Component {component_id} successfully reconnected")
                        else:
                            logger.error(f"Component {component_id} failed to reconnect")
                            success = False
                    except Exception as e:
                        logger.error(f"Error checking registration for {component_id}: {e}")
                        success = False
                
                # Stop the monitor
                await monitor.stop()
                return success
            else:
                logger.error("No Hermes process found")
                await monitor.stop()
                return False
        else:
            logger.error("Failed to find Hermes process")
            await monitor.stop()
            return False
    except Exception as e:
        logger.exception(f"Error testing Hermes restart: {e}")
        await monitor.stop()
        return False


async def test_startup_sequence(components: List[str], hermes_url: Optional[str] = None) -> bool:
    """
    Test the startup sequence.
    
    Args:
        components: List of components to test
        hermes_url: URL of the Hermes API
        
    Returns:
        Success status
    """
    logger.info(f"Testing startup sequence for components: {', '.join(components)}")
    
    try:
        # Check if tekton_launcher.py exists
        launcher_path = os.path.join(SCRIPT_DIR, "tekton_launcher.py")
        if not os.path.isfile(launcher_path):
            logger.error(f"Launcher script not found: {launcher_path}")
            return False
        
        # Make the script executable
        os.chmod(launcher_path, 0o755)
        
        # Build command
        cmd = [sys.executable, launcher_path]
        cmd.extend(components)
        
        if hermes_url:
            cmd.extend(["--hermes-url", hermes_url])
        
        # Add other options
        cmd.append("--verbose")
        
        # Run the launcher
        logger.info(f"Running launcher: {' '.join(cmd)}")
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Read output until a timeout
        start_time = time.time()
        timeout = 60  # 60 seconds
        
        stdout_lines = []
        stderr_lines = []
        
        while process.poll() is None and time.time() - start_time < timeout:
            # Read output
            if process.stdout:
                line = process.stdout.readline()
                if line:
                    logger.info(f"Launcher: {line.strip()}")
                    stdout_lines.append(line)
            
            # Read errors
            if process.stderr:
                line = process.stderr.readline()
                if line:
                    logger.error(f"Launcher error: {line.strip()}")
                    stderr_lines.append(line)
            
            await asyncio.sleep(0.1)
        
        # Check if process is still running
        if process.poll() is None:
            logger.warning("Launcher is taking too long, terminating...")
            process.terminate()
            return False
        
        # Check exit code
        exit_code = process.poll()
        if exit_code != 0:
            logger.error(f"Launcher exited with code {exit_code}")
            
            # Read remaining output
            if process.stdout:
                for line in process.stdout:
                    logger.error(f"Launcher: {line.strip()}")
            
            if process.stderr:
                for line in process.stderr:
                    logger.error(f"Launcher error: {line.strip()}")
            
            return False
        
        logger.info("Launcher completed successfully")
        
        # Check for specific success messages in output
        success_count = 0
        for component in components:
            for line in stdout_lines:
                if f"SUCCESS" in line and component.lower() in line.lower():
                    logger.info(f"Found success message for {component}")
                    success_count += 1
                    break
        
        if success_count == len(components):
            logger.info("All components started successfully")
            return True
        else:
            logger.warning(f"Only {success_count}/{len(components)} components started successfully")
            return False
    
    except Exception as e:
        logger.exception(f"Error testing startup sequence: {e}")
        return False


async def test_venv_isolation() -> bool:
    """
    Test virtual environment isolation.
    
    Returns:
        Success status
    """
    logger.info("Testing virtual environment isolation...")
    
    components = ["Synthesis", "Harmonia", "Athena", "Sophia"]
    missing_venvs = []
    
    for component in components:
        venv_dir = os.path.join(TEKTON_DIR, component, "venv")
        component_dir = os.path.join(TEKTON_DIR, component)
        
        if not os.path.isdir(component_dir):
            logger.warning(f"Component directory not found: {component_dir}")
            continue
        
        if os.path.isdir(venv_dir):
            logger.info(f"Found virtual environment for {component}: {venv_dir}")
            
            # Check for Python executable
            python_exec = os.path.join(venv_dir, "bin", "python")
            if os.path.isfile(python_exec):
                logger.info(f"Found Python executable: {python_exec}")
                
                # Check if it has the required dependencies
                try:
                    # Run a script to check dependencies
                    result = subprocess.run(
                        [python_exec, "-c", "import sys; print(sys.executable); import tekton.core.component_registration"],
                        capture_output=True,
                        text=True
                    )
                    
                    if result.returncode == 0:
                        logger.info(f"Virtual environment for {component} has required dependencies")
                    else:
                        logger.warning(f"Virtual environment for {component} is missing required dependencies")
                        logger.warning(f"Error: {result.stderr}")
                        missing_venvs.append(component)
                except Exception as e:
                    logger.warning(f"Error checking dependencies for {component}: {e}")
                    missing_venvs.append(component)
            else:
                logger.warning(f"Python executable not found: {python_exec}")
                missing_venvs.append(component)
        else:
            logger.warning(f"No virtual environment found for {component}")
            missing_venvs.append(component)
    
    if missing_venvs:
        logger.warning(f"Missing or incomplete virtual environments: {', '.join(missing_venvs)}")
        return False
    else:
        logger.info("All components have proper virtual environments")
        return True


async def test_dependency_resolution() -> bool:
    """
    Test component dependency resolution.
    
    Returns:
        Success status
    """
    logger.info("Testing component dependency resolution...")
    
    # Define test dependencies
    dependencies = {
        "synthesis": ["prometheus"],
        "harmonia": ["hermes"],
        "athena": ["hermes"],
        "sophia": ["hermes"],
        "prometheus": ["athena"],
        "rhetor": ["sophia"],
        "telos": ["rhetor"]
    }
    
    # Create a StartUpProcess
    process = StartUpProcess()
    
    # Add components with their dependencies
    for component, deps in dependencies.items():
        # Create dummy instructions
        instructions = StartUpInstructions(
            component_id=f"{component}.core",
            component_type=component,
            data_directory=f"/tmp/tekton/{component}",
            dependencies=[f"{dep}.core" for dep in deps],
            register=True,
            capabilities=[],
            metadata={"version": "0.1.0"}
        )
        
        # Add to process
        process.add_component(instructions)
    
    # Resolve dependencies
    try:
        order = process.resolve_dependencies()
        logger.info(f"Dependency resolution successful: {order}")
        
        # Verify dependencies are satisfied
        component_order = [comp.split(".")[0] for comp in order]
        for i, component in enumerate(component_order):
            component_deps = dependencies.get(component, [])
            for dep in component_deps:
                # Find position of dependency
                try:
                    dep_pos = component_order.index(dep)
                    if dep_pos > i:
                        logger.error(f"Dependency violation: {component} depends on {dep}, but {dep} comes after {component}")
                        return False
                except ValueError:
                    logger.error(f"Dependency {dep} not found in resolution order")
                    return False
        
        logger.info("All dependencies are properly satisfied")
        return True
    
    except Exception as e:
        logger.exception(f"Error resolving dependencies: {e}")
        return False


async def main():
    """Main entry point."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Test Tekton Startup Sequence")
    parser.add_argument(
        "--components",
        default="Synthesis,Harmonia,Athena,Sophia",
        help="Comma-separated list of components to test"
    )
    parser.add_argument(
        "--hermes-url",
        default=os.environ.get("HERMES_URL", "http://localhost:5000/api"),
        help="URL of the Hermes API"
    )
    parser.add_argument(
        "--no-restart-test",
        action="store_true",
        help="Skip Hermes restart test"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    # Set log level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Parse components
    components = [comp.strip() for comp in args.components.split(",")]
    
    # Print test parameters
    logger.info("Tekton Startup Sequence Test")
    logger.info(f"Components: {', '.join(components)}")
    logger.info(f"Hermes URL: {args.hermes_url}")
    
    # Run tests
    results = {}
    
    # Test 1: Dependency resolution
    logger.info("\n--- Test 1: Dependency Resolution ---")
    dependency_result = await test_dependency_resolution()
    results["dependency_resolution"] = dependency_result
    
    # Test 2: Virtual environment isolation
    logger.info("\n--- Test 2: Virtual Environment Isolation ---")
    venv_result = await test_venv_isolation()
    results["venv_isolation"] = venv_result
    
    # Test 3: Startup sequence
    logger.info("\n--- Test 3: Startup Sequence ---")
    startup_result = await test_startup_sequence(components, args.hermes_url)
    results["startup_sequence"] = startup_result
    
    # Test 4: Hermes restart handling
    if not args.no_restart_test:
        logger.info("\n--- Test 4: Hermes Restart Handling ---")
        restart_result = await test_hermes_restart(args.hermes_url, components)
        results["hermes_restart"] = restart_result
    
    # Print results
    logger.info("\n=== Test Results ===")
    for test, result in results.items():
        status = "PASSED" if result else "FAILED"
        logger.info(f"{test}: {status}")
    
    # Overall status
    overall = all(results.values())
    overall_status = "PASSED" if overall else "FAILED"
    logger.info(f"\nOverall Status: {overall_status}")
    
    # Exit with appropriate code
    sys.exit(0 if overall else 1)


if __name__ == "__main__":
    # Import time module (needed for timestamp)
    import time
    
    asyncio.run(main())
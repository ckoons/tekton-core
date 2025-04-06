#!/usr/bin/env python3
"""
Tekton Launcher - Python implementation of the Tekton component launcher

This script provides a programmable way to launch and coordinate Tekton components
using the StartUpInstructions protocol and dependency-aware component lifecycle management.
Enhanced with deadlock avoidance and component lifecycle management.
"""

import argparse
import asyncio
import logging
import os
import signal
import sys
import time
import uuid
from typing import Dict, List, Any, Optional, Set, Union, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("tekton_launcher")

# Add Tekton directories to Python path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TEKTON_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
sys.path.insert(0, TEKTON_DIR)
sys.path.insert(0, os.path.join(TEKTON_DIR, "tekton-core"))

# Import Tekton modules
try:
    from tekton.core.heartbeat import HeartbeatMonitor, ComponentHeartbeat
    from tekton.core.lifecycle import (
        ComponentState, 
        ReadinessCondition, 
        ComponentRegistration,
        PersistentMessageQueue
    )
    from tekton.core.dependency import DependencyResolver
    from tekton.core.component_lifecycle import ComponentRegistry
    from tekton.core.startup_coordinator import EnhancedStartUpCoordinator as StartUpCoordinator
    USING_ENHANCED_LIFECYCLE = True
    logger.info("Using enhanced component lifecycle management")
except ImportError:
    logger.error("Failed to import Tekton core modules. Make sure tekton-core is properly installed.")
    sys.exit(1)

# Import local modules
from startup_utils import ComponentLauncher, shutdown_handler
from launcher import (
    EnhancedComponentLauncher,
    on_component_start,
    on_component_fail
)


async def main():
    """Main entry point."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Tekton Component Launcher (Python)")
    parser.add_argument(
        "components",
        nargs="*",
        help="Components to launch (can specify multiple)"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Launch all available components"
    )
    parser.add_argument(
        "--hermes-url",
        default=os.environ.get("HERMES_URL", "http://localhost:5000/api"),
        help="URL of the Hermes API"
    )
    parser.add_argument(
        "--direct",
        action="store_true",
        help="Run components directly (not in subprocesses)"
    )
    parser.add_argument(
        "--restart",
        action="store_true",
        help="Restart components if they fail or if Hermes restarts"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    parser.add_argument(
        "--base-dir",
        default=TEKTON_DIR,
        help="Base directory for Tekton components"
    )
    # Enhanced lifecycle is now the only option
    parser.add_argument(
        "--timeout",
        type=int,
        default=120,
        help="Default timeout for component operations (in seconds)"
    )
    parser.add_argument(
        "--resolve-deadlocks",
        action="store_true",
        help="Periodically check for and resolve potential deadlocks"
    )
    
    args = parser.parse_args()
    
    # Configure logging
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Set Hermes URL in environment
    os.environ["HERMES_URL"] = args.hermes_url
    
    # Set unique startup timestamp
    os.environ["TEKTON_STARTUP_TIMESTAMP"] = str(int(time.time()))
    
    # Create component launcher
    logger.info("Using enhanced component launcher with deadlock avoidance")
    launcher = EnhancedComponentLauncher(
        base_dir=args.base_dir,
        hermes_url=args.hermes_url,
        use_direct=args.direct,
        restart_mode=args.restart,
        timeout=args.timeout
    )
    
    # Initialize the launcher
    await launcher.initialize()
    
    # Set event handlers for component status reporting
    launcher.on_component_start = on_component_start
    launcher.on_component_fail = on_component_fail
    
    try:
        # Launch components
        results = await launcher.launch_components(
            components=args.components,
            all_components=args.all
        )
        
        # Report results summary
        success_count = sum(1 for result in results.values() if result)
        logger.info(f"Successfully launched {success_count}/{len(results)} components")
        
        # If restart mode is enabled, set up monitoring
        if args.restart:
            logger.info("Entering monitoring mode to handle component restarts")
            
            # Set up component monitoring
            await launcher.setup_component_monitoring()
            
            # Set up signal handlers for graceful shutdown
            loop = asyncio.get_event_loop()
            for sig in (signal.SIGINT, signal.SIGTERM):
                loop.add_signal_handler(
                    sig,
                    lambda s=sig: asyncio.create_task(shutdown_handler(s, launcher.heartbeat_monitor))
                )
            
            # Start process monitoring
            monitor_task = asyncio.create_task(launcher.monitor_processes())
            
            # If deadlock resolution is enabled, set up periodic checks
            deadlock_resolution_task = None
            if args.resolve_deadlocks and hasattr(launcher, 'resolve_deadlocks'):
                logger.info("Setting up periodic deadlock resolution")
                
                async def periodic_deadlock_resolution():
                    while True:
                        await asyncio.sleep(60)  # Check every minute
                        await launcher.resolve_deadlocks()
                
                deadlock_resolution_task = asyncio.create_task(periodic_deadlock_resolution())
            
            # Keep the script running
            try:
                # Run forever
                while True:
                    await asyncio.sleep(3600)  # Sleep for an hour
            except asyncio.CancelledError:
                # Cancel tasks
                monitor_task.cancel()
                if deadlock_resolution_task:
                    deadlock_resolution_task.cancel()
                
            # Wait for tasks to complete
            try:
                await monitor_task
                if deadlock_resolution_task:
                    await deadlock_resolution_task
            except asyncio.CancelledError:
                pass
                
        # If we're not in restart mode, just exit
        elif not args.restart:
            # If any components failed, exit with error code
            if success_count < len(results):
                sys.exit(1)
    
    finally:
        # Clean up on exit
        await launcher.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
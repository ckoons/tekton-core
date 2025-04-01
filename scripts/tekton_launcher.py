#!/usr/bin/env python3
"""
Tekton Launcher - Python implementation of the Tekton component launcher

This script provides a programmable way to launch and coordinate Tekton components
using the StartUpInstructions protocol and component_registration module.
"""

import argparse
import asyncio
import logging
import os
import signal
import sys
import time
from typing import Dict, List, Any, Optional, Set, Union

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
    from tekton.core.heartbeat_monitor import HeartbeatMonitor
except ImportError:
    logger.error("Failed to import Tekton core modules. Make sure tekton-core is properly installed.")
    sys.exit(1)

# Import local modules
from startup_utils import start_components_with_startup_process, shutdown_handler


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
        help="Restart components if Hermes restarts"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level)
    
    # Set Hermes URL in environment
    os.environ["HERMES_URL"] = args.hermes_url
    
    # Set unique startup timestamp
    os.environ["TEKTON_STARTUP_TIMESTAMP"] = str(int(time.time()))
    
    # Determine which components to launch
    components_to_launch = []
    if args.all:
        # Launch all available components
        for component in ["Synthesis", "Harmonia", "Athena", "Sophia", "Prometheus", "Rhetor", "Telos"]:
            if os.path.isdir(os.path.join(TEKTON_DIR, component)):
                components_to_launch.append(component)
    else:
        # Launch specified components
        components_to_launch = args.components
    
    if not components_to_launch:
        logger.error("No components specified. Use --all to launch all components.")
        sys.exit(1)
    
    # Launch components
    logger.info(f"Launching components: {', '.join(components_to_launch)}")
    results = await start_components_with_startup_process(
        components_to_launch, 
        use_subprocess=not args.direct,
        hermes_url=args.hermes_url
    )
    
    # Report results
    success_count = sum(1 for result in results.values() if result)
    logger.info(f"Successfully launched {success_count}/{len(results)} components")
    
    for component, result in results.items():
        status = "SUCCESS" if result else "FAILED"
        logger.info(f"{component}: {status}")
    
    # If any components failed, exit with error code
    if success_count < len(results):
        sys.exit(1)
    
    # If restart mode is enabled, keep running to monitor component health
    if args.restart:
        logger.info("Entering monitoring mode to handle component restarts")
        
        # Create monitor
        monitor = HeartbeatMonitor(hermes_url=args.hermes_url)
        await monitor.start()
        
        # Set up signal handlers for graceful shutdown
        loop = asyncio.get_event_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(
                sig,
                lambda s=sig: asyncio.create_task(shutdown_handler(s, monitor))
            )
        
        # Keep the script running
        try:
            # Run forever
            while True:
                await asyncio.sleep(3600)  # Sleep for an hour
        except asyncio.CancelledError:
            pass


if __name__ == "__main__":
    asyncio.run(main())
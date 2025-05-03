#!/usr/bin/env python3
"""
Component Launcher - A standalone script to launch Tekton components.

This script provides a reliable way to launch components without string
interpolation issues that can occur in shell scripts.
"""

import sys
import os
import importlib
import argparse
import logging
import asyncio
import subprocess
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger("component_launcher")

async def launch_with_start_server(module_path, component_dir, host, port, log_file):
    """
    Launch a component that has a start_server function.
    
    Args:
        module_path: The module path (e.g., "rhetor.api.app")
        component_dir: The component directory
        host: The host to bind to
        port: The port to use
        log_file: The log file to write to
    """
    # Set up Python path
    sys.path.insert(0, component_dir)
    
    try:
        # Import the module
        module_name = module_path
        logger.info(f"Importing module {module_name}")
        module = importlib.import_module(module_name)
        
        # Check if the module has a start_server function
        if hasattr(module, 'start_server'):
            logger.info(f"Starting server with {module_name}.start_server({host}, {port})")
            await module.start_server(host=host, port=port)
        else:
            logger.error(f"Module {module_name} does not have a start_server function")
            return 1
    except Exception as e:
        logger.error(f"Error starting server: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

def launch_with_uvicorn(module_path, component_dir, host, port, log_file):
    """
    Launch a component with uvicorn.
    
    Args:
        module_path: The module path (e.g., "rhetor.api.app")
        component_dir: The component directory
        host: The host to bind to
        port: The port to use
        log_file: The log file to write to
    """
    # Set up environment
    env = os.environ.copy()
    env['PYTHONPATH'] = f"{component_dir}:{env.get('PYTHONPATH', '')}"
    
    # Build the command
    cmd = [
        sys.executable,
        "-m",
        "uvicorn",
        f"{module_path}:app",
        "--host",
        host,
        "--port",
        str(port)
    ]
    
    logger.info(f"Launching with uvicorn: {' '.join(cmd)}")
    
    # Open log file
    with open(log_file, 'w') as log:
        # Start the process
        process = subprocess.Popen(
            cmd,
            env=env,
            stdout=log,
            stderr=log,
            close_fds=True
        )
    
    # Wait a moment and check if the process is still running
    time.sleep(2)
    if process.poll() is None:
        logger.info(f"Process started with PID {process.pid}")
        return 0
    else:
        logger.error(f"Process failed to start (exit code {process.poll()})")
        return 1

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Launch a Tekton component')
    parser.add_argument('--module', required=True, help='Module path (e.g., "rhetor.api.app")')
    parser.add_argument('--component-dir', required=True, help='Component directory')
    parser.add_argument('--host', default='127.0.0.1', help='Host to bind to')
    parser.add_argument('--port', type=int, required=True, help='Port to use')
    parser.add_argument('--log-file', required=True, help='Log file path')
    parser.add_argument('--method', choices=['start_server', 'uvicorn'], default='start_server',
                        help='Launch method to use')
    
    args = parser.parse_args()
    
    logger.info(f"Launching component {args.module} with method {args.method}")
    logger.info(f"Component directory: {args.component_dir}")
    logger.info(f"Host: {args.host}, Port: {args.port}")
    logger.info(f"Log file: {args.log_file}")
    
    if args.method == 'start_server':
        return asyncio.run(launch_with_start_server(
            args.module,
            args.component_dir,
            args.host,
            args.port,
            args.log_file
        ))
    elif args.method == 'uvicorn':
        return launch_with_uvicorn(
            args.module,
            args.component_dir,
            args.host,
            args.port,
            args.log_file
        )
    else:
        logger.error(f"Unknown method: {args.method}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
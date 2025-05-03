#!/usr/bin/env python3
"""
Simple script to directly run the Rhetor server.
"""

import sys
import os
import logging
import importlib
import asyncio

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger("run_rhetor")

async def main():
    """Main entry point for running Rhetor."""
    # Get the Tekton root directory
    tekton_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    rhetor_dir = os.path.join(tekton_dir, "Rhetor")
    
    logger.info(f"Tekton directory: {tekton_dir}")
    logger.info(f"Rhetor directory: {rhetor_dir}")
    
    # Add Rhetor to Python path
    sys.path.insert(0, rhetor_dir)
    
    try:
        # Import the Rhetor app module
        from rhetor.api.app import start_server
        
        # Start the server
        logger.info("Starting Rhetor server on port 8003")
        await start_server(host="127.0.0.1", port=8003)
        
    except Exception as e:
        logger.error(f"Error starting Rhetor: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    asyncio.run(main())
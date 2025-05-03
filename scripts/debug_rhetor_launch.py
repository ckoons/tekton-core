#!/usr/bin/env python3
"""
Debug script to identify issues with launching Rhetor.
"""

import sys
import os
import logging
import importlib

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger("debug_rhetor")

def main():
    """Main entry point for debugging Rhetor launch."""
    # Get the Tekton root directory
    tekton_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    rhetor_dir = os.path.join(tekton_dir, "Rhetor")
    
    logger.info(f"Tekton directory: {tekton_dir}")
    logger.info(f"Rhetor directory: {rhetor_dir}")
    
    # Add Rhetor to Python path
    sys.path.insert(0, rhetor_dir)
    logger.info(f"Python path: {sys.path}")
    
    try:
        # Try to import the Rhetor module
        import rhetor
        logger.info(f"Rhetor module found: {rhetor.__file__}")
        
        # Try to import the API module
        from rhetor.api import app
        logger.info(f"Rhetor app module found: {app.__file__}")
        
        # Check if the app has a start_server function
        if hasattr(app, "start_server"):
            logger.info("app.start_server found")
        else:
            logger.warning("app.start_server not found - will fall back to uvicorn")
        
        # Try to access the app object
        if hasattr(app, "app"):
            logger.info(f"app.app found: {app.app}")
        else:
            logger.error("app.app not found - cannot start via uvicorn")
            
        # Try to import and run the app
        logger.info("Attempting to start Rhetor app with uvicorn")
        module = importlib.import_module("rhetor.api.app")
        
        # Print available attributes
        logger.info(f"Available attributes: {dir(module)}")
        
        # Check the port the app is configured to run on
        if hasattr(module, "PORT"):
            logger.info(f"App configured for port: {module.PORT}")
        else:
            logger.info("No port configuration found in module")
            
        # Check the host the app is configured to run on
        if hasattr(module, "HOST"):
            logger.info(f"App configured for host: {module.HOST}")
        else:
            logger.info("No host configuration found in module")
        
        logger.info("Debug complete - Rhetor app can be imported successfully")
        
    except Exception as e:
        logger.error(f"Error importing Rhetor: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
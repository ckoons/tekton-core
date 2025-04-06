"""
Main entry point for the Hephaestus GUI.
"""
import argparse
import os
import sys
import logging
import asyncio


logger = logging.getLogger(__name__)


async def start_gui_server(host="localhost", port=8080, debug=False):
    """
    Start the Hephaestus GUI server.
    
    Args:
        host: Server host
        port: Server port
        debug: Enable debug mode
    """
    try:
        # This is a placeholder for the actual server startup
        logger.info(f"Starting Hephaestus GUI server on {host}:{port}")
        
        # In the future, this will initialize the actual web server
        # For now, just keep the event loop running
        while True:
            await asyncio.sleep(1)
            
    except Exception as e:
        logger.error(f"Error starting Hephaestus GUI: {e}")
        raise


def main():
    """Main entry point for the Hephaestus GUI."""
    parser = argparse.ArgumentParser(description="Hephaestus - Tekton GUI")
    parser.add_argument("--host", default="localhost", help="Host to bind the server to")
    parser.add_argument("--port", type=int, default=8080, help="Port to bind the server to")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    
    args = parser.parse_args()
    
    # Configure logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    logger.info("Starting Hephaestus")
    
    try:
        asyncio.run(start_gui_server(host=args.host, port=args.port, debug=args.debug))
    except KeyboardInterrupt:
        logger.info("Hephaestus GUI shutting down")
    except Exception as e:
        logger.error(f"Unhandled exception: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
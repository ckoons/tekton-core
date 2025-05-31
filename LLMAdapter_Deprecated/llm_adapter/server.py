"""
Main server module for the LLM Adapter
"""

import os
import sys
import logging
import threading
from typing import Optional

from .http_server import start_http_server
from .ws_server import start_ws_server
from .config import HOST, HTTP_PORT, WS_PORT, ANTHROPIC_API_KEY

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def setup_environment():
    """Set up the environment for the adapter"""
    # Log configuration
    logger.info(f"Starting LLM Adapter on {HOST}")
    logger.info(f"HTTP server will run on port {HTTP_PORT}")
    logger.info(f"WebSocket server will run on port {WS_PORT}")
    
    # Check if Claude API key is available
    if ANTHROPIC_API_KEY:
        logger.info("Anthropic API key is configured")
    else:
        logger.warning("No Anthropic API key found - Claude integration will be simulated")
        logger.warning("Set ANTHROPIC_API_KEY environment variable to enable Claude")

def start_servers():
    """Start both HTTP and WebSocket servers"""
    # Set up the environment
    setup_environment()
    
    # Start HTTP server in a separate thread
    http_thread = threading.Thread(target=start_http_server)
    http_thread.daemon = True
    http_thread.start()
    logger.info(f"HTTP server started on http://{HOST}:{HTTP_PORT}")
    
    # Start WebSocket server in the main thread
    logger.info(f"Starting WebSocket server on ws://{HOST}:{WS_PORT}")
    start_ws_server()

if __name__ == "__main__":
    start_servers()
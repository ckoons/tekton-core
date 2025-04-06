#!/usr/bin/env python3
"""
Test Component Integration

This script demonstrates end-to-end integration of Tekton components,
testing registration, lifecycle management, graceful degradation, and metrics.
"""

import os
import sys
import logging
import asyncio

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import from the refactored package
from test_integration import run_test

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger("tekton.test_integration")


if __name__ == "__main__":
    try:
        asyncio.run(run_test())
    except KeyboardInterrupt:
        logger.info("Test terminated by user")
    except Exception as e:
        logger.exception(f"Test failed: {e}")
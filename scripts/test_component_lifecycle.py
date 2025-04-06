#!/usr/bin/env python3
"""
Test Component Lifecycle Management

This script demonstrates the enhanced component lifecycle management features
including state transitions, health monitoring, and graceful degradation.
"""

import os
import sys
import logging
import asyncio

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import from the refactored package
from component_lifecycle_test import run_lifecycle_test

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger("tekton.test_lifecycle")


if __name__ == "__main__":
    try:
        asyncio.run(run_lifecycle_test())
    except KeyboardInterrupt:
        logger.info("Test terminated by user")
    except Exception as e:
        logger.exception(f"Test failed: {e}")
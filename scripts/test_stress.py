#!/usr/bin/env python3
"""
Component Lifecycle Stress Test

This script stress tests the component lifecycle management system under load,
simulating multiple components, failures, and high request volumes.
"""

import os
import sys
import logging
import asyncio

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import from the refactored package
from stress_test import run_stress_test

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger("tekton.stress_test")


if __name__ == "__main__":
    try:
        asyncio.run(run_stress_test())
    except KeyboardInterrupt:
        logger.info("Test terminated by user")
    except Exception as e:
        logger.exception(f"Test failed: {e}")
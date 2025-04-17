#!/usr/bin/env python3
"""
Test script to identify Engram import issues
"""

import os
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("engram_test")

# Add Engram path to Python path
engram_path = os.path.join(os.path.dirname(__file__), "Engram")
sys.path.insert(0, engram_path)

def test_import():
    """Test importing the key Engram modules"""
    try:
        logger.info("Testing import of engram.core.memory...")
        from engram.core.memory import MemoryService
        logger.info("Successfully imported MemoryService")
        
        logger.info("Testing import of engram.core.memory_manager...")
        from engram.core.memory_manager import MemoryManager
        logger.info("Successfully imported MemoryManager")
        
        logger.info("Testing import of engram.api.consolidated_server...")
        from engram.api.consolidated_server import app, main
        logger.info("Successfully imported consolidated_server")
        
        return True
    except Exception as e:
        logger.error(f"Import error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Testing Engram imports...\n")
    
    result = test_import()
    
    if result:
        print("\n✅ All imports successful - Engram component should work properly!")
    else:
        print("\n❌ Some imports failed - Engram component needs additional fixing")
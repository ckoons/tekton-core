#!/usr/bin/env python3
"""Test Rhetor MCP Bridge initialization"""

import asyncio
import logging
import sys
import os

# Add Tekton root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(name)s - %(levelname)s - %(message)s')

async def test_rhetor_bridge():
    try:
        # Import and test bridge
        from Rhetor.rhetor.core.mcp.hermes_bridge import RhetorMCPBridge
        
        # Create a mock LLM manager
        llm_manager = None  # We'll use None for testing
        
        # Create bridge
        bridge = RhetorMCPBridge(llm_manager)
        print(f"✓ Created RhetorMCPBridge")
        
        # Initialize bridge
        await bridge.initialize()
        print(f"✓ Initialized bridge")
        print(f"  - FastMCP tools loaded: {len(bridge._fastmcp_tools) if bridge._fastmcp_tools else 0}")
        
        # Check if hermes client was created
        print(f"  - Hermes client created: {bridge.hermes_client is not None}")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_rhetor_bridge())
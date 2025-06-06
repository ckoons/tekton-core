#!/usr/bin/env python3
"""
Quick test to check if Metis registration is working.
"""

import asyncio
import httpx
import time

async def test_metis_registration():
    """Test if Metis tools are registered with Hermes."""
    print("🔍 Testing Metis MCP Tool Registration")
    print("=" * 40)
    
    # Wait a moment for startup
    print("⏳ Waiting for components to start...")
    await asyncio.sleep(2)
    
    # Check Hermes tools
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8001/api/mcp/v2/tools")
            if response.status_code == 200:
                tools = response.json()
                print(f"✅ Found {len(tools)} tools in Hermes")
                
                # Look for Metis tools
                metis_tools = [t for t in tools if t.get('name', '').startswith('metis.')]
                if metis_tools:
                    print(f"✅ Found {len(metis_tools)} Metis tools:")
                    for tool in metis_tools:
                        print(f"   - {tool.get('name', 'Unknown')}: {tool.get('description', 'No description')}")
                else:
                    print("❌ No Metis tools found")
                    
                # Show all tools for debugging
                print(f"\n📋 All registered tools:")
                for tool in tools:
                    name = tool.get('name', 'Unknown')
                    desc = tool.get('description', 'No description')[:50] + ('...' if len(tool.get('description', '')) > 50 else '')
                    print(f"   - {name}: {desc}")
                    
            else:
                print(f"❌ Failed to get tools: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_metis_registration())
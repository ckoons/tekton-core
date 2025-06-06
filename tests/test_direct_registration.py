#!/usr/bin/env python3
"""
Test direct tool registration with Hermes to bypass import issues.
"""

import asyncio
import aiohttp
import json

async def test_direct_registration():
    """Test registering a tool directly with Hermes."""
    print("🔧 Testing Direct Tool Registration")
    print("=" * 40)
    
    # Test tool specification
    tool_spec = {
        "name": "metis.test_tool",
        "description": "Test tool for MCP registration",
        "schema": {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "Test message"
                }
            },
            "required": ["message"]
        },
        "endpoint": "http://localhost:8011/api/tools/test_tool/execute",
        "tags": ["test"],
        "metadata": {
            "component": "metis",
            "test": True
        }
    }
    
    print("1. Testing tool registration...")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "http://localhost:8001/api/mcp/v2/tools",
                json=tool_spec,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    tool_id = result.get("tool_id")
                    print(f"   ✅ Tool registered successfully: {tool_id}")
                    
                    # Test listing tools
                    print("2. Testing tool listing...")
                    async with session.get("http://localhost:8001/api/mcp/v2/tools") as list_resp:
                        if list_resp.status == 200:
                            tools = await list_resp.json()
                            test_tools = [t for t in tools if t.get('name', '').startswith('metis.')]
                            print(f"   ✅ Found {len(test_tools)} Metis tools in registry")
                            for tool in test_tools:
                                print(f"      - {tool.get('name')}: {tool.get('description', 'No description')}")
                        else:
                            print(f"   ❌ Failed to list tools: {list_resp.status}")
                    
                    # Clean up - unregister the test tool
                    print("3. Cleaning up...")
                    async with session.delete(f"http://localhost:8001/api/mcp/v2/tools/{tool_id}") as del_resp:
                        if del_resp.status in (200, 204):
                            print(f"   ✅ Test tool cleaned up")
                        else:
                            print(f"   ⚠️  Failed to clean up: {del_resp.status}")
                            
                else:
                    error = await resp.text()
                    print(f"   ❌ Registration failed: {resp.status} - {error}")
                    
    except Exception as e:
        print(f"   ❌ Error: {e}")

    print("\n📝 Summary:")
    print("If registration worked, the HTTP API is functional.")
    print("The issue is likely in the bridge import/initialization during startup.")

if __name__ == "__main__":
    asyncio.run(test_direct_registration())
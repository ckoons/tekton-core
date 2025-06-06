#!/usr/bin/env python3
"""
Debug script to check if Hermes bridges are working
"""

import asyncio
import httpx
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def check_component_direct_tools(component: str, port: int):
    """Check if a component has FastMCP tools directly."""
    print(f"\n🔍 Checking {component} (port {port})...")
    
    # Check health
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"http://localhost:{port}/health")
            if response.status_code == 200:
                print(f"  ✅ Health check passed")
            else:
                print(f"  ❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"  ❌ Health check error: {e}")
        return
    
    # Check FastMCP endpoints
    endpoints = [
        "/api/mcp/v2/capabilities",
        "/api/mcp/v2/tools", 
        "/api/v1/mcp/capabilities",
        "/api/v1/mcp/tools"
    ]
    
    for endpoint in endpoints:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"http://localhost:{port}{endpoint}")
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, list):
                        print(f"  ✅ {endpoint}: {len(data)} items")
                    elif isinstance(data, dict):
                        if "tools" in data:
                            print(f"  ✅ {endpoint}: {len(data['tools'])} tools")
                        elif "capabilities" in data:
                            print(f"  ✅ {endpoint}: {len(data['capabilities'])} capabilities")
                        else:
                            print(f"  ✅ {endpoint}: Response received")
                else:
                    print(f"  ❌ {endpoint}: {response.status_code}")
        except Exception as e:
            print(f"  ⚠️  {endpoint}: Not available")

async def check_hermes_registration():
    """Check what's registered with Hermes."""
    print("\n🔍 Checking Hermes registration...")
    
    # Check Hermes tools endpoint
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8001/api/mcp/v2/tools")
            if response.status_code == 200:
                tools = response.json()
                if isinstance(tools, list):
                    print(f"  ✅ Hermes has {len(tools)} tools registered")
                    # Group by component if possible
                    tool_names = [t.get("name", "Unknown") for t in tools]
                    print(f"  📋 Tools: {', '.join(tool_names[:10])}")
                    if len(tool_names) > 10:
                        print(f"     ... and {len(tool_names) - 10} more")
    except Exception as e:
        print(f"  ❌ Failed to check Hermes tools: {e}")
    
    # Try to find registered components
    endpoints = [
        "/api/v1/registrations",
        "/api/v1/components", 
        "/health"
    ]
    
    for endpoint in endpoints:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"http://localhost:8001{endpoint}")
                if response.status_code == 200:
                    print(f"  ✅ {endpoint} available")
        except:
            pass

async def main():
    """Run debug checks."""
    print("🔧 Hermes Bridge Debug Script")
    print("=" * 50)
    
    # Check Hermes first
    await check_hermes_registration()
    
    # Check each component
    components = [
        ("Metis", 8006),
        ("Prometheus", 8004),
        ("Synthesis", 8011),
        ("Telos", 8012),
        ("Athena", 8005),
        ("Budget", 8002),
        ("Engram", 8000)
    ]
    
    for name, port in components:
        await check_component_direct_tools(name, port)
    
    print("\n" + "=" * 50)
    print("📝 Debug Summary:")
    print("1. Check if components have /api/mcp/v2/* or /api/v1/mcp/* endpoints")
    print("2. Verify Hermes is receiving tool registrations")
    print("3. Look at component logs for bridge initialization errors")

if __name__ == "__main__":
    asyncio.run(main())
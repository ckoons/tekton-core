#!/usr/bin/env python3
"""
Test script to verify complete Phase 3 MCP migration - Hermes tool registration

This script tests that all migrated components properly register 
their FastMCP tools with Hermes through the new bridge implementation.
"""

import asyncio
import sys
import os
import time
import httpx
from typing import Dict, List, Any

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Component configurations - all migrated components
COMPONENTS = {
    "hermes": {"port": 8001, "name": "Hermes"},
    "athena": {"port": 8005, "name": "Athena"},
    "budget": {"port": 8002, "name": "Budget"},
    "engram": {"port": 8000, "name": "Engram"},
    "rhetor": {"port": 8003, "name": "Rhetor"},
    "sophia": {"port": 8007, "name": "Sophia"},
    "apollo": {"port": 8008, "name": "Apollo"},
    "ergon": {"port": 8009, "name": "Ergon"},
    "harmonia": {"port": 8010, "name": "Harmonia"},
    "metis": {"port": 8006, "name": "Metis"},
    "prometheus": {"port": 8004, "name": "Prometheus"},
    "synthesis": {"port": 8011, "name": "Synthesis"},
    "telos": {"port": 8012, "name": "Telos"}
}

async def check_component_health(name: str, port: int) -> bool:
    """Check if a component is healthy."""
    url = f"http://localhost:{port}/health"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=5.0)
            if response.status_code == 200:
                data = response.json()
                return data.get("status") == "healthy"
    except Exception as e:
        print(f"❌ {name} health check failed: {e}")
    return False

async def get_hermes_tools() -> Dict[str, List[str]]:
    """Get all tools registered with Hermes."""
    url = "http://localhost:8001/api/mcp/v2/tools"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=10.0)
            if response.status_code == 200:
                data = response.json()
                # Handle both list and dict response formats
                if isinstance(data, list):
                    tools = data
                else:
                    tools = data.get("tools", [])
                
                # Group tools by component
                tools_by_component = {}
                for tool in tools:
                    tool_name = tool.get("name", "")
                    # Try to extract component from tool name
                    if "." in tool_name:
                        component, name = tool_name.split(".", 1)
                        if component not in tools_by_component:
                            tools_by_component[component] = []
                        tools_by_component[component].append(name)
                    elif tool_name:
                        # Handle tools without component prefix
                        if "hermes" not in tools_by_component:
                            tools_by_component["hermes"] = []
                        tools_by_component["hermes"].append(tool_name)
                return tools_by_component
    except Exception as e:
        print(f"❌ Failed to get Hermes tools: {e}")
    return {}

async def test_tool_execution(tool_id: str, parameters: Dict[str, Any]) -> bool:
    """Test executing a tool through Hermes."""
    url = "http://localhost:8001/api/mcp/v2/process"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json={
                    "tool": tool_id,
                    "parameters": parameters
                },
                timeout=10.0
            )
            if response.status_code == 200:
                data = response.json()
                return data.get("status") == "success"
    except Exception as e:
        print(f"❌ Failed to execute tool {tool_id}: {e}")
    return False

async def main():
    """Run the complete Phase 3 migration tests."""
    print("🔍 Testing Complete Phase 3 MCP Migration - All Components")
    print("=" * 60)
    
    # Step 1: Check if all components are healthy
    print("\n1️⃣ Checking component health...")
    all_healthy = True
    healthy_components = []
    unhealthy_components = []
    
    for comp_name, comp_info in COMPONENTS.items():
        is_healthy = await check_component_health(comp_info["name"], comp_info["port"])
        status = "✅" if is_healthy else "❌"
        print(f"   {status} {comp_info['name']} (port {comp_info['port']}): {'Healthy' if is_healthy else 'Not healthy'}")
        if is_healthy:
            healthy_components.append(comp_name)
        else:
            unhealthy_components.append(comp_name)
            all_healthy = False
    
    if unhealthy_components:
        print(f"\n⚠️  {len(unhealthy_components)} components are not healthy:")
        for comp in unhealthy_components:
            print(f"   - Start {COMPONENTS[comp]['name']}: cd {COMPONENTS[comp]['name']} && ./run_{comp}.sh")
        print(f"\n✅ {len(healthy_components)} components are healthy and will be tested.")
    
    # Wait a bit for tool registration to complete
    print("\n⏳ Waiting for tool registration to complete...")
    await asyncio.sleep(3)
    
    # Step 2: Check tools registered with Hermes
    print("\n2️⃣ Checking tools registered with Hermes...")
    tools_by_component = await get_hermes_tools()
    
    # Expected minimum tools for each component (at least health_check and component_info)
    expected_min_tools = {
        "athena": 10,     # Knowledge graph tools
        "budget": 7,      # Budget management tools
        "engram": 10,     # Memory management tools
        "rhetor": 16,     # LLM service tools
        "sophia": 16,     # ML & Intelligence tools
        "apollo": 12,     # Executive coordinator tools
        "ergon": 14,      # Agent framework tools
        "harmonia": 5,    # Workflow orchestration tools
        "hermes": 2,      # Self-registration tools
        "metis": 5,       # Task management tools (AI-powered)
        "prometheus": 10, # Planning tools
        "synthesis": 16,  # Integration tools
        "telos": 10       # Requirements management tools
    }
    
    # Check each component's tools
    components_with_tools = 0
    total_tools = 0
    
    print("\n   Component Tool Registration Summary:")
    print("   " + "-" * 50)
    
    for component in healthy_components:
        if component in tools_by_component:
            registered = tools_by_component.get(component, [])
            expected = expected_min_tools.get(component, 2)
            total_tools += len(registered)
            
            if len(registered) >= expected:
                status = "✅"
                components_with_tools += 1
            else:
                status = "⚠️"
                
            print(f"   {status} {COMPONENTS[component]['name']:12} | {len(registered):3} tools registered (expected ≥{expected})")
            
            # Show some registered tools
            if registered and len(registered) > 2:
                sample_tools = [t for t in registered if t not in ["health_check", "component_info"]][:3]
                if sample_tools:
                    print(f"      Sample tools: {', '.join(sample_tools)}")
    
    print(f"\n   Total: {total_tools} tools registered across {components_with_tools} components")
    
    # Step 3: Test tool execution
    print("\n3️⃣ Testing tool execution through Hermes...")
    
    # Test health check for each healthy component
    test_results = []
    print("\n   Testing health_check tools:")
    for component in healthy_components:
        if component in tools_by_component and "health_check" in tools_by_component[component]:
            tool_id = f"{component}.health_check"
            success = await test_tool_execution(tool_id, {})
            status = "✅" if success else "❌"
            print(f"   {status} {tool_id}")
            test_results.append(success)
    
    # Test component-specific tools for a few key components
    print("\n   Testing component-specific tools:")
    
    specific_tests = [
        ("athena", "SearchEntities", {"query": "test", "limit": 5}),
        ("budget", "GetBudgetStatus", {"context_id": "test-context"}),
        ("engram", "SearchMemories", {"query": "test", "limit": 5}),
        ("metis", "decompose_task", {"task_id": "test-task", "depth": 1}),
        ("prometheus", "create_project_plan", {"project_name": "test", "description": "test"}),
        ("synthesis", "unify_data", {"sources": ["test1", "test2"]}),
        ("telos", "list_projects", {})
    ]
    
    for component, tool_name, params in specific_tests:
        if component in healthy_components and component in tools_by_component:
            if tool_name in tools_by_component[component]:
                tool_id = f"{component}.{tool_name}"
                success = await test_tool_execution(tool_id, params)
                status = "✅" if success else "❌"
                print(f"   {status} {tool_id}")
                test_results.append(success)
    
    # Summary
    print("\n" + "=" * 60)
    success_count = sum(test_results)
    total_count = len(test_results)
    
    print(f"\n📊 Test Results Summary:")
    print(f"   - Components tested: {len(healthy_components)}/{len(COMPONENTS)}")
    print(f"   - Components with tools: {components_with_tools}")
    print(f"   - Total tools registered: {total_tools}")
    print(f"   - Tool execution tests: {success_count}/{total_count} passed")
    
    if success_count == total_count and components_with_tools >= 9:  # At least 9 components migrated
        print("\n✅ Phase 3 migration is successful!")
        print("\nThe following components are now integrated with Hermes:")
        for comp in healthy_components:
            if comp in tools_by_component and len(tools_by_component[comp]) > 0:
                print(f"   - {COMPONENTS[comp]['name']}: {len(tools_by_component[comp])} tools registered")
    else:
        print(f"\n⚠️  Migration partially complete.")
        print("\nPlease check the logs of failing components for more details.")
    
    print("\n📝 Note: All components maintain their FastMCP implementation")
    print("   while also registering tools with Hermes for centralized access.")
    print("\n🔗 Access Hermes tool list at: http://localhost:8001/api/mcp/v2/tools")

if __name__ == "__main__":
    asyncio.run(main())
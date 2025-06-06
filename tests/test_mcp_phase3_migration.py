#!/usr/bin/env python3
"""
Test script to verify Phase 3 MCP migration - Hermes tool registration

This script tests that all components properly register their FastMCP tools 
with Hermes through the new bridge implementation.

Usage:
    python test_mcp_phase3_migration.py                    # Test all components
    python test_mcp_phase3_migration.py --component hermes # Test only Hermes
    python test_mcp_phase3_migration.py -c hermes,apollo   # Test Hermes and Apollo
"""

import asyncio
import sys
import os
import time
import httpx
import argparse
from typing import Dict, List, Any, Optional

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Use shared environment utilities
from shared.utils.env_config import get_component_config

config = get_component_config()

# Component configurations using proper config
COMPONENTS = {
    "hermes": {"port": config.hermes.port, "name": "Hermes"},
    "apollo": {"port": config.apollo.port, "name": "Apollo"},
    "athena": {"port": config.athena.port, "name": "Athena"},
    "budget": {"port": config.budget.port, "name": "Budget"},
    "engram": {"port": config.engram.port, "name": "Engram"},
    "ergon": {"port": config.ergon.port, "name": "Ergon"},
    "harmonia": {"port": config.harmonia.port, "name": "Harmonia"},
    "metis": {"port": config.metis.port, "name": "Metis"},
    "prometheus": {"port": config.prometheus.port, "name": "Prometheus"},
    "rhetor": {"port": config.rhetor.port, "name": "Rhetor"},
    "sophia": {"port": config.sophia.port, "name": "Sophia"},
    "synthesis": {"port": config.synthesis.port, "name": "Synthesis"},
    "telos": {"port": config.telos.port, "name": "Telos"}
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

async def get_hermes_tools() -> tuple[Dict[str, List[str]], Dict[str, str]]:
    """Get all tools registered with Hermes."""
    url = "http://localhost:8001/api/mcp/v2/tools"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=10.0)
            if response.status_code == 200:
                data = response.json()
                # Group tools by component and create name->ID mapping
                tools_by_component = {}
                name_to_id_map = {}
                
                # data is a list of tools, not a dict with "tools" key
                for tool in data:
                    tool_id = tool.get("id", "")
                    tool_name = tool.get("name", "")
                    
                    # Map full name to ID
                    name_to_id_map[tool_name] = tool_id
                    
                    # Check if tool name has component prefix (e.g., "athena.SearchEntities")
                    if "." in tool_name:
                        component, tool_name_only = tool_name.split(".", 1)
                        if component not in tools_by_component:
                            tools_by_component[component] = []
                        tools_by_component[component].append(tool_name_only)
                    else:
                        # Handle tools without component prefix
                        component = "hermes"  # Default to hermes for system tools
                        if component not in tools_by_component:
                            tools_by_component[component] = []
                        tools_by_component[component].append(tool_name)
                        
                return tools_by_component, name_to_id_map
    except Exception as e:
        print(f"❌ Failed to get Hermes tools: {e}")
    return {}, {}

async def test_tool_execution(tool_id: str, parameters: Dict[str, Any]) -> bool:
    """Test executing a tool through Hermes."""
    url = f"http://localhost:8001/api/mcp/v2/tools/{tool_id}/execute"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json={
                    "parameters": parameters,
                    "context": None
                },
                timeout=10.0
            )
            if response.status_code == 200:
                data = response.json()
                return data.get("success", False)
    except Exception as e:
        print(f"❌ Failed to execute tool {tool_id}: {e}")
    return False

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Test Phase 3 MCP migration - Hermes tool registration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python test_mcp_phase3_migration.py                    # Test all components
  python test_mcp_phase3_migration.py --component hermes # Test only Hermes
  python test_mcp_phase3_migration.py -c hermes,apollo   # Test Hermes and Apollo
  python test_mcp_phase3_migration.py -c apollo,athena,budget,engram
        """
    )
    
    parser.add_argument(
        '--component', '-c',
        type=str,
        help='Comma-separated list of components to test (default: all)',
        default=None
    )
    
    return parser.parse_args()


def filter_components(components_dict: Dict, filter_list: Optional[str]) -> Dict:
    """Filter components based on command line argument."""
    if not filter_list:
        return components_dict
        
    # Parse comma-separated list
    selected = [c.strip().lower() for c in filter_list.split(',')]
    
    # Filter components
    filtered = {}
    for comp_name, comp_info in components_dict.items():
        if comp_name.lower() in selected:
            filtered[comp_name] = comp_info
            
    if not filtered:
        print(f"❌ No valid components found in filter: {filter_list}")
        print(f"Available components: {', '.join(components_dict.keys())}")
        sys.exit(1)
        
    return filtered


async def main():
    """Run the Phase 3 migration tests."""
    args = parse_arguments()
    
    # Filter components if specified
    components_to_test = filter_components(COMPONENTS, args.component)
    
    if args.component:
        print(f"🔍 Testing Phase 3 MCP Migration - {', '.join(components_to_test.keys())}")
    else:
        print("🔍 Testing Phase 3 MCP Migration - Hermes Tool Registration")
    print("=" * 60)
    
    # Step 1: Check if selected components are healthy
    print("\n1️⃣ Checking component health...")
    all_healthy = True
    for comp_name, comp_info in components_to_test.items():
        is_healthy = await check_component_health(comp_info["name"], comp_info["port"])
        status = "✅" if is_healthy else "❌"
        print(f"   {status} {comp_info['name']} (port {comp_info['port']}): {'Healthy' if is_healthy else 'Not healthy'}")
        if not is_healthy:
            all_healthy = False
    
    if not all_healthy:
        print("\n⚠️  Not all components are healthy. Please start them first:")
        print("   - Start Hermes: cd Hermes && ./run_hermes.sh")
        print("   - Start Athena: cd Athena && ./run_athena.sh")
        print("   - Start Budget: cd Budget && ./run_budget.sh")
        print("   - Start Engram: cd Engram && ./run_engram.sh")
        return
    
    # Wait a bit for tool registration to complete
    print("\n⏳ Waiting for tool registration to complete...")
    await asyncio.sleep(3)
    
    # Step 2: Check tools registered with Hermes
    print("\n2️⃣ Checking tools registered with Hermes...")
    tools_by_component, name_to_id_map = await get_hermes_tools()
    
    # Expected tools for each component (minimum 2 per component: health_check + component_info)
    expected_tools = {
        "hermes": [
            "GetComponentStatus", "ListComponents", "QueryVectorDatabase", 
            "StoreVectorData", "PublishMessage", "CreateChannel"
        ],
        "apollo": ["health_check", "component_info"],
        "athena": [
            "health_check", "component_info",
            "SearchEntities", "GetEntityById", "GetEntityRelationships",
            "FindEntityPaths", "MergeEntities", "QueryKnowledgeGraph",
            "NaiveQuery", "LocalQuery", "GlobalQuery", "HybridQuery"
        ],
        "budget": [
            "health_check", "component_info",
            "AllocateBudget", "CheckBudget", "RecordUsage", "GetBudgetStatus",
            "GetModelRecommendations", "RouteWithBudgetAwareness", "GetUsageAnalytics"
        ],
        "engram": [
            "health_check", "component_info",
            "StoreMemory", "RecallMemory", "SearchMemories", "DeleteMemory",
            "GetMemoryStats", "StoreStructuredMemory", "GetStructuredMemory",
            "SearchStructuredMemories", "UpdateStructuredMemory", "DeleteStructuredMemory"
        ],
        "ergon": ["health_check", "component_info"],
        "harmonia": ["health_check", "component_info"],
        "metis": [
            "health_check", "component_info",
            "decompose_task", "analyze_task_complexity", "suggest_task_order",
            "generate_subtasks", "detect_dependencies"
        ],
        "prometheus": ["health_check", "component_info"],
        "rhetor": ["health_check", "component_info"],
        "sophia": ["health_check", "component_info"],
        "synthesis": ["health_check", "component_info"],
        "telos": ["health_check", "component_info"]
    }
    
    # Check each component's tools (only test filtered components)
    components_to_check = list(components_to_test.keys())
    if not args.component:
        # If no filter, include hermes
        if 'hermes' not in components_to_check:
            components_to_check.append('hermes')
    elif 'hermes' in [c.lower() for c in args.component.split(',')]:
        # If hermes explicitly requested, ensure it's included
        if 'hermes' not in components_to_check:
            components_to_check.append('hermes')
    
    for component in components_to_check:
        if component not in expected_tools:
            continue
            
        expected = expected_tools[component]
        registered = tools_by_component.get(component, [])
        print(f"\n   {component.capitalize()}:")
        print(f"   Expected: {len(expected)} tools")
        print(f"   Registered: {len(registered)} tools")
        
        # Check for missing tools
        missing = set(expected) - set(registered)
        if missing:
            print(f"   ❌ Missing tools: {', '.join(missing)}")
        else:
            print(f"   ✅ All expected tools registered")
        
        # Show all registered tools
        if registered:
            # Sort tools for consistent display
            sorted_tools = sorted(registered)
            if len(sorted_tools) <= 10:
                print(f"   Tools: {', '.join(sorted_tools)}")
            else:
                # Show first 10 tools on one line, then the rest
                print(f"   Tools: {', '.join(sorted_tools[:10])}")
                remaining = sorted_tools[10:]
                for i in range(0, len(remaining), 10):
                    chunk = remaining[i:i+10]
                    print(f"          {', '.join(chunk)}")
    
    # Step 3: Test tool execution
    print("\n3️⃣ Testing tool execution through Hermes...")
    
    # Test health check for each component (only filtered components, skip hermes for health tests)
    test_results = []
    test_components = [comp for comp in components_to_check if comp != "hermes" and comp in expected_tools]
    for component in test_components:
        if component in tools_by_component and "health_check" in tools_by_component[component]:
            tool_name = f"{component}.health_check"
            tool_id = name_to_id_map.get(tool_name)
            if tool_id:
                success = await test_tool_execution(tool_id, {})
                status = "✅" if success else "❌"
                print(f"   {status} {tool_name}: {'Success' if success else 'Failed'}")
                test_results.append(success)
            else:
                print(f"   ⚠️  {tool_name}: ID not found")
                test_results.append(False)
        else:
            print(f"   ⚠️  {component}.health_check: Not registered")
            test_results.append(False)
    
    # Test a specific tool from each component
    print("\n   Testing component-specific tools:")
    
    # Test component-specific tools (only for filtered components)
    specific_tests = {
        "athena": ("SearchEntities", {"query": "test", "limit": 5}),
        "budget": ("GetBudgetStatus", {"context_id": "test-context"}),
        "engram": ("SearchMemories", {"query": "test", "limit": 5})
    }
    
    for component, (tool_name_only, params) in specific_tests.items():
        if component not in test_components:
            continue
            
        if component in tools_by_component and tool_name_only in tools_by_component[component]:
            tool_name = f"{component}.{tool_name_only}"
            tool_id = name_to_id_map.get(tool_name)
            if tool_id:
                success = await test_tool_execution(tool_id, params)
                status = "✅" if success else "❌"
                print(f"   {status} {tool_name}: {'Success' if success else 'Failed'}")
                test_results.append(success)
            else:
                print(f"   ⚠️  {tool_name}: ID not found")
                test_results.append(False)
    
    # Summary
    print("\n" + "=" * 60)
    success_count = sum(test_results)
    total_count = len(test_results)
    
    if success_count == total_count:
        print("✅ All tests passed! Phase 3 migration is successful.")
        print("\nThe following components are now integrated with Hermes:")
        print("- Athena: FastMCP tools accessible through Hermes")
        print("- Budget: FastMCP tools accessible through Hermes")
        print("- Engram: FastMCP tools accessible through Hermes")
    else:
        print(f"⚠️  {success_count}/{total_count} tests passed.")
        print("\nPlease check the logs of failing components for more details.")
        
        # Check if this is likely an import/environment issue
        if not tools_by_component or len(tools_by_component) <= 1:
            print("\n🔍 Diagnosis: No component tools found in Hermes registry.")
            print("   This suggests the MCP bridges are not being initialized.")
            print("   Likely causes:")
            print("   - Import errors preventing bridge initialization")
            print("   - Python path not including component modules")
            print("   - Environment variables not set correctly")
            print("   - Bridge code not being executed during startup")
    
    print("\n📝 Note: The components maintain their FastMCP implementation")
    print("   while also registering tools with Hermes for centralized access.")

if __name__ == "__main__":
    asyncio.run(main())
#!/usr/bin/env python3
"""
Test script to verify MCP Installation - Hermes tool registration

This script tests that all components properly register their FastMCP tools 
with Hermes through the new bridge implementation.

Usage:
    python test_mcp_instation.py                    # Test all components
    python test_mcp_instation.py --component hermes # Test only Hermes
    python test_mcp_instation.py -c hermes,apollo   # Test Hermes and Apollo
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
        description="Test MCP Installation - Hermes tool registration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python test_mcp_instation.py                    # Test all components
  python test_mcp_instation.py --component hermes # Test only Hermes
  python test_mcp_instation.py -c hermes,apollo   # Test Hermes and Apollo
  python test_mcp_instation.py -c apollo,athena,budget,engram
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
    """Run the MCP Installation tests."""
    args = parse_arguments()
    
    # Filter components if specified
    components_to_test = filter_components(COMPONENTS, args.component)
    
    if args.component:
        print(f"🔍 Testing MCP Installation - {', '.join(components_to_test.keys())}")
    else:
        print("🔍 Testing MCP Installation - Hermes Tool Registration")
    print("=" * 60)
    
    # Step 1: Check if selected components are healthy
    print("\n1️⃣ Checking component health...")
    all_healthy = True
    unhealthy_components = []
    healthy_components = []
    
    # Always check Hermes first if not filtered
    if not args.component or 'hermes' in args.component.lower():
        hermes_healthy = await check_component_health("Hermes", 8001)
        status = "✅" if hermes_healthy else "❌"
        print(f"   {status} Hermes (port 8001): {'Healthy' if hermes_healthy else 'Not healthy'}")
        if not hermes_healthy:
            print("\n❌ Hermes is required to be running. Please start it first:")
            print("   cd Hermes && ./run_hermes.sh")
            return
    
    for comp_name, comp_info in components_to_test.items():
        if comp_name.lower() == "hermes":
            continue  # Already checked above
        is_healthy = await check_component_health(comp_info["name"], comp_info["port"])
        status = "✅" if is_healthy else "❌"
        print(f"   {status} {comp_info['name']} (port {comp_info['port']}): {'Healthy' if is_healthy else 'Not healthy'}")
        if not is_healthy:
            all_healthy = False
            unhealthy_components.append(comp_info)
        else:
            healthy_components.append(comp_info)
    
    if not all_healthy:
        print(f"\n⚠️  {len(unhealthy_components)} component(s) are not healthy:")
        for comp in unhealthy_components:
            print(f"   - Start {comp['name']}: cd {comp['name']} && ./run_{comp['name'].lower()}.sh")
        print(f"\n✅ {len(healthy_components)} component(s) are healthy and will be tested.")
        print("\n🔄 Continuing with available components...")
    else:
        print(f"\n✅ All {len(components_to_test)} components are healthy!")
    
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
            "MemoryStore", "MemoryQuery", "GetContext", "StructuredMemoryAdd",
            "StructuredMemoryGet", "StructuredMemoryUpdate", "StructuredMemoryDelete",
            "StructuredMemorySearch", "NexusProcess"
        ],
        "ergon": ["health_check", "component_info"],
        "harmonia": [
            "health_check", "component_info",
            "CreateWorkflowDefinition", "UpdateWorkflowDefinition", "DeleteWorkflowDefinition",
            "GetWorkflowDefinition", "ListWorkflowDefinitions", "ExecuteWorkflow",
            "CancelWorkflowExecution", "PauseWorkflowExecution", "ResumeWorkflowExecution",
            "GetWorkflowExecutionStatus", "ListWorkflowExecutions", "CreateTemplate",
            "InstantiateTemplate", "ListTemplates", "ListComponents",
            "GetComponentActions", "ExecuteComponentAction"
        ],
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
    
    # Check each component's tools (only test healthy components)
    # Build list of healthy component names
    healthy_component_names = [comp['name'].lower() for comp in healthy_components]
    
    # Always include Hermes if it's running (already checked above)
    if not args.component or 'hermes' in args.component.lower():
        healthy_component_names.append('hermes')
    
    components_to_check = healthy_component_names
    
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
    
    print(f"📊 Test Results: {success_count}/{total_count} tests passed")
    
    if unhealthy_components:
        print(f"\n⚠️  {len(unhealthy_components)} component(s) were skipped (not running):")
        for comp in unhealthy_components:
            print(f"   - {comp['name']} (port {comp['port']})")
    
    if healthy_components:
        print(f"\n✅ {len(healthy_components)} component(s) were tested:")
        
        # Group components by their tool registration status
        fully_integrated = []
        partially_integrated = []
        basic_only = []
        
        for comp in healthy_components:
            comp_name = comp['name'].lower()
            if comp_name in tools_by_component:
                tools = tools_by_component[comp_name]
                expected = expected_tools.get(comp_name, [])
                
                # Count FastMCP tools (exclude health_check and component_info)
                fastmcp_tools = [t for t in tools if t not in ['health_check', 'component_info']]
                
                if len(fastmcp_tools) > 0:
                    if set(expected).issubset(set(tools)):
                        fully_integrated.append((comp['name'], len(fastmcp_tools)))
                    else:
                        partially_integrated.append((comp['name'], len(fastmcp_tools)))
                else:
                    basic_only.append(comp['name'])
            else:
                basic_only.append(comp['name'])
        
        if fully_integrated:
            print("\n   🌟 Fully Integrated (FastMCP + Hermes):")
            for name, tool_count in fully_integrated:
                print(f"      - {name}: {tool_count} FastMCP tools")
        
        if partially_integrated:
            print("\n   ⚠️  Partially Integrated:")
            for name, tool_count in partially_integrated:
                print(f"      - {name}: {tool_count} FastMCP tools (some missing)")
        
        if basic_only:
            print("\n   📋 Basic Integration Only:")
            for name in basic_only:
                print(f"      - {name}: health_check, component_info only")
    
    if success_count < total_count:
        print("\n🔍 Diagnosis Tips:")
        print("   - Check component logs for FastMCP registration errors")
        print("   - Verify get_all_tools() function exists and returns tools")
        print("   - Ensure MCP bridge is initialized during startup")
        print("   - Check for import errors in tools.py files")
    
    print("\n📝 Note: Components maintain their FastMCP implementation")
    print("   while also registering tools with Hermes for centralized access.")

if __name__ == "__main__":
    asyncio.run(main())

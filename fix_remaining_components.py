#!/usr/bin/env python3
"""Fix remaining components that only show basic tools."""

import os
import re

# Components to fix and their tool names
COMPONENTS_TO_FIX = {
    "Rhetor": {
        "path": "Rhetor/rhetor/core/mcp/tools.py",
        "tools": [
            # LLM Management tools
            "get_available_models",
            "set_default_model", 
            "get_model_capabilities",
            "test_model_connection",
            "get_model_performance",
            "manage_model_rotation",
            # Prompt Engineering tools
            "create_prompt_template",
            "optimize_prompt",
            "validate_prompt_syntax",
            "get_prompt_history",
            "analyze_prompt_performance",
            "manage_prompt_library",
            # Context Management tools
            "analyze_context_usage",
            "optimize_context_window",
            "track_context_history",
            "compress_context"
        ]
    },
    "Synthesis": {
        "path": "Synthesis/synthesis/core/mcp/tools.py",
        "tools": [
            "synthesize_component_data",
            "integrate_data_streams",
            "analyze_data_patterns",
            "create_synthesis_report",
            "transform_data_format"
        ]
    },
    "Telos": {
        "path": "Telos/telos/core/mcp/tools.py", 
        "tools": [
            # Requirements Management
            "create_project",
            "get_project",
            "list_projects",
            "create_requirement",
            "get_requirement",
            "update_requirement",
            # Requirement Tracing
            "create_trace",
            "list_traces",
            # Requirement Validation
            "validate_project",
            # Prometheus Integration
            "analyze_requirements",
            "create_plan"
        ]
    }
}

def add_get_all_tools_function(file_path, tool_names, component_name):
    """Add get_all_tools function to a component's tools.py file."""
    
    # Read the file
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Check if get_all_tools already exists
    if 'def get_all_tools' in content:
        print(f"✓ {component_name} already has get_all_tools function")
        return
    
    # Build the function
    tools_code = []
    for tool in tool_names:
        tools_code.append(f"    tools.append({tool}._mcp_tool_meta.to_dict())")
    
    function_code = f'''

def get_all_tools(component_manager=None):
    """Get all {component_name} MCP tools."""
    if not fastmcp_available:
        logger.warning("FastMCP not available, returning empty tools list")
        return []
        
    tools = []
    
    # {component_name} tools
{chr(10).join(tools_code)}
    
    logger.info(f"get_all_tools returning {{len(tools)}} {component_name} MCP tools")
    return tools'''
    
    # Add to end of file
    with open(file_path, 'a') as f:
        f.write(function_code)
    
    print(f"✓ Added get_all_tools to {component_name}")

def fix_bridge_import(component_name):
    """Fix the bridge import to use process_mcp_request."""
    bridge_path = f"{component_name}/{component_name.lower()}/core/mcp/hermes_bridge.py"
    
    if not os.path.exists(bridge_path):
        print(f"✗ Bridge not found: {bridge_path}")
        return
        
    with open(bridge_path, 'r') as f:
        content = f.read()
    
    # Replace the import and usage
    if 'process_request_func' in content:
        # Fix import
        content = re.sub(
            r'from .*? import process_request_func',
            'from tekton.mcp.fastmcp.utils.requests import process_mcp_request',
            content
        )
        
        # Fix usage
        content = re.sub(
            r'response = await process_request_func\((.*?), request\)',
            f'response = await process_mcp_request(\n                component_manager=\\1,\n                request=request,\n                component_module_path="{component_name.lower()}.core.mcp.tools"\n            )',
            content,
            flags=re.DOTALL
        )
        
        with open(bridge_path, 'w') as f:
            f.write(content)
            
        print(f"✓ Fixed bridge import for {component_name}")
    else:
        print(f"✓ {component_name} bridge already fixed or doesn't use process_request_func")

# Main execution
if __name__ == "__main__":
    os.chdir("/Users/cskoons/projects/github/Tekton")
    
    for component_name, config in COMPONENTS_TO_FIX.items():
        print(f"\nFixing {component_name}...")
        
        # Add get_all_tools function
        add_get_all_tools_function(config["path"], config["tools"], component_name)
        
        # Fix bridge import
        fix_bridge_import(component_name)
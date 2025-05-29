#!/usr/bin/env python3
"""
install_tekton_mcps.py

A script to install and configure all Tekton components as MCPs for Claude.
This script automates the process of:
1. Registering each component with the MCP system
2. Configuring connection details
3. Setting up authentication if needed
4. Testing the connection to each component
"""

import os
import sys
import subprocess
import json
import logging
from pathlib import Path
import asyncio

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("tekton_mcp_installer")

# Get Tekton root directory
TEKTON_ROOT = os.environ.get("TEKTON_ROOT", os.path.dirname(os.path.abspath(__file__)))

# Component definitions - name, port, MCP path
COMPONENTS = [
    {"name": "engram", "port": 8001, "mcp_path": "/mcp", "description": "Persistent memory system"},
    {"name": "rhetor", "port": 8003, "mcp_path": "/api/mcp/v2", "description": "LLM orchestration and routing"},
    {"name": "hermes", "port": 8000, "mcp_path": "/mcp", "description": "Central message bus and registration"},
    {"name": "ergon", "port": 8002, "mcp_path": "/mcp", "description": "Agent creation and management"},
    {"name": "athena", "port": 8005, "mcp_path": "/mcp", "description": "Knowledge graph management"},
    {"name": "prometheus", "port": 8006, "mcp_path": "/mcp", "description": "Strategic planning"},
    {"name": "harmonia", "port": 8007, "mcp_path": "/mcp", "description": "Workflow orchestration"},
    {"name": "telos", "port": 8008, "mcp_path": "/mcp", "description": "Requirements tracking"},
    {"name": "synthesis", "port": 8009, "mcp_path": "/mcp", "description": "Code synthesis engine"}
]

async def check_component_availability(name: str, port: int, mcp_path: str) -> bool:
    """Check if a component's MCP endpoint is available."""
    import aiohttp
    
    url = f"http://localhost:{port}{mcp_path}/health"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=2) as response:
                if response.status == 200:
                    logger.info(f"✅ {name.capitalize()} MCP is available at {url}")
                    return True
                else:
                    logger.warning(f"⚠️ {name.capitalize()} returned status {response.status}")
                    return False
    except Exception as e:
        logger.warning(f"⚠️ {name.capitalize()} MCP not available: {str(e)}")
        return False

async def get_component_capabilities(name: str, port: int, mcp_path: str) -> dict:
    """Get capabilities of a component through its MCP endpoint."""
    import aiohttp
    
    url = f"http://localhost:{port}{mcp_path}/capabilities"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=5) as response:
                if response.status == 200:
                    data = await response.json()
                    return data
                else:
                    logger.warning(f"⚠️ Failed to get capabilities from {name}: status {response.status}")
                    return {}
    except Exception as e:
        logger.warning(f"⚠️ Error getting capabilities from {name}: {str(e)}")
        return {}

async def get_component_tools(name: str, port: int, mcp_path: str) -> list:
    """Get tools offered by a component through its MCP endpoint."""
    import aiohttp
    
    url = f"http://localhost:{port}{mcp_path}/tools"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=5) as response:
                if response.status == 200:
                    data = await response.json()
                    return data
                else:
                    logger.warning(f"⚠️ Failed to get tools from {name}: status {response.status}")
                    return []
    except Exception as e:
        logger.warning(f"⚠️ Error getting tools from {name}: {str(e)}")
        return []

def generate_config_file(components_info: list) -> str:
    """Generate a Claude-compatible MCP configuration file."""
    config = {
        "mcps": []
    }
    
    for comp in components_info:
        if comp["available"]:
            mcp_config = {
                "name": comp["name"],
                "url": f"http://localhost:{comp['port']}{comp['mcp_path']}",
                "description": comp["description"],
                "capabilities": comp["capabilities"],
                "tools": [t["name"] for t in comp["tools"]]
            }
            config["mcps"].append(mcp_config)
    
    return json.dumps(config, indent=2)

async def main():
    """Main function to install all Tekton MCPs."""
    logger.info("Starting Tekton MCP installation for Claude")
    
    # Check if components are running
    logger.info("Checking if Tekton components are running...")
    
    # Collect component information
    components_info = []
    for comp in COMPONENTS:
        name = comp["name"]
        port = comp["port"]
        mcp_path = comp["mcp_path"]
        
        logger.info(f"Checking {name.capitalize()} MCP...")
        available = await check_component_availability(name, port, mcp_path)
        
        comp_info = {
            "name": name,
            "port": port,
            "mcp_path": mcp_path,
            "description": comp["description"],
            "available": available,
            "capabilities": [],
            "tools": []
        }
        
        if available:
            # Get capabilities
            capabilities = await get_component_capabilities(name, port, mcp_path)
            comp_info["capabilities"] = capabilities
            
            # Get tools
            tools = await get_component_tools(name, port, mcp_path)
            comp_info["tools"] = tools
            
            logger.info(f"  - {name.capitalize()} offers {len(tools)} tools")
        
        components_info.append(comp_info)
    
    # Generate configuration file
    config_content = generate_config_file(components_info)
    config_path = os.path.join(TEKTON_ROOT, "tekton_mcp_config.json")
    
    with open(config_path, "w") as f:
        f.write(config_content)
    
    logger.info(f"✅ Tekton MCP configuration written to {config_path}")
    
    # Output summary
    available_count = sum(1 for comp in components_info if comp["available"])
    total_count = len(COMPONENTS)
    
    logger.info("\n" + "="*50)
    logger.info(f"Installation Summary: {available_count}/{total_count} components available")
    logger.info("="*50)
    
    if available_count == 0:
        logger.warning("⚠️ No components are available. Did you start Tekton?")
        logger.info("Start Tekton with: ./scripts/tekton-launch")
    elif available_count < total_count:
        logger.info("Some components are not available. Start them with:")
        logger.info("./scripts/tekton-launch --components all")
    else:
        logger.info("🎉 All components are available and configured for Claude!")
    
    logger.info("\nTo use with Claude, add this configuration file to Claude's MCP settings.")
    logger.info("The configuration includes all available Tekton components and their tools.")

if __name__ == "__main__":
    asyncio.run(main())
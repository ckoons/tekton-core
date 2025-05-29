#!/usr/bin/env python3
"""
Install Tekton components as MCP servers for Claude Desktop.

This script configures Claude Desktop to use Tekton components as MCP servers,
allowing Claude to directly access Engram memory, Hermes messaging, and other services.
"""

import json
import os
import sys
from pathlib import Path
import argparse

# Claude Desktop config location
CLAUDE_CONFIG_PATH = Path.home() / ".config" / "claude" / "claude_desktop_config.json"

# Tekton component MCP configurations
TEKTON_MCP_SERVERS = {
    "engram": {
        "command": "python",
        "args": ["-m", "engram.api.fastmcp_server"],
        "description": "Engram memory system - store(), recall(), context()",
        "env": {
            "ENGRAM_MODE": "mcp",
            "ENGRAM_PORT": "8000"
        }
    },
    "hermes": {
        "command": "python", 
        "args": ["-m", "hermes.api.mcp_server"],
        "description": "Hermes messaging and service registry",
        "env": {
            "HERMES_PORT": "8001"
        }
    },
    "athena": {
        "command": "python",
        "args": ["-m", "athena.api.mcp_server"],
        "description": "Athena knowledge graph",
        "env": {
            "ATHENA_PORT": "8005"
        }
    },
    "prometheus": {
        "command": "python",
        "args": ["-m", "prometheus.api.mcp_server"],
        "description": "Prometheus planning system",
        "env": {
            "PROMETHEUS_PORT": "8006"
        }
    }
}


def load_claude_config():
    """Load existing Claude Desktop configuration."""
    if not CLAUDE_CONFIG_PATH.exists():
        print(f"Claude config not found at {CLAUDE_CONFIG_PATH}")
        print("Creating new configuration...")
        CLAUDE_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        return {"mcpServers": {}}
    
    try:
        with open(CLAUDE_CONFIG_PATH, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        print("Warning: Existing config is invalid JSON. Creating new configuration...")
        return {"mcpServers": {}}


def save_claude_config(config):
    """Save Claude Desktop configuration."""
    with open(CLAUDE_CONFIG_PATH, 'w') as f:
        json.dump(config, f, indent=2)
    print(f"Configuration saved to {CLAUDE_CONFIG_PATH}")


def install_component(config, component_name, component_config):
    """Install a single Tekton component as MCP server."""
    if "mcpServers" not in config:
        config["mcpServers"] = {}
    
    # Check if already installed
    if component_name in config["mcpServers"]:
        print(f"⚠️  {component_name} already configured. Updating...")
    
    # Add Tekton base path to environment
    tekton_path = str(Path(__file__).parent.parent)
    if "env" not in component_config:
        component_config["env"] = {}
    component_config["env"]["PYTHONPATH"] = tekton_path
    
    # Install the component
    config["mcpServers"][component_name] = component_config
    print(f"✅ Installed {component_name}: {component_config['description']}")


def main():
    parser = argparse.ArgumentParser(description="Install Tekton components as MCP servers")
    parser.add_argument("components", nargs="*", 
                       help="Components to install (default: all)")
    parser.add_argument("--list", action="store_true",
                       help="List available components")
    parser.add_argument("--remove", action="store_true",
                       help="Remove components instead of installing")
    
    args = parser.parse_args()
    
    # List components
    if args.list:
        print("Available Tekton MCP components:")
        for name, config in TEKTON_MCP_SERVERS.items():
            print(f"  {name}: {config['description']}")
        return
    
    # Load configuration
    config = load_claude_config()
    
    # Determine which components to process
    if args.components:
        components = args.components
    else:
        components = ["engram"]  # Default to just Engram for safety
    
    # Process components
    for component in components:
        if component not in TEKTON_MCP_SERVERS:
            print(f"❌ Unknown component: {component}")
            continue
        
        if args.remove:
            if component in config.get("mcpServers", {}):
                del config["mcpServers"][component]
                print(f"🗑️  Removed {component}")
            else:
                print(f"⚠️  {component} not installed")
        else:
            install_component(config, component, TEKTON_MCP_SERVERS[component])
    
    # Save configuration
    save_claude_config(config)
    
    print("\n📝 Next steps:")
    print("1. Restart Claude Desktop for changes to take effect")
    print("2. Use claudemem_mcp to start a session with Engram enabled")
    print("3. Claude will have direct access to memory tools")


if __name__ == "__main__":
    main()
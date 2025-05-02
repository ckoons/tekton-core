#!/usr/bin/env python3
"""
Tekton Configuration CLI

This utility provides a bridge between bash scripts and Python configuration
for Tekton components. It allows loading and accessing configuration from
both environment variables and configuration files.

Usage:
  tekton-config-cli.py get <key> [<default>]
  tekton-config-cli.py set <key> <value>
  tekton-config-cli.py list
  tekton-config-cli.py get-port <component>
  tekton-config-cli.py generate-env [--format=<format>]

Options:
  --format=<format>  Output format for environment variables [default: export]
                     Valid formats: export, docker, dotenv
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, Any, Optional, List, Union

# Configuration file paths
HOME_DIR = os.path.expanduser("~")
TEKTON_DIR = os.environ.get("TEKTON_DIR", "")
GLOBAL_CONFIG = os.path.join(HOME_DIR, ".tekton", "config.json")
LOCAL_CONFIG = os.path.join(TEKTON_DIR, "config", "config.json") if TEKTON_DIR else ""

# Component ports - must match tekton-ports.sh
COMPONENT_PORTS = {
    "hephaestus": 8080,
    "engram": 8000,
    "hermes": 8001,
    "ergon": 8002,
    "rhetor": 8003,
    "terma": 8004,
    "athena": 8005,
    "prometheus": 8006,
    "harmonia": 8007,
    "telos": 8008,
    "synthesis": 8009,
    "core": 8010,
    "tekton-core": 8010,
    "llm-adapter": 8300,
    "llm_adapter": 8300,
    "llmadapter": 8300,
}


def load_config() -> Dict[str, Any]:
    """Load configuration from files and environment variables."""
    config = {}
    
    # Load global config
    if os.path.exists(GLOBAL_CONFIG):
        try:
            with open(GLOBAL_CONFIG, 'r') as f:
                config.update(json.load(f))
        except (json.JSONDecodeError, OSError) as e:
            print(f"Warning: Failed to load global config: {e}", file=sys.stderr)
    
    # Load local config if available
    if LOCAL_CONFIG and os.path.exists(LOCAL_CONFIG):
        try:
            with open(LOCAL_CONFIG, 'r') as f:
                config.update(json.load(f))
        except (json.JSONDecodeError, OSError) as e:
            print(f"Warning: Failed to load local config: {e}", file=sys.stderr)
    
    # Load environment variables (prefixed with TEKTON_)
    for key, value in os.environ.items():
        if key.startswith("TEKTON_"):
            config_key = key[7:].lower().replace("_", "-")
            config[config_key] = value
    
    return config


def get_config(key: str, default: Optional[str] = None) -> str:
    """Get a configuration value or return default if not found."""
    config = load_config()
    
    # First check for exact key
    if key in config:
        return str(config[key])
    
    # Check for case-insensitive match
    key_lower = key.lower()
    for k, v in config.items():
        if k.lower() == key_lower:
            return str(v)
    
    # Key not found, return default
    return default if default is not None else ""


def set_config(key: str, value: str) -> bool:
    """Set a configuration value in the global config file."""
    # Create config directory if it doesn't exist
    os.makedirs(os.path.dirname(GLOBAL_CONFIG), exist_ok=True)
    
    # Load existing config or create a new one
    if os.path.exists(GLOBAL_CONFIG):
        try:
            with open(GLOBAL_CONFIG, 'r') as f:
                config = json.load(f)
        except (json.JSONDecodeError, OSError):
            config = {}
    else:
        config = {}
    
    # Update the configuration
    config[key] = value
    
    # Save to file
    try:
        with open(GLOBAL_CONFIG, 'w') as f:
            json.dump(config, f, indent=2)
        return True
    except OSError as e:
        print(f"Error: Failed to save configuration: {e}", file=sys.stderr)
        return False


def list_config() -> Dict[str, str]:
    """List all configuration values."""
    return load_config()


def get_component_port(component: str) -> int:
    """Get the standard port for a component."""
    component = component.lower()
    
    # Check if component port is defined
    if component in COMPONENT_PORTS:
        return COMPONENT_PORTS[component]
    
    # Unknown component
    print(f"Warning: Unknown component: {component}", file=sys.stderr)
    return 0


def generate_env_variables(format_type: str = "export") -> str:
    """Generate environment variables for all configuration values."""
    config = load_config()
    
    lines = []
    for key, value in config.items():
        env_key = f"TEKTON_{key.upper().replace('-', '_')}"
        
        if format_type == "export":
            lines.append(f'export {env_key}="{value}"')
        elif format_type == "docker":
            lines.append(f'{env_key}="{value}"')
        elif format_type == "dotenv":
            lines.append(f'{env_key}="{value}"')
        else:
            print(f"Warning: Unknown format type: {format_type}, using export", file=sys.stderr)
            lines.append(f'export {env_key}="{value}"')
    
    return "\n".join(lines)


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(description="Tekton Configuration CLI")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # get command
    get_parser = subparsers.add_parser("get", help="Get a configuration value")
    get_parser.add_argument("key", help="Configuration key")
    get_parser.add_argument("default", nargs="?", help="Default value if key not found")
    
    # set command
    set_parser = subparsers.add_parser("set", help="Set a configuration value")
    set_parser.add_argument("key", help="Configuration key")
    set_parser.add_argument("value", help="Value to set")
    
    # list command
    subparsers.add_parser("list", help="List all configuration values")
    
    # get-port command
    port_parser = subparsers.add_parser("get-port", help="Get the port for a component")
    port_parser.add_argument("component", help="Component name")
    
    # generate-env command
    env_parser = subparsers.add_parser("generate-env", help="Generate environment variables")
    env_parser.add_argument("--format", default="export", choices=["export", "docker", "dotenv"],
                           help="Output format [default: export]")
    
    args = parser.parse_args()
    
    if args.command == "get":
        value = get_config(args.key, args.default)
        print(value)
    
    elif args.command == "set":
        success = set_config(args.key, args.value)
        if not success:
            sys.exit(1)
    
    elif args.command == "list":
        config = list_config()
        print(json.dumps(config, indent=2))
    
    elif args.command == "get-port":
        port = get_component_port(args.component)
        print(port)
    
    elif args.command == "generate-env":
        env_vars = generate_env_variables(args.format)
        print(env_vars)
    
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
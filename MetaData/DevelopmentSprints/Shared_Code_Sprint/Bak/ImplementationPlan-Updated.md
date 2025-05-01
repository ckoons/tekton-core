# Tekton Shared Code Implementation Plan - Revised

## Phase 1: Create Core Shared Utilities (Week 1)

Let's start with the script utilities since they're more self-contained and will provide immediate benefits.

### 1. Create Bash Utility Library

Implementation Steps:

1. Create a directory structure for shared utilities:
```
scripts/
└── lib/
    ├── tekton-utils.sh       # Core shared utilities
    ├── tekton-ports.sh       # Port management
    ├── tekton-process.sh     # Process handling
    └── tekton-config.sh      # Configuration utilities
```
2. Implement tekton-utils.sh with core functions:
   - Color output and formatting
   - Directory detection
   - Common utility functions
   - Script logging
3. Implement tekton-ports.sh with port management:
   - Port assignment from environment variables
   - Port checking and availability
   - Port release functions
4. Implement tekton-process.sh with process management:
   - Process discovery
   - Process status checking
   - Process termination functions
5. Implement tekton-config.sh with configuration utilities:
   - Environment variable loading
   - Default value handling
   - Python configuration bridge

### 2. Create Python Configuration Bridge

Implementation Steps:

1. Create a CLI tool at scripts/bin/tekton-config-cli.py that:
   - Exposes tekton-core configuration to bash scripts
   - Provides port management functions
   - Supports environment variable configuration
2. Enhance tekton-core/tekton/utils/tekton_config.py to support:
   - Component-specific configuration
   - Environment variable overrides
   - Default value management

### 3. Update Core Scripts

Implementation Steps:

1. Refactor tekton-launch to use shared libraries
2. Refactor tekton-status to use shared libraries
3. Refactor tekton-kill to use shared libraries

## Phase 2: Create Unified Component Registration System (Week 2)

### 1. Create Core Registration Library

Implementation Steps:

1. Create a directory structure in tekton-core:
```
tekton-core/tekton/utils/registration/
├── __init__.py
├── cli.py               # Command-line interface
├── config.py            # Configuration loading
├── models.py            # Data models
├── registry.py          # Registration logic
└── heartbeat.py         # Heartbeat handling
```
2. Implement a data model for component capabilities:
   - Define standardized schema for components
   - Create validation utilities
   - Support serialization to/from JSON/YAML
3. Create registration handlers:
   - Implement Hermes API client
   - Create heartbeat functionality
   - Implement registration, unregistration, and status
4. Create a simple CLI interface:
```
tekton-register register --component=telos --config=./telos.yaml
```

### 2. Create Component Configuration Format

Implementation Approach:

Let's use YAML for configuration as it's more human-readable and supports comments:

```yaml
# telos.yaml
component:
  id: "telos"
  name: "Telos Requirements System"
  version: "0.1.0"
  description: "Requirements management and traceability system"
  port: 8800

capabilities:
  - id: "requirements_management"
    name: "Requirements Management"
    description: "Create and manage project requirements"
    methods:
      - id: "create_requirement"
        name: "Create Requirement"
        description: "Create a new requirement"
        parameters:
          - name: "name"
            type: "string"
            required: true
          - name: "description"
            type: "string"
            required: true
        returns:
          type: "object"

  - id: "requirements_analysis"
    name: "Requirements Analysis"
    # ... more capabilities
```

### 3. Implement tekton-register CLI Tool

Implementation Steps:

1. Create a standalone CLI tool at tekton-core/scripts/bin/tekton-register
2. Implement command line arguments:
   - Component name/ID specification
   - Configuration file path
   - Hermes URL configuration
   - Logging verbosity
3. Create core registration functionality:
   - Configuration loading and validation
   - Component registration with Hermes
   - Heartbeat maintenance
   - Graceful shutdown and unregistration
4. Add automatic component discovery:
   - Search for component.yaml in standard locations
   - Auto-detect component properties when possible
5. Create configuration generator:
   - Utility to generate template YAML files for components
   - Interactive mode for configuration setup

### 4. Migrate Initial Components

Implementation Steps:

1. Create YAML configurations for two initial components:
   - Telos: A newer component with clean structure
   - Rhetor: A core component with multiple capabilities
2. Replace their register_with_hermes.py scripts with the tekton-register utility
3. Test and validate registration functionality
4. Document the migration approach for other components

## Phase 3: Create LLM Integration Utilities (Week 3)

### 1. Enhance tekton-llm-client

Implementation Steps:

1. Create directory structure:
```
tekton-llm-client/
├── tekton_llm_client/
│   ├── prompt_templates/       # NEW: Shared prompt templates
│   │   ├── __init__.py
│   │   ├── registry.py
│   │   └── templates/
│   ├── response_handlers/      # NEW: Response parsers
│   │   ├── __init__.py
│   │   ├── json_parser.py
│   │   └── stream_handler.py
│   └── config/                 # NEW: Configuration
│       ├── __init__.py
│       └── environment.py
```
2. Implement prompt template system:
   - Create a registry for system prompts
   - Implement template rendering with variables
   - Add context management utilities
3. Implement response handlers:
   - Add structured output parsing
   - Create streaming response handler
   - Implement error handling utilities
4. Enhance configuration:
   - Create model selection utilities
   - Add fallback configuration
   - Implement environment-based configuration

### 2. Create Simple Migration Tool

Implementation Steps:

1. Create a script to analyze component LLM usage:
   - Detect LLM adapter patterns
   - Extract prompt templates
   - Identify response handling
2. Create a migration guide with examples:
   - Document common patterns
   - Show before/after examples
   - Provide step-by-step migration process

## Phase 4: Implement Across Components (Week 4)

### 1. Apply Script Utilities

Implementation Steps:

1. Update all component setup scripts to use shared utilities
2. Standardize launch processes across components
3. Create consistent configuration handling

### 2. Complete Component Registration Migration

Implementation Steps:

1. Create YAML configurations for all remaining components
2. Replace all register_with_hermes.py scripts with the tekton-register utility
3. Test all components with the new registration system
4. Create documentation for the new registration system:
   - Update COMPONENT_LIFECYCLE.md
   - Update SHARED_COMPONENT_UTILITIES.md
   - Create migration guide for future components

### 3. Update LLM Integration

Implementation Steps:

1. Migrate LLM adapters to use the enhanced tekton-llm-client
2. Convert prompt templates to the new system
3. Update response handling to use shared utilities

## Documentation Updates

The following documentation should be updated:

1. **COMPONENT_LIFECYCLE.md**: Document the standardized registration process.
2. **SHARED_COMPONENT_UTILITIES.md**: Add details about all shared utilities:
   - Bash utilities
   - Registration system
   - LLM integration utilities
3. **MetaData/TektonDocumentation/DeveloperGuides/SharedUtilities.md**: Comprehensive documentation of all utilities

## Detailed Implementation for First Week

Let's focus on the most impactful part first - creating and implementing the shell utilities.

### tekton-utils.sh - Core Module

```bash
#!/bin/bash
# Tekton Core Utilities - Shared functions for Tekton scripts

# Ensure bash environment
if [ -z "$BASH_VERSION" ]; then
  echo "Error: This script requires bash" >&2
  exit 1
fi

# ANSI color codes
export TEKTON_COLOR_BLUE="\033[94m"
export TEKTON_COLOR_GREEN="\033[92m"
export TEKTON_COLOR_YELLOW="\033[93m"
export TEKTON_COLOR_RED="\033[91m"
export TEKTON_COLOR_BOLD="\033[1m"
export TEKTON_COLOR_RESET="\033[0m"

# Tekton directory detection
tekton_find_root() {
  local script_dir="$1"

  if [[ "$script_dir" == *"/utils" ]]; then
    # Script is running from a symlink in utils
    echo $(cd "$script_dir" && cd "$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")" && cd "../.." && pwd)
  else
    # Script is running from Tekton/scripts
    echo "$(cd "$script_dir/.." && pwd)"
  fi
}

# Determine script and Tekton directories
TEKTON_SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export TEKTON_ROOT_DIR=$(tekton_find_root "$TEKTON_SCRIPT_DIR")

# Source additional utility modules if they exist
if [ -f "$TEKTON_SCRIPT_DIR/tekton-ports.sh" ]; then
  source "$TEKTON_SCRIPT_DIR/tekton-ports.sh"
fi

if [ -f "$TEKTON_SCRIPT_DIR/tekton-process.sh" ]; then
  source "$TEKTON_SCRIPT_DIR/tekton-process.sh"
fi

if [ -f "$TEKTON_SCRIPT_DIR/tekton-config.sh" ]; then
  source "$TEKTON_SCRIPT_DIR/tekton-config.sh"
fi

# Logging functions
tekton_log_info() {
  echo -e "${TEKTON_COLOR_BLUE}[INFO]${TEKTON_COLOR_RESET} $*"
}

tekton_log_success() {
  echo -e "${TEKTON_COLOR_GREEN}[SUCCESS]${TEKTON_COLOR_RESET} $*"
}

tekton_log_warn() {
  echo -e "${TEKTON_COLOR_YELLOW}[WARNING]${TEKTON_COLOR_RESET} $*"
}

tekton_log_error() {
  echo -e "${TEKTON_COLOR_RED}[ERROR]${TEKTON_COLOR_RESET} $*" >&2
}

# Check if tekton-core Python package is available
tekton_check_core() {
  python3 -c "import sys; sys.path.insert(0, '$TEKTON_ROOT_DIR'); import tekton.core" 2>/dev/null
  return $?
}

# Check if a command exists
tekton_command_exists() {
  command -v "$1" >/dev/null 2>&1
}

# Check if Tekton is installed properly
tekton_check_installation() {
  if [ ! -d "$TEKTON_ROOT_DIR" ]; then
    tekton_log_error "Tekton root directory not found"
    return 1
  fi

  if ! tekton_check_core; then
    tekton_log_warn "Tekton core Python package not available"
  fi

  return 0
}

# Initialize Tekton utilities
tekton_init() {
  tekton_check_installation

  # Initialize ports if function exists
  if declare -F tekton_load_ports >/dev/null; then
    tekton_load_ports
  fi
}

# Call initialization if not being sourced
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  tekton_init
  tekton_log_info "Tekton utilities initialized"
fi
```

### tekton-ports.sh - Port Management Module

```bash
#!/bin/bash
# Tekton Port Utilities - Functions for port management

# Get the Tekton configuration CLI path
TEKTON_CONFIG_CLI="$TEKTON_ROOT_DIR/scripts/bin/tekton-config-cli.py"

# Load port assignments from environment or Python configuration
tekton_load_ports() {
  # Try to load ports from Python if available
  if [ -f "$TEKTON_CONFIG_CLI" ] && tekton_command_exists python3; then
    # Use Python CLI to get port assignments as shell exports
    if eval "$($TEKTON_CONFIG_CLI list-ports --format=shell 2>/dev/null)"; then
      tekton_log_info "Loaded port assignments from Python configuration"
      return 0
    fi
  fi

  # Fallback to hardcoded defaults with environment variable override
  export HEPHAESTUS_PORT=${HEPHAESTUS_PORT:-8080}
  export ENGRAM_PORT=${ENGRAM_PORT:-8000}
  export HERMES_PORT=${HERMES_PORT:-8100}
  export ERGON_PORT=${ERGON_PORT:-8200}
  export LLM_ADAPTER_PORT=${LLM_ADAPTER_PORT:-8300}
  export RHETOR_PORT=${RHETOR_PORT:-8400}
  export ATHENA_PORT=${ATHENA_PORT:-8500}
  export PROMETHEUS_PORT=${PROMETHEUS_PORT:-8600}
  export HARMONIA_PORT=${HARMONIA_PORT:-8700}
  export TELOS_PORT=${TELOS_PORT:-8800}
  export SYNTHESIS_PORT=${SYNTHESIS_PORT:-5005}

  tekton_log_info "Loaded port assignments from defaults with environment overrides"
  return 0
}

# Check if a port is in use
tekton_is_port_used() {
  local port="$1"

  # Try lsof first (more common on Unix/Linux/macOS)
  if tekton_command_exists lsof; then
    lsof -iTCP:"$port" -sTCP:LISTEN -nP >/dev/null 2>&1
    return $?
  fi

  # Try netstat as fallback
  if tekton_command_exists netstat; then
    netstat -tuln | grep -q ":$port "
    return $?
  fi

  # No tools available
  tekton_log_warn "Neither lsof nor netstat found, can't check port $port"
  return 1
}

# Get the process using a port
tekton_get_port_process() {
  local port="$1"

  if tekton_command_exists lsof; then
    lsof -iTCP:"$port" -sTCP:LISTEN -nP -F p 2>/dev/null | grep '^p' | cut -c 2-
  elif tekton_command_exists netstat && tekton_command_exists pgrep; then
    local pid=$(netstat -tulnp 2>/dev/null | grep ":$port " | grep -o 'LISTEN.*' | grep -o '[0-9]*/[a-zA-Z0-9_-]\+' | cut -d'/' -f1)
    echo "$pid"
  else
    tekton_log_warn "Neither lsof nor netstat found, can't find process for port $port"
    echo ""
  fi
}

# Release a port if it's in use
tekton_release_port() {
  local port="$1"
  local description="$2"
  local force="$3"  # Set to "true" to use SIGKILL immediately

  if tekton_is_port_used "$port"; then
    tekton_log_warn "Releasing $description port $port..."
    local pids=$(tekton_get_port_process "$port")

    if [ -n "$pids" ]; then
      tekton_log_warn "Killing processes using port $port: $pids"

      if [ "$force" = "true" ]; then
        # Force kill immediately
        kill -9 $pids 2>/dev/null || true
      else
        # Try graceful shutdown first
        kill $pids 2>/dev/null || true
        sleep 1

        # Check if still in use
        if tekton_is_port_used "$port"; then
          tekton_log_warn "Port $port still in use, using SIGKILL"
          kill -9 $(tekton_get_port_process "$port") 2>/dev/null || true
        fi
      fi

      sleep 1
      if tekton_is_port_used "$port"; then
        tekton_log_error "Warning: Port $port is still in use"
        return 1
      else
        tekton_log_success "✓ Port $port successfully released"
        return 0
      fi
    fi
  else
    tekton_log_info "Port $port is already free"
    return 0
  fi
}

# Get the port for a component
tekton_get_component_port() {
  local component="$1"
  local port_var="${component^^}_PORT"  # Convert to uppercase

  # Check if we have the variable defined
  if [ -n "${!port_var}" ]; then
    echo "${!port_var}"
    return 0
  fi

  # Try to get from Python configuration
  if [ -f "$TEKTON_CONFIG_CLI" ] && tekton_command_exists python3; then
    local port=$("$TEKTON_CONFIG_CLI" get-port "$component" 2>/dev/null)
    if [ -n "$port" ]; then
      echo "$port"
      return 0
    fi
  fi

  # Return failure
  return 1
}

# Initialize if not being sourced
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  tekton_load_ports
  tekton_log_info "Tekton port utilities initialized"
fi
```

### tekton-config-cli.py - Python Configuration Bridge

```python
#!/usr/bin/env python3
"""
Tekton Configuration CLI

Command-line interface for Tekton configuration, providing access
to configuration values for shell scripts.
"""

import sys
import os
import argparse
import json
from typing import Dict, Optional, Any, List

# Find Tekton root directory
script_dir = os.path.dirname(os.path.abspath(__file__))
tekton_root = os.path.dirname(os.path.dirname(script_dir))
sys.path.insert(0, tekton_root)

# Try to import Tekton configuration
try:
    from tekton.utils.tekton_config import TektonConfig
    HAS_TEKTON_CONFIG = True
except ImportError:
    HAS_TEKTON_CONFIG = False

# Define default port assignments in case config is unavailable
DEFAULT_PORTS = {
    "hephaestus": 8080,
    "engram": 8000,
    "hermes": 8100,
    "ergon": 8200,
    "llm_adapter": 8300,
    "rhetor": 8400,
    "athena": 8500,
    "prometheus": 8600,
    "harmonia": 8700,
    "telos": 8800,
    "synthesis": 5005,
}

def get_component_port(component: str) -> int:
    """Get the port for a component."""
    # Convert to lowercase for consistency
    component = component.lower()

    # Try environment variable first
    env_var = f"{component.upper()}_PORT"
    if env_var in os.environ:
        try:
            return int(os.environ[env_var])
        except ValueError:
            pass

    # Try Tekton config if available
    if HAS_TEKTON_CONFIG:
        try:
            config = TektonConfig()
            return config.get_port(component)
        except Exception:
            pass

    # Fall back to default ports
    if component in DEFAULT_PORTS:
        return DEFAULT_PORTS[component]

    raise ValueError(f"Unknown component: {component}")

def list_ports() -> Dict[str, int]:
    """List all standard port assignments."""
    components = list(DEFAULT_PORTS.keys())

    ports = {}
    for component in components:
        try:
            ports[component] = get_component_port(component)
        except Exception:
            continue

    return ports

def print_shell_exports() -> None:
    """Print shell export statements for all ports."""
    ports = list_ports()
    for component, port in ports.items():
        print(f"export {component.upper()}_PORT={port}")

def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Tekton Configuration CLI")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # get-port command
    get_port_parser = subparsers.add_parser("get-port", help="Get port for a component")
    get_port_parser.add_argument("component", help="Component ID (e.g., 'hermes')")

    # list-ports command
    list_ports_parser = subparsers.add_parser("list-ports", help="List all port assignments")
    list_ports_parser.add_argument("--format", choices=["json", "shell"], default="json",
                               help="Output format (default: json)")

    args = parser.parse_args()

    if args.command == "get-port":
        try:
            print(get_component_port(args.component))
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    elif args.command == "list-ports":
        if args.format == "json":
            print(json.dumps(list_ports(), indent=2))
        elif args.format == "shell":
            print_shell_exports()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
```

## Next Steps

Once we have these core utilities implemented, we can refactor the tekton-launch, tekton-status, and tekton-kill scripts to use them, and then proceed to the next phase of implementing the component registration system.
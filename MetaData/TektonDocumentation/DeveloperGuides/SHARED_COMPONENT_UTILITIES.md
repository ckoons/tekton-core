# Tekton Shared Component Utilities

This document describes the shared utilities available for Tekton components, how to use them, and best practices for incorporating them into your component development.

## Overview

Tekton provides a set of shared utilities to standardize common functionality across components. These utilities help ensure consistent behavior, reduce code duplication, and simplify component development.

## Shell Utilities

### Core Utilities (tekton-utils.sh)

The core utilities provide common functions for logging, directory detection, command execution, and cross-platform compatibility.

```bash
#!/bin/bash

# Source the utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/../lib/tekton-utils.sh"

# Use logging functions
tekton_info "Starting component..."
tekton_success "Component started"
tekton_warn "Warning message"
tekton_error_exit "Error message" 1

# Directory functions
TEKTON_ROOT=$(tekton_find_root)
tekton_is_in_tekton_dir "/some/path"

# Command utilities
if tekton_command_exists "python3"; then
    # Do something
fi

# Prompt user for input
VALUE=$(tekton_prompt_with_default "Enter value" "default")
if tekton_prompt_yes_no "Continue?" "y"; then
    # User chose yes
fi
```

### Port Management (tekton-ports.sh)

Utilities for managing ports according to Tekton's Single Port Architecture.

```bash
#!/bin/bash

# Source the utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/../lib/tekton-utils.sh"
source "${SCRIPT_DIR}/../lib/tekton-ports.sh"

# Check if a port is in use
if tekton_is_port_used 8080; then
    # Port is in use
fi

# Get process using a port
PROCESS_INFO=$(tekton_get_port_process 8080)

# Release a port
tekton_release_port 8080 "Hephaestus UI"

# Get a component's standard port
PORT=$(tekton_get_component_port "hermes")

# Ensure all ports are available
tekton_ensure_ports_available

# Check if a port is responding
if tekton_is_port_responding 8080 "localhost" "/health"; then
    # Service is healthy
fi

# Wait for a port to be available
tekton_wait_for_port_available 8080 30 "Hephaestus UI"

# Wait for a port to start responding
tekton_wait_for_port_responding 8080 30 "Hephaestus UI"
```

### Process Management (tekton-process.sh)

Utilities for starting, stopping, and monitoring processes.

```bash
#!/bin/bash

# Source the utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/../lib/tekton-utils.sh"
source "${SCRIPT_DIR}/../lib/tekton-ports.sh"
source "${SCRIPT_DIR}/../lib/tekton-process.sh"

# Check if a process is running
if tekton_is_running "hermes"; then
    # Process is running
fi

# Get PIDs of matching processes
PIDS=$(tekton_get_pids "hermes")

# Kill processes
tekton_kill_processes "hermes" "Hermes Service"

# Start a Python script in the background
PID=$(tekton_start_python_script "/path/to/script.py" "My Service" "--arg1" "--arg2")

# Start a component server
tekton_start_component_server "hermes" "hermes.api.app" "/path/to/Hermes" 8001

# Use Hermes for graceful shutdown
tekton_shutdown_via_hermes

# Get process information for a component
INFO=$(tekton_get_component_processes "hermes")
```

### Configuration Management (tekton-config.sh)

Utilities for loading and managing configuration from files and environment variables.

```bash
#!/bin/bash

# Source the utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/../lib/tekton-utils.sh"
source "${SCRIPT_DIR}/../lib/tekton-config.sh"

# Initialize configuration
tekton_init_config

# Get configuration values
VALUE=$(tekton_get_config "my-key" "default-value")
BOOL_VALUE=$(tekton_get_config_bool "my-bool" "false")
NUM_VALUE=$(tekton_get_config_number "my-num" "0")

# Set configuration values
tekton_set_config "my-key" "new-value"

# Save configuration to file
tekton_save_config "my-key" "saved-value"

# Parse command-line arguments
tekton_parse_args "$@"
```

## Python Utilities

### LLM Client

The `tekton_llm_client` package provides a standardized client for interacting with LLMs through Rhetor.

```python
import asyncio
from tekton_llm_client import (
    TektonLLMClient, 
    PromptTemplateRegistry, 
    parse_json,
    StructuredOutputParser, 
    OutputFormat
)

async def main():
    # Create an LLM client
    client = TektonLLMClient(component_id="my-component")
    await client.initialize()
    
    # Use prompt templates
    registry = PromptTemplateRegistry()
    prompt = registry.render(
        "code_review",
        language="python",
        code="def hello(): return 'Hello, world!'",
        focus_area="best practices"
    )
    
    # Generate text
    response = await client.generate_text(prompt=prompt)
    
    # Parse structured output
    data = parse_json(response.content)
    
    # Parse specific output formats
    parser = StructuredOutputParser(format=OutputFormat.LIST)
    items = parser.parse(response.content)
    
    # Clean up
    await client.shutdown()

asyncio.run(main())
```

### Component Registration

The `tekton.utils.registration` module provides utilities for registering components with the Hermes service registry.

```python
from tekton.utils.registration import (
    load_component_config,
    register_component,
    unregister_component,
    get_registration_status
)

async def main():
    # Load component configuration
    config = load_component_config("my-component")
    
    # Register component
    success, client = await register_component("my-component", config)
    
    if success:
        print("Component registered successfully")
        
        # Use the client for other operations
        await client.heartbeat()
        
        # When done, unregister and close the client
        await client.unregister()
        await client.close()
    else:
        print("Failed to register component")
```

## Command-Line Tools

### tekton-register

Registers Tekton components with the Hermes service registry.

```bash
# Register a component
tekton-register register --component rhetor

# Check registration status
tekton-register status --component rhetor

# Generate a template configuration
tekton-register generate --component my-component --port 8123 --output my-component.yaml

# List all registered components
tekton-register list

# Unregister a component
tekton-register unregister --component rhetor
```

### tekton-config-cli.py

Provides access to configuration values from bash scripts.

```bash
# Get a configuration value
value=$(tekton-config-cli.py get my-key default-value)

# Set a configuration value
tekton-config-cli.py set my-key "my value"

# Get a component port
port=$(tekton-config-cli.py get-port hephaestus)

# Generate environment variables
eval $(tekton-config-cli.py generate-env)
```

## New Shared Utilities

### Prompt Templates

A shared system for managing and rendering LLM prompt templates.

```python
from tekton_llm_client import PromptTemplateRegistry, load_template

# Create a registry with default templates
registry = PromptTemplateRegistry()

# Register a custom template
registry.register({
    "name": "api_design",
    "template": "Design a REST API for {{ service_name }} with these requirements:\n{{ requirements }}",
    "description": "Template for API design tasks."
})

# Load a template from a file
template = load_template("/path/to/templates/code_review.json")
registry.register(template)

# Render a template with variables
prompt = registry.render("api_design",
    service_name="User Management",
    requirements="- User registration\n- Authentication\n- Profile management"
)
```

### Response Handlers

Utilities for parsing and processing LLM responses in different formats.

```python
from tekton_llm_client import (
    parse_json, 
    StructuredOutputParser, 
    OutputFormat,
    StreamHandler
)

# Parse JSON from LLM response
try:
    data = parse_json("```json\n{\"key\": \"value\"}\n```")
    print(f"Parsed: {data}")
except Exception as e:
    print(f"Parsing error: {e}")

# Parse different output formats
parser = StructuredOutputParser(format=OutputFormat.LIST)
items = parser.parse("1. First item\n2. Second item\n3. Third item")

# Process streaming responses
async def handle_stream():
    stream = client.generate_text(prompt="Write a story", streaming=True)
    handler = StreamHandler()
    result = await handler.process_stream(stream)
    print(f"Complete text: {result}")
```

### Configuration Utilities

Utilities for managing configuration from environment variables and files.

```python
from tekton_llm_client.config import (
    get_env, set_env, load_settings, save_settings,
    ClientSettings, LLMSettings
)

# Get/set environment variables
debug = get_env_bool("DEBUG", default=False)
set_env("APP_MODE", "production")

# Load settings from file and environment
settings = load_settings(
    component_id="my-component",
    file_path="/path/to/settings.json",
    load_from_env=True
)

# Create and save settings
my_settings = ClientSettings(
    component_id="my-component",
    llm=LLMSettings(
        provider="anthropic",
        model="claude-3-haiku-20240307"
    )
)
save_settings(my_settings, "/path/to/settings.json")
```

## Best Practices

1. **Use Shared Utilities**: Always prefer shared utilities over custom implementations.

2. **Port Management**: Use the standardized port assignments and environment variables rather than hardcoding port numbers.

3. **Component Registration**: Register your component with Hermes using the `tekton-register` utility to enable lifecycle management and service discovery.

4. **Error Handling**: Use the standardized error handling functions for consistent error reporting.

5. **Configuration**: Use the configuration utilities to load configuration from files and environment variables.

6. **Process Management**: Use the process management utilities for starting, stopping, and monitoring processes.

7. **Cross-Platform Compatibility**: Use the cross-platform utilities for OS-specific operations.

8. **LLM Integration**: Use the tekton-llm-client for all LLM interactions, including prompt templates and response handling.

## Migration Guide

To migrate existing components to use the shared utilities:

1. Replace custom logging with `tekton_info`, `tekton_success`, `tekton_warn`, and `tekton_error_exit`.

2. Replace port management code with `tekton_is_port_used`, `tekton_release_port`, etc.

3. Replace process management code with `tekton_is_running`, `tekton_kill_processes`, etc.

4. Replace configuration loading code with `tekton_get_config`, `tekton_set_config`, etc.

5. Replace component registration code with the `tekton-register` utility.

6. Replace custom LLM integration with the `tekton-llm-client` package.

7. Replace ad-hoc prompt templates with the shared prompt template system.

8. Replace custom response parsing with the shared response handlers.

## Examples

See the `examples` directory for complete examples of using the shared utilities and the enhanced tekton-llm-client.
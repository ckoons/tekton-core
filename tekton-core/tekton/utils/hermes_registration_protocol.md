# Standardized Hermes Registration Protocol for Tekton Components

This document outlines the standardized approach for all Tekton components to register with the Hermes service registry, maintain heartbeats, and handle component capabilities.

## Overview

The Hermes Registration Protocol establishes a consistent way for components to:

1. Register themselves with the central Hermes service registry
2. Advertise their capabilities to other components
3. Maintain health information through heartbeats
4. Gracefully shut down and unregister when necessary

## Core Concepts

### Component Identification

Each component must identify itself with:

- **Component ID**: Unique identifier (e.g., `athena.knowledge`, `harmonia.workflow`)
- **Component Name**: Human-readable name (e.g., `Athena Knowledge Graph`)
- **Component Type**: Category of component (e.g., `knowledge_graph`, `workflow_engine`)
- **Component Version**: Semantic version number (e.g., `0.1.0`)

### Capabilities

Components advertise their capabilities as a list of functions they can perform:

```json
[
  {
    "name": "create_workflow",
    "description": "Create a new workflow definition",
    "parameters": {
      "name": "string",
      "description": "string (optional)",
      "tasks": "array",
      "input": "object (optional)",
      "output": "object (optional)"
    }
  },
  {
    "name": "execute_workflow",
    "description": "Execute a workflow",
    "parameters": {
      "workflow_id": "string",
      "input": "object (optional)"
    }
  }
]
```

### Dependencies

Components can specify dependencies on other components:

```json
["hermes.core.database", "athena.knowledge"]
```

### Metadata

Additional metadata provides context about the component:

```json
{
  "description": "Workflow orchestration engine",
  "version": "0.1.0",
  "endpoints": {
    "api": "http://localhost:5006/api/workflows",
    "monitoring": "http://localhost:5006/metrics"
  }
}
```

## Registration Process

### Step 1: Initialize Registration Client

```python
from tekton.utils.hermes_registration import HermesRegistrationClient

client = HermesRegistrationClient(
    component_id="harmonia.workflow",
    component_name="Harmonia Workflow Engine",
    component_type="workflow_engine",
    component_version="0.1.0",
    capabilities=[...],
    dependencies=["hermes.core.database"]
)
```

### Step 2: Register with Hermes

```python
success = await client.register()
if success:
    print("Successfully registered!")
else:
    print("Registration failed!")
```

### Step 3: Maintain Heartbeats

The client automatically maintains heartbeats once registered.

### Step 4: Handle Shutdown

```python
# Set up signal handlers
client.setup_signal_handlers()

# When shutting down
await client.close()  # Stops heartbeats and unregisters
```

## Using the Template Script

Each component should implement a `register_with_hermes.py` script using the provided template.

1. Copy the template script to your component's directory
2. Customize the placeholders to match your component's details
3. Test the registration process

## Command-Line Usage

```
python register_with_hermes.py --hermes-url http://localhost:8000/api
```

## Environment Variables

- `HERMES_URL`: URL of the Hermes API
- `STARTUP_INSTRUCTIONS_FILE`: Path to JSON file with startup instructions
- `{COMPONENT_UPPER}_API_ENDPOINT`: API endpoint for the component

## Startup Instructions

Components can load startup instructions from a JSON file:

```json
{
  "component_id": "harmonia.workflow",
  "name": "Harmonia Workflow Engine",
  "type": "workflow_engine",
  "version": "0.1.0",
  "capabilities": [...],
  "dependencies": ["hermes.core.database"],
  "hermes_url": "http://localhost:8000/api",
  "endpoint": "http://localhost:5006/api/workflows",
  "metadata": {
    "description": "Workflow orchestration engine"
  }
}
```

## Service Discovery

Once registered, other components can discover and use the component's services:

```python
from hermes.api.client import HermesClient

# Initialize client
client = HermesClient(component_id="my.component")

# Discover workflow engines
workflow_engines = await client.discover_components(
    component_type="workflow_engine",
    capabilities=["execute_workflow"]
)

# Use the first available workflow engine
if workflow_engines:
    workflow_engine = workflow_engines[0]
    result = await client.invoke_capability(
        component_id=workflow_engine.component_id,
        capability="execute_workflow",
        parameters={
            "workflow_id": "my-workflow",
            "input": {"key": "value"}
        }
    )
```

## Best Practices

1. **Capability Design**: Make capabilities atomic and well-defined
2. **Resilient Registration**: Handle registration failures gracefully
3. **Graceful Shutdown**: Ensure proper unregistration when shutting down
4. **Health Reporting**: Report accurate health status in heartbeats
5. **Version Compatibility**: Include version information in capabilities
6. **Dependency Management**: Clearly specify dependencies
7. **Error Handling**: Properly handle communication errors
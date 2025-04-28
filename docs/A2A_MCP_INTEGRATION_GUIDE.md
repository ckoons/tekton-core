# A2A and MCP Integration Guide

This document provides guidelines for integrating the Agent-to-Agent (A2A) Communication Framework and Multimodal Cognitive Protocol (MCP) into Tekton components.

## Overview

The A2A and MCP protocols extend the capabilities of Tekton components by enabling:

1. **Agent-to-Agent Communication** - Autonomous agent collaboration through a standardized messaging protocol
2. **Multimodal Content Processing** - Unified handling of different content types (text, code, images, structured data)
3. **Tool Registration and Discovery** - Dynamic tool registration and discovery across components
4. **Context Management** - Persistent, enhanceable context across modalities and conversations

## Integration Architecture

### Single Port Architecture Integration

Both A2A and MCP follow Tekton's Single Port Architecture:

| Protocol | HTTP Endpoints | WebSocket Endpoints |
|----------|---------------|---------------------|
| A2A | `/api/a2a/*` | `/ws` (with `protocol: "a2a"`) |
| MCP | `/api/mcp/*` | `/ws` (with `protocol: "mcp"`) |

All components share the same port for both HTTP and WebSocket communication, using path-based routing to distinguish between different protocols and operations.

### Client Libraries

Each component should use the provided client libraries:

- `A2AClient` for agent-to-agent communication
- `MCPClient` for multimodal content processing

These clients handle the communication details, allowing components to focus on their core functionality.

## A2A Integration Steps

### 1. Add A2A Client

```python
from tekton.a2a.client import A2AClient

# Create A2A client
a2a_client = A2AClient(
    agent_id="my-component-agent",
    agent_name="My Component Agent",
    capabilities={"processing": ["capability1", "capability2"]}
)

# Initialize and register
await a2a_client.initialize()
await a2a_client.register()
```

### 2. Implement Message Handling

```python
# Handle incoming messages
async def handle_message(message):
    sender = message.get("sender", {}).get("agent_id")
    content = message.get("content", {})
    
    # Process message based on content and intent
    response_content = await process_message(content)
    
    # Send response if needed
    if message.get("message_type") == "request":
        await a2a_client.send_message(
            recipients=[{"agent_id": sender}],
            content=response_content,
            message_type="response",
            conversation_id=message.get("conversation_id"),
            reply_to=message.get("message_id")
        )
```

### 3. Register API Endpoints

```python
from fastapi import APIRouter

router = APIRouter(prefix="/api/a2a", tags=["a2a"])

@router.post("/messages/receive")
async def receive_message(message: dict):
    return await handle_message(message)
```

## MCP Integration Steps

### 1. Add MCP Client

```python
from tekton.mcp.client import MCPClient

# Create MCP client
mcp_client = MCPClient(
    client_id="my-component-mcp",
    client_name="My Component MCP Client"
)

# Initialize
await mcp_client.initialize()
```

### 2. Register Tools (if applicable)

```python
# Define a tool handler
async def my_tool_handler(parameters, context):
    # Tool implementation
    return {"result": "Tool output"}

# Register tool
await mcp_client.register_tool(
    tool_id="my-tool",
    name="My Tool",
    description="Tool description",
    parameters={"type": "object", "properties": {...}},
    returns={"type": "object", "properties": {...}},
    handler=my_tool_handler
)
```

### 3. Process Content

```python
# Process multimodal content
result = await mcp_client.process_content(
    content="Content to process",
    content_type="text",  # or "code", "image", "structured"
    processing_options={"option1": "value1"},
    context={"context_id": "my-context"}
)
```

## Service Discovery

Components publish and discover A2A agents and MCP tools through Hermes:

### Publishing Capabilities

1. **Agent Registration**: When an A2A client registers, it publishes its capabilities to Hermes
2. **Tool Registration**: When an MCP tool is registered, it becomes discoverable through Hermes

### Discovering Capabilities

1. **Agent Discovery**: Components can discover agents by their capabilities
   ```python
   agents = await a2a_client.discover_agents(capabilities=["capability1", "capability2"])
   ```

2. **Tool Discovery**: Components can discover available tools
   ```python
   tools = await mcp_client.list_tools(capability="image_processing")
   ```

## External Tool Integration

External tools can be integrated through the MCP protocol:

1. **Registration**: External tools register with Hermes using the MCP tool registration endpoint
2. **Execution**: Tools can be executed by any component through the MCP service
3. **Discovery**: External tools appear alongside internal tools in discovery results

## Best Practices

1. **Use Shared Utilities**: Leverage `tekton_http`, `tekton_websocket`, and other shared utilities
2. **Follow Single Port Architecture**: Use the standardized URL patterns
3. **Implement Graceful Degradation**: Handle cases where services are unavailable
4. **Use Standardized Error Handling**: Follow the error handling conventions
5. **Add Health Checks**: Implement `/health` endpoints for A2A and MCP services
6. **Document Capabilities**: Clearly document agent capabilities and tool functionality
7. **Validate Content**: Validate content and parameters before processing

## Example Integration

The Ergon component demonstrates full A2A and MCP integration:

- `/Ergon/ergon/core/a2a_client.py` - A2A client implementation
- `/Ergon/ergon/core/mcp_client.py` - MCP client implementation
- `/Ergon/ergon/api/a2a_endpoints.py` - A2A API endpoints
- `/Ergon/ergon/api/mcp_endpoints.py` - MCP API endpoints
- `/Ergon/ergon/utils/mcp_adapter.py` - MCP adapter utilities
- `/Ergon/ergon/utils/tekton_integration.py` - Tekton integration utilities
- `/Ergon/examples/a2a_mcp_integration.py` - A2A and MCP integration example

## Related Documentation

- [SINGLE_PORT_ARCHITECTURE.md](./SINGLE_PORT_ARCHITECTURE.md) - Details on Tekton's Single Port Architecture
- [COMPONENT_LIFECYCLE.md](./COMPONENT_LIFECYCLE.md) - Component lifecycle management
- [SHARED_COMPONENT_UTILITIES.md](./SHARED_COMPONENT_UTILITIES.md) - Shared utilities for component development
- [STANDARDIZED_ERROR_HANDLING.md](./STANDARDIZED_ERROR_HANDLING.md) - Error handling conventions
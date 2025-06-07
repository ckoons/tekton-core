# A2A Protocol v0.2.1 Implementation in Tekton

## Overview

The Agent-to-Agent (A2A) Protocol provides standardized communication between autonomous agents in the Tekton ecosystem. Our implementation follows the A2A Protocol v0.2.1 specification, using JSON-RPC 2.0 as the message format and providing a robust framework for agent discovery, task management, and inter-agent communication.

## Architecture

### Core Components

```
/tekton/a2a/
├── __init__.py           # Public API exports
├── jsonrpc.py           # JSON-RPC 2.0 implementation
├── errors.py            # Error definitions and handling
├── agent.py             # Agent Card and Registry
├── task.py              # Task lifecycle management
├── discovery.py         # Agent discovery service
└── methods.py           # Method dispatcher and standard methods
```

### Integration Architecture

```
┌─────────────────┐     JSON-RPC 2.0      ┌─────────────────┐
│   Component A   │◄──────────────────────►│     Hermes      │
│  (e.g., Ergon)  │                        │  (A2A Hub)      │
└─────────────────┘                        └─────────────────┘
                                                    │
                                                    │
                                          ┌─────────┴─────────┐
                                          │                   │
                                    ┌─────▼─────┐      ┌──────▼────┐
                                    │Component B│      │Component C│
                                    └───────────┘      └───────────┘
```

## Protocol Implementation

### JSON-RPC 2.0 Message Format

All A2A communication uses JSON-RPC 2.0:

```json
// Request
{
  "jsonrpc": "2.0",
  "method": "agent.register",
  "params": {
    "agent_card": {
      "id": "agent-123",
      "name": "My Agent",
      "capabilities": ["task_execution"],
      "supported_methods": ["custom.method"]
    }
  },
  "id": "req-456"
}

// Response
{
  "jsonrpc": "2.0",
  "result": {
    "success": true,
    "agent_id": "agent-123"
  },
  "id": "req-456"
}
```

### Standard Methods

The A2A implementation provides these standard methods:

#### Agent Management
- `agent.register` - Register an agent
- `agent.unregister` - Unregister an agent
- `agent.heartbeat` - Send heartbeat signal
- `agent.update_status` - Update agent status
- `agent.get` - Get agent information
- `agent.list` - List all online agents

#### Discovery
- `discovery.query` - Query agents with filters
- `discovery.find_for_method` - Find agent for specific method
- `discovery.find_for_capability` - Find agents with capability
- `discovery.capability_map` - Get capability to agent mapping
- `discovery.method_map` - Get method to agent mapping

#### Task Management
- `task.create` - Create a new task
- `task.assign` - Assign task to agent
- `task.update_state` - Update task state
- `task.update_progress` - Update task progress
- `task.complete` - Complete a task
- `task.fail` - Fail a task
- `task.cancel` - Cancel a task
- `task.get` - Get task information
- `task.list` - List tasks with filters

#### Hermes-Specific Extensions
- `agent.forward` - Forward method call to specific agent
- `channel.subscribe` - Subscribe to message channel
- `channel.unsubscribe` - Unsubscribe from channel
- `channel.publish` - Publish message to channel

## Implementation Details

### Agent Cards

Agents are described using Agent Cards (v0.2.1 spec):

```python
from tekton.a2a import AgentCard

agent_card = AgentCard.create(
    name="My Agent",
    description="An example agent",
    version="1.0.0",
    capabilities=["nlp", "code_generation"],
    supported_methods=["analyze.text", "generate.code"],
    endpoint="http://localhost:8000/api/a2a/v1/",
    tags=["ai", "assistant"]
)
```

### Task Lifecycle

Tasks follow a formal state machine:

```
   ┌─────────┐
   │ PENDING │──────┬────────► CANCELLED
   └────┬────┘      │
        │           │
        ▼           │
   ┌─────────┐      │
   │ RUNNING │──────┼────────► FAILED
   └────┬────┘      │
        │           │
        ├───────────┘
        │
        ├────────► PAUSED ──┐
        │                   │
        │◄──────────────────┘
        │
        ▼
   ┌───────────┐
   │ COMPLETED │
   └───────────┘
```

### Error Handling

A2A uses standard JSON-RPC error codes plus custom extensions:

```python
# Standard JSON-RPC errors
-32700  # Parse error
-32600  # Invalid Request
-32601  # Method not found
-32602  # Invalid params
-32603  # Internal error

# A2A custom errors (-32000 to -32099)
-32000  # Agent not found
-32001  # Task not found
-32002  # Unauthorized
-32003  # Capability not supported
-32004  # Invalid task state transition
-32005  # Rate limit exceeded
-32006  # Operation timeout
```

## Integration with Tekton Components

### Hermes as Central Hub

Hermes serves as the central A2A hub, providing:
1. Agent registration and discovery
2. Method routing between agents
3. Task management
4. Channel-based messaging

### Component Integration Steps

To add A2A support to a Tekton component:

1. **Create an A2A client**:
```python
from ergon.core.a2a_client import A2AClient

client = A2AClient(
    agent_name="My Component",
    capabilities=["my_capability"],
    supported_methods=["my.method"]
)

await client.initialize()  # Registers with Hermes
```

2. **Implement A2A endpoints** (optional):
```python
from fastapi import APIRouter
from tekton.a2a import JSONRPCRequest

router = APIRouter()

@router.post("/api/a2a/v1/")
async def handle_a2a(request: JSONRPCRequest):
    # Handle incoming A2A requests
    pass
```

3. **Use A2A for inter-component communication**:
```python
# Discover agents
agents = await client.discover_agents(capabilities=["text_processing"])

# Create and manage tasks
task = await client.create_task(
    name="Process Document",
    input_data={"document": "..."}
)

# Forward method calls
result = await client.forward_to_agent(
    agent_id="other-agent",
    method="process.text",
    params={"text": "..."}
)
```

## Testing

### Unit Testing

Run A2A unit tests:
```bash
python tests/run_unit_tests_only.py
```

### Integration Testing

Test A2A integration with a running Hermes instance:
```python
import aiohttp
import json

async def test_a2a():
    async with aiohttp.ClientSession() as session:
        # Test JSON-RPC endpoint
        request = {
            "jsonrpc": "2.0",
            "method": "agent.list",
            "id": 1
        }
        
        async with session.post(
            "http://localhost:8001/api/a2a/v1/",
            json=request
        ) as response:
            result = await response.json()
            print(f"Online agents: {result['result']}")
```

## Preparing for V1.0

The current implementation (v0.2.1) provides a solid foundation for the upcoming V1.0 release. Key areas for enhancement:

### 1. Streaming Support (Phase 2)
- Server-Sent Events (SSE) for real-time updates
- WebSocket support for bidirectional streaming
- Streaming task progress and logs

### 2. Enhanced Security (Phase 3)
- JWT-based authentication
- OAuth 2.0 support
- Method-level authorization
- Rate limiting per agent

### 3. Persistence
- Agent state persistence in Hermes database
- Task history and audit logs
- Conversation history

### 4. Advanced Features
- Agent capability negotiation
- Multi-agent task coordination
- Distributed task execution
- Agent health monitoring and auto-recovery

## Maintenance Guidelines

### Adding New Methods

1. Define method in `methods.py`:
```python
async def my_new_method(param1: str, param2: int) -> Dict[str, Any]:
    """Documentation for the method"""
    # Implementation
    return {"result": "success"}
```

2. Register with dispatcher:
```python
dispatcher.register_method("category.my_method", my_new_method)
```

3. Update agent capabilities:
```python
supported_methods.append("category.my_method")
```

### Monitoring and Debugging

Enable debug logging:
```python
import logging
logging.getLogger("tekton.a2a").setLevel(logging.DEBUG)
```

Monitor A2A traffic through Hermes logs:
```bash
tail -f logs/hermes.log | grep "a2a"
```

### Performance Considerations

1. **Connection Pooling**: A2A clients use aiohttp session pooling
2. **Batch Requests**: Use JSON-RPC batch requests for multiple operations
3. **Heartbeat Interval**: Default 60s, adjust based on network latency
4. **Task Cleanup**: Implement periodic cleanup of completed tasks

## Best Practices

1. **Always use structured errors** - Return proper JSON-RPC error responses
2. **Implement heartbeats** - Keep agent registration active
3. **Handle disconnections gracefully** - Re-register on connection loss
4. **Use appropriate task states** - Follow the state machine
5. **Document custom methods** - Include in agent card metadata
6. **Version your agents** - Use semantic versioning
7. **Test state transitions** - Ensure valid task lifecycle

## References

- [A2A Protocol Specification v0.2.1](https://google-a2a.github.io/A2A/specification/)
- [JSON-RPC 2.0 Specification](https://www.jsonrpc.org/specification)
- [Tekton A2A Implementation](/tekton/a2a/)
- [Phase 1 Status Report](/MetaData/DevelopmentSprints/A2Av2_Sprint/PHASE1_STATUS.md)
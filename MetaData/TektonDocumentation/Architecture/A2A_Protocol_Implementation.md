# A2A Protocol v0.2.1 Implementation in Tekton

## Overview

The Agent-to-Agent (A2A) Protocol v0.2.1 provides a standardized communication framework for autonomous agents within the Tekton ecosystem. This implementation uses JSON-RPC 2.0 as the message format and supports both request-response and streaming communication patterns.

## Architecture

### Core Components

1. **JSON-RPC Layer** (`/tekton/a2a/jsonrpc.py`)
   - Implements JSON-RPC 2.0 specification
   - Handles single requests, batch requests, and notifications
   - Provides error handling and response formatting

2. **Agent Registry** (`/tekton/a2a/agent.py`)
   - Manages agent registration and lifecycle
   - Tracks agent capabilities and status
   - Implements Agent Card format compliance

3. **Task Manager** (`/tekton/a2a/task.py`)
   - Handles task creation, assignment, and lifecycle
   - Supports state transitions with validation
   - Emits events for streaming (Phase 2)

4. **Discovery Service** (`/tekton/a2a/discovery.py`)
   - Provides agent discovery by capability
   - Supports method-based agent lookup
   - Enables dynamic service discovery

5. **Method Dispatcher** (`/tekton/a2a/methods.py`)
   - Routes JSON-RPC methods to handlers
   - Implements standard A2A methods
   - Extensible for custom methods

6. **Streaming Support** (`/tekton/a2a/streaming/`) - Phase 2
   - Server-Sent Events (SSE) for real-time updates
   - Event-driven architecture with filters
   - Subscription management for targeted delivery

### Integration with Hermes

Hermes serves as the central hub for A2A communication:

1. **A2A Service** (`/Hermes/hermes/core/a2a_service.py`)
   - Bridges Hermes infrastructure with A2A protocol
   - Manages component lifecycle
   - Handles event routing

2. **A2A Endpoints** (`/Hermes/hermes/api/a2a_endpoints.py`)
   - Provides JSON-RPC endpoint at `/api/a2a/v1/`
   - Well-known agent card at `/.well-known/agent.json`
   - SSE streaming at `/api/a2a/v1/stream/events`

## Implementation Phases

### Phase 1: Core Protocol (Completed)

- ✅ JSON-RPC 2.0 message handling
- ✅ Agent registration and discovery
- ✅ Task lifecycle management
- ✅ Method dispatcher with standard methods
- ✅ Integration with Hermes
- ✅ Comprehensive test suite (96 tests)

### Phase 2: Streaming Support (In Progress)

- ✅ SSE implementation for unidirectional streaming
- ✅ Event-driven task updates
- ✅ Subscription management
- ✅ Connection filtering
- 🔄 WebSocket support (pending)
- 🔄 Channel-based pub/sub (pending)

### Phase 3: Advanced Features (Future)

- Multi-agent conversation support
- Distributed task coordination
- Capability negotiation
- Security and authentication

## Standard A2A Methods

### Agent Methods
- `agent.register` - Register a new agent
- `agent.unregister` - Remove an agent
- `agent.heartbeat` - Update agent heartbeat
- `agent.update_status` - Change agent status
- `agent.get` - Get agent details
- `agent.list` - List all agents

### Task Methods
- `task.create` - Create a new task
- `task.assign` - Assign task to agent
- `task.update_state` - Update task state
- `task.update_progress` - Update task progress
- `task.complete` - Mark task complete
- `task.fail` - Mark task failed
- `task.cancel` - Cancel a task
- `task.get` - Get task details
- `task.list` - List tasks

### Discovery Methods
- `discovery.query` - Query agents by criteria
- `discovery.find_for_method` - Find agents supporting a method
- `discovery.find_for_capability` - Find agents with capability
- `discovery.capability_map` - Get capability to agents mapping
- `discovery.method_map` - Get method to agents mapping

### Hermes-Specific Methods
- `agent.forward` - Forward request to specific agent
- `channel.subscribe` - Subscribe to a channel
- `channel.unsubscribe` - Unsubscribe from channel
- `channel.publish` - Publish to channel

## Testing

### Running Tests

```bash
# Run all A2A tests
python tests/run_a2a_all_tests.py

# Run only unit tests
python tests/run_a2a_all_tests.py -u

# Run only integration tests
python tests/run_a2a_all_tests.py -i

# Run manual streaming test
python tests/manual/test_a2a_streaming.py
```

### Test Coverage

- **Unit Tests**: Core protocol components, JSON-RPC handling, streaming
- **Integration Tests**: Hermes integration, end-to-end flows
- **Manual Tests**: SSE streaming, subscription management

## Usage Examples

### Basic Agent Registration

```python
# JSON-RPC request
{
    "jsonrpc": "2.0",
    "method": "agent.register",
    "params": {
        "agent_card": {
            "name": "MyAgent",
            "description": "Example agent",
            "version": "1.0.0",
            "capabilities": ["task_processing"],
            "supported_methods": ["custom.method"],
            "endpoint": "http://localhost:8005/"
        }
    },
    "id": 1
}
```

### Creating and Monitoring a Task with SSE

```python
# Create task
{
    "jsonrpc": "2.0",
    "method": "task.create",
    "params": {
        "name": "Process Data",
        "description": "Process user data",
        "priority": "high"
    },
    "id": 1
}

# Connect to SSE stream
GET /api/a2a/v1/stream/events?task_id=task-123

# Receive real-time updates
data: {"type": "task.state_changed", "task_id": "task-123", ...}
data: {"type": "task.progress", "task_id": "task-123", "progress": 0.5, ...}
data: {"type": "task.completed", "task_id": "task-123", ...}
```

## Development Guidelines

### Adding New Methods

1. Define method handler in appropriate module
2. Register with method dispatcher
3. Add tests for the new method
4. Update documentation

### Extending Streaming

1. Create new event types in `events.py`
2. Add event emission in relevant components
3. Update filters if needed
4. Test with SSE client

### Debugging

- Enable debug logging: `export LOG_LEVEL=DEBUG`
- Check Hermes logs for A2A service messages
- Use manual test scripts for interactive testing
- Monitor SSE connections at `/api/a2a/v1/stream/connections`

## Migration from Legacy A2A

The new implementation is not backwards compatible. Key changes:

1. **Message Format**: Custom format → JSON-RPC 2.0
2. **Agent Registration**: Direct registration → Agent Cards
3. **Task Management**: Simple states → Full lifecycle
4. **Discovery**: Basic listing → Advanced querying
5. **Streaming**: Not supported → SSE/WebSocket

## Future Enhancements

1. **Security**
   - Agent authentication
   - Message signing
   - Capability-based access control

2. **Performance**
   - Connection pooling
   - Event batching
   - Caching layer

3. **Reliability**
   - Message persistence
   - Delivery guarantees
   - Retry mechanisms

4. **Monitoring**
   - Metrics collection
   - Health checks
   - Performance tracking
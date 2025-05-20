# LLM Adapter MCP Integration

This document describes the Model Context Protocol (MCP) integration for LLM Adapter, the unified language model interface and conversation management system in the Tekton ecosystem.

## Overview

LLM Adapter implements FastMCP (Fast Model Context Protocol) to provide a standardized interface for language model interactions, conversation management, streaming operations, and provider abstraction. This integration allows external systems and AI models to interact with various language model providers through a consistent, well-defined API.

## Architecture

### Integration Approach

LLM Adapter uses an **integrated implementation** approach for MCP integration:

- **Main API Server** (`/api/*`): Provides the full LLM Adapter REST API on port 8006
- **FastMCP Integration** (`/api/mcp/v2/*`): Integrated FastMCP endpoints within the main server
- **Multi-Protocol Support**: HTTP, WebSocket, and Server-Sent Events (SSE)

This approach ensures seamless integration while providing modern FastMCP capabilities for language model operations.

### FastMCP Implementation

The FastMCP integration includes:

1. **Tool Registration**: All tools are registered with the FastMCP registry using decorators
2. **Provider Abstraction**: Unified interface across multiple LLM providers
3. **Capability Grouping**: Tools are organized into logical capabilities
4. **Error Handling**: Comprehensive error handling with meaningful error messages
5. **Real-time Support**: WebSocket and streaming capabilities

## Capabilities and Tools

### Model Management Capability

The `model_management` capability provides comprehensive model discovery and configuration.

#### Tools

1. **list_available_models**
   - List all available language models and providers
   - Parameters: `provider` (optional), `model_type` (optional)
   - Returns: Available models with details and capabilities

2. **get_model_info**
   - Get detailed information about a specific model
   - Parameters: `model_name`, `provider`
   - Returns: Model specifications, pricing, and limits

3. **set_default_model**
   - Set the default model for conversations
   - Parameters: `model_name`, `provider`
   - Returns: Configuration update confirmation

4. **validate_model_config**
   - Validate model configuration parameters
   - Parameters: `config`
   - Returns: Validation results and suggestions

### Conversation Capability

The `conversation` capability handles message exchange and conversation management.

#### Tools

1. **send_message**
   - Send a message to a language model and get a response
   - Parameters: `message`, `conversation_id` (optional), `model` (optional), `provider` (optional), `temperature`, `max_tokens`
   - Returns: Response with metadata and token usage

2. **create_conversation**
   - Create a new conversation with optional system prompt
   - Parameters: `name` (optional), `system_prompt` (optional), `model` (optional), `provider` (optional)
   - Returns: Conversation ID and configuration

3. **get_conversation_history**
   - Get the message history for a conversation
   - Parameters: `conversation_id`, `limit` (optional), `offset` (optional)
   - Returns: Message history with pagination

4. **clear_conversation**
   - Clear the message history for a conversation
   - Parameters: `conversation_id`
   - Returns: Confirmation of history clearing

### Streaming Capability

The `streaming` capability provides real-time conversation streaming.

#### Tools

1. **start_streaming_conversation**
   - Start a streaming conversation session
   - Parameters: `conversation_id` (optional), `model` (optional), `provider` (optional)
   - Returns: Streaming session details and WebSocket URL

2. **send_streaming_message**
   - Send a message in a streaming conversation
   - Parameters: `session_id`, `message`, `stream_options`
   - Returns: Stream initiation confirmation

3. **stop_streaming_conversation**
   - Stop an active streaming session
   - Parameters: `session_id`
   - Returns: Session termination confirmation

### Integration Capability

The `integration` capability manages connections with Tekton components and external systems.

#### Tools

1. **register_with_hermes**
   - Register LLM Adapter capabilities with Hermes
   - Parameters: `service_info` (optional)
   - Returns: Registration confirmation and service ID

2. **health_check**
   - Check the health status of the LLM Adapter
   - Parameters: None
   - Returns: Health status, performance metrics, and connection status

3. **get_adapter_status**
   - Get detailed status information about the LLM Adapter
   - Parameters: None
   - Returns: Configuration, statistics, and active sessions

## API Endpoints

### Standard FastMCP Endpoints

- `GET /api/mcp/v2/capabilities` - List all capabilities
- `GET /api/mcp/v2/tools` - List all tools
- `POST /api/mcp/v2/process` - Execute tools
- `GET /api/mcp/v2/health` - Health check

### Streaming Endpoints

- `GET /ws/stream` - WebSocket endpoint for streaming conversations
- `GET /api/sse/stream` - Server-Sent Events for real-time updates

## Usage Examples

### Python Client Example

```python
from tekton.mcp.fastmcp.client import FastMCPClient

# Connect to LLM Adapter FastMCP
client = FastMCPClient("http://localhost:8006/api/mcp/v2")

# List available models
models_result = await client.call_tool("list_available_models", {})
print(f"Available models: {models_result['total_count']}")

# Create a conversation
conversation_result = await client.call_tool("create_conversation", {
    "name": "AI Assistant Chat",
    "system_prompt": "You are a helpful AI assistant.",
    "model": "claude-3-haiku",
    "provider": "anthropic"
})

conversation_id = conversation_result["conversation_id"]

# Send a message
message_result = await client.call_tool("send_message", {
    "message": "Explain quantum computing in simple terms",
    "conversation_id": conversation_id,
    "temperature": 0.7,
    "max_tokens": 500
})

print(f"Response: {message_result['response']}")
print(f"Tokens used: {message_result['tokens_used']}")
```

### Model Management Examples

```python
# Get information about a specific model
model_info = await client.call_tool("get_model_info", {
    "model_name": "gpt-4",
    "provider": "openai"
})

print(f"Model capabilities: {model_info['capabilities']}")
print(f"Max tokens: {model_info['parameters']['max_tokens']}")
print(f"Cost per 1K tokens: ${model_info['pricing']['input_cost_per_1k_tokens']}")

# Set default model
set_default = await client.call_tool("set_default_model", {
    "model_name": "claude-3-haiku", 
    "provider": "anthropic"
})

# List models by provider
anthropic_models = await client.call_tool("list_available_models", {
    "provider": "anthropic",
    "model_type": "chat"
})
```

### Streaming Examples

```python
# Start a streaming conversation
streaming_session = await client.call_tool("start_streaming_conversation", {
    "conversation_id": conversation_id,
    "model": "claude-3-haiku"
})

session_id = streaming_session["session_id"]
websocket_url = streaming_session["websocket_url"]

# Connect to WebSocket for real-time streaming
import websockets

async with websockets.connect(websocket_url) as websocket:
    # Send streaming message
    await websocket.send(json.dumps({
        "type": "message",
        "content": "Tell me a story",
        "session_id": session_id
    }))
    
    # Receive streaming response
    async for message in websocket:
        data = json.loads(message)
        if data["type"] == "content":
            print(data["content"], end="", flush=True)
        elif data["type"] == "done":
            break
```

### Conversation Management Examples

```python
# Get conversation history
history = await client.call_tool("get_conversation_history", {
    "conversation_id": conversation_id,
    "limit": 50
})

for message in history["messages"]:
    role = message["role"]
    content = message["content"]
    timestamp = message["timestamp"]
    print(f"[{timestamp}] {role}: {content}")

# Create conversation with custom configuration
custom_conversation = await client.call_tool("create_conversation", {
    "name": "Code Review Assistant",
    "system_prompt": "You are an expert code reviewer. Provide detailed, constructive feedback.",
    "model": "gpt-4",
    "provider": "openai"
})
```

## Installation and Setup

### Dependencies

LLM Adapter FastMCP requires:
```
tekton-core>=0.1.0
anthropic>=0.10.0
fastapi>=0.103.0
uvicorn>=0.23.2
websockets>=11.0.3
```

### Provider Configuration

#### Anthropic Configuration
```bash
export ANTHROPIC_API_KEY=your_api_key_here
```

#### OpenAI Configuration  
```bash
export OPENAI_API_KEY=your_api_key_here
```

#### Local Model Configuration
```bash
export LOCAL_MODEL_ENDPOINT=http://localhost:8080
export LOCAL_MODEL_TYPE=llama
```

### Running the Server

```bash
# Start LLM Adapter with integrated FastMCP
python -m llm_adapter.server
```

FastMCP endpoints available at: `http://localhost:8006/api/mcp/v2`

### Configuration

Environment variables:
- `LLM_ADAPTER_PORT`: Port for server (default: 8006)
- `LLM_ADAPTER_LOG_LEVEL`: Logging level (default: info)
- `DEFAULT_MODEL`: Default model to use
- `DEFAULT_PROVIDER`: Default provider to use
- `MAX_CONCURRENT_REQUESTS`: Maximum concurrent requests (default: 100)

## Testing

Run the comprehensive test suite:

```bash
# Test FastMCP integration
./examples/run_fastmcp_test.sh

# Test with custom URL
./examples/run_fastmcp_test.sh --url http://localhost:8006

# Test with cleanup
./examples/run_fastmcp_test.sh --cleanup
```

The test suite validates:
- Server availability and health
- All capabilities and tools
- Model management operations
- Conversation functionality
- Streaming capabilities
- Integration features
- Error handling

## Error Handling

All tools return consistent error responses:

```json
{
  "error": "Description of what went wrong"
}
```

Common error scenarios:
- **Model not available**: Requested model or provider unavailable
- **Authentication failed**: Invalid API keys or credentials
- **Rate limit exceeded**: Provider rate limits reached
- **Invalid parameters**: Malformed request parameters
- **Conversation not found**: Invalid conversation ID

## Provider Support

### Supported Providers

1. **Anthropic**
   - Models: Claude 3.7 Sonnet, Claude 3 Haiku, Claude Instant
   - Features: Chat, completion, streaming
   - Authentication: API Key

2. **OpenAI**
   - Models: GPT-4, GPT-3.5-turbo, text-embedding-ada-002
   - Features: Chat, completion, embeddings, streaming
   - Authentication: API Key

3. **Local Models**
   - Support for local Llama, CodeLlama, and other models
   - Features: Chat, completion (streaming depends on implementation)
   - Authentication: None

4. **Custom Providers**
   - Extensible architecture for adding new providers
   - Plugin-based provider registration
   - Standardized provider interface

## Performance Considerations

- **Connection Pooling**: Automatic connection pooling for provider APIs
- **Request Batching**: Batch multiple requests where supported
- **Caching**: Response caching for model information and configuration
- **Rate Limiting**: Built-in rate limiting and backoff strategies
- **Load Balancing**: Provider failover and load distribution

## Security

- **API Key Management**: Secure storage and rotation of provider API keys
- **Input Validation**: All tool parameters validated using Pydantic models
- **Request Sanitization**: Input sanitization to prevent injection attacks
- **Rate Limiting**: Protection against abuse and excessive usage
- **CORS Configuration**: Configurable CORS policies for production

## Integration with Other Components

### Hermes Integration

LLM Adapter automatically registers with Hermes for service discovery:

```json
{
  "name": "llm_adapter",
  "type": "language_model_interface",
  "port": 8006,
  "health_endpoint": "/health",
  "capabilities": ["model_management", "conversation", "streaming"]
}
```

### Engram Integration

Store and retrieve conversation memories:
- Conversation history → Long-term memory
- Model preferences → User preferences
- Usage patterns → Learning data

### Terma Integration

Provide LLM access to terminal interfaces:
- Command assistance → Natural language interfaces
- Error explanation → AI-powered help
- Script generation → Automated task creation

### Component Communication

Enable cross-component AI capabilities:
- Athena queries → Natural language knowledge retrieval
- Prometheus planning → AI-assisted project planning
- Rhetor analysis → Enhanced text processing

## Future Enhancements

Planned improvements:
1. **Advanced Model Features**: Function calling, tool use, multi-modal support
2. **Enhanced Streaming**: Parallel streaming, stream branching, real-time collaboration
3. **Provider Extensions**: Additional providers, custom model support
4. **Analytics Dashboard**: Usage analytics, cost tracking, performance monitoring
5. **Conversation Features**: Conversation templates, auto-summarization, context compression
6. **Enterprise Features**: Multi-tenancy, user management, audit logging

## Troubleshooting

### Common Issues

1. **Provider authentication failed**
   - Check API keys are correctly set in environment variables
   - Verify API key permissions and quotas
   - Ensure network connectivity to provider APIs

2. **Model not found errors**
   - Verify model name and provider combination
   - Check if model is available in your region
   - Ensure provider account has access to the model

3. **Request timeout**
   - Check model load and provider response times
   - Adjust timeout settings in configuration
   - Consider using smaller models for faster responses

4. **Streaming connection issues**
   - Verify WebSocket connectivity
   - Check firewall and proxy settings
   - Ensure client supports WebSocket protocol

### Debug Mode

Enable debug logging:
```bash
export LLM_ADAPTER_LOG_LEVEL=debug
python -m llm_adapter.server
```

### Health Monitoring

Monitor LLM Adapter health:
```python
health_result = await client.call_tool("health_check", {})
print(f"Service status: {health_result}")

status_result = await client.call_tool("get_adapter_status", {})
print(f"Active sessions: {status_result['active_sessions']}")
```

## Support

For issues related to LLM Adapter FastMCP integration:
1. Check server logs for detailed error messages
2. Run the test suite to identify specific failing operations
3. Verify provider API connectivity and authentication
4. Ensure proper environment configuration

## Conclusion

LLM Adapter FastMCP integration provides a powerful, standardized interface for language model operations within the Tekton ecosystem. The comprehensive tool set, multi-provider support, and real-time capabilities make it an essential component for AI-powered applications and cross-component language model access.

The integrated implementation approach ensures optimal performance while maintaining compatibility with the broader Tekton architecture, enabling sophisticated AI interactions and seamless language model integration across the entire ecosystem.
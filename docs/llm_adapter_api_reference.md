# LLM Adapter API Reference

## Overview

This document provides a comprehensive reference for the LLM Adapter's API interfaces, including HTTP endpoints, WebSocket communication protocol, request/response formats, and error handling.

## HTTP API

The LLM Adapter exposes the following HTTP endpoints for synchronous communication.

### Base URLs

- **Single Port Architecture**: `http://localhost:8003/api/`
- **Legacy**: `http://localhost:8300/`

### Endpoints

#### Root Endpoint

```
GET /
```

Returns basic information about the adapter.

**Response**

```json
{
  "name": "Tekton LLM Adapter",
  "version": "0.1.0",
  "status": "running",
  "endpoints": ["/message", "/stream", "/health"],
  "claude_available": true
}
```

#### Health Check

```
GET /health
```

Returns the health status of the adapter.

**Response**

```json
{
  "status": "healthy",
  "version": "0.1.0",
  "claude_available": true,
  "providers": ["anthropic", "simulated"]
}
```

#### Available Providers

```
GET /providers
```

Returns information about available LLM providers and models.

**Response**

```json
{
  "providers": {
    "anthropic": {
      "name": "Anthropic Claude",
      "available": true,
      "models": [
        {"id": "claude-3-sonnet-20240229", "name": "Claude 3 Sonnet"},
        {"id": "claude-3-opus-20240229", "name": "Claude 3 Opus"},
        {"id": "claude-3-haiku-20240307", "name": "Claude 3 Haiku"}
      ]
    },
    "simulated": {
      "name": "Simulated LLM",
      "available": true,
      "models": [
        {"id": "simulated-fast", "name": "Fast Simulation"},
        {"id": "simulated-standard", "name": "Standard Simulation"}
      ]
    }
  },
  "current_provider": "anthropic",
  "current_model": "claude-3-sonnet-20240229"
}
```

#### Set Provider and Model

```
POST /provider
```

Sets the active provider and model.

**Request**

```json
{
  "provider_id": "anthropic",
  "model_id": "claude-3-sonnet-20240229"
}
```

**Response**

```json
{
  "success": true,
  "provider": "anthropic",
  "model": "claude-3-sonnet-20240229"
}
```

#### Send Message

```
POST /message
```

Sends a message to the LLM and gets a response.

**Request**

```json
{
  "message": "Hello, how are you?",
  "context_id": "ergon",
  "streaming": false,
  "options": {
    "temperature": 0.7,
    "max_tokens": 4000,
    "model": "claude-3-sonnet-20240229"
  }
}
```

**Response (success)**

```json
{
  "message": "Hello! I'm doing well. How can I assist you with the Tekton system today?",
  "context": "ergon",
  "model": "claude-3-sonnet-20240229",
  "finished": true,
  "timestamp": "2025-04-28T19:20:00.123456"
}
```

**Response (error)**

```json
{
  "error": "Error message",
  "context": "ergon",
  "timestamp": "2025-04-28T19:20:00.123456"
}
```

#### Stream Message

```
POST /stream
```

Sends a message to the LLM and gets a streaming response using Server-Sent Events.

**Request**

```json
{
  "message": "Hello, how are you?",
  "context_id": "ergon",
  "options": {
    "temperature": 0.7,
    "max_tokens": 4000,
    "model": "claude-3-sonnet-20240229"
  }
}
```

**Response**

Server-Sent Events stream with the following event data format:

```json
{
  "chunk": "Hello",
  "context": "ergon",
  "timestamp": "2025-04-28T19:20:00.123456",
  "done": false
}
```

Final event:

```json
{
  "chunk": "",
  "context": "ergon",
  "timestamp": "2025-04-28T19:20:00.123456",
  "done": true
}
```

## WebSocket API

The LLM Adapter provides a WebSocket interface for real-time, bi-directional communication.

### Connection URLs

- **Single Port Architecture**: `ws://localhost:8003/ws`
- **Legacy**: `ws://localhost:8301`

### Message Protocol

All messages are JSON objects with a standardized structure.

#### Message Structure

```json
{
  "type": "MESSAGE_TYPE",
  "source": "SOURCE_IDENTIFIER",
  "target": "TARGET_IDENTIFIER",
  "timestamp": "ISO_TIMESTAMP",
  "payload": {
    // Message-specific data
  }
}
```

#### Client-to-Server Message Types

##### LLM Request

Sends a message to the LLM for processing.

```json
{
  "type": "LLM_REQUEST",
  "source": "UI",
  "target": "LLM",
  "timestamp": "2025-04-28T19:20:00.123456",
  "payload": {
    "message": "Hello, how are you?",
    "context": "ergon",
    "streaming": true,
    "options": {
      "temperature": 0.7,
      "max_tokens": 4000,
      "model": "claude-3-sonnet-20240229"
    }
  }
}
```

##### Registration

Registers a client with the WebSocket server.

```json
{
  "type": "REGISTER",
  "source": "UI",
  "timestamp": "2025-04-28T19:20:00.123456"
}
```

##### Status Request

Requests the current status of the adapter.

```json
{
  "type": "STATUS",
  "source": "UI",
  "timestamp": "2025-04-28T19:20:00.123456"
}
```

#### Server-to-Client Message Types

##### Update

Provides updates on processing status, typing indicators, and response chunks.

```json
{
  "type": "UPDATE",
  "source": "SYSTEM",
  "target": "UI",
  "timestamp": "2025-04-28T19:20:00.123456",
  "payload": {
    "status": "typing",
    "isTyping": true,
    "context": "ergon"
  }
}
```

##### Chunk Update (for streaming)

```json
{
  "type": "UPDATE",
  "source": "ergon",
  "target": "UI",
  "timestamp": "2025-04-28T19:20:00.123456",
  "payload": {
    "chunk": "Hello",
    "context": "ergon"
  }
}
```

##### Stream Complete

```json
{
  "type": "UPDATE",
  "source": "ergon",
  "target": "UI",
  "timestamp": "2025-04-28T19:20:00.123456",
  "payload": {
    "done": true,
    "context": "ergon"
  }
}
```

##### Response (for non-streaming)

```json
{
  "type": "RESPONSE",
  "source": "ergon",
  "target": "UI",
  "timestamp": "2025-04-28T19:20:00.123456",
  "payload": {
    "message": "Hello! I'm doing well. How can I assist you with the Tekton system today?",
    "context": "ergon"
  }
}
```

##### Registration Response

```json
{
  "type": "RESPONSE",
  "source": "SYSTEM",
  "target": "UI",
  "timestamp": "2025-04-28T19:20:00.123456",
  "payload": {
    "status": "registered",
    "message": "Client registered successfully with LLM Adapter"
  }
}
```

##### Status Response

```json
{
  "type": "RESPONSE",
  "source": "SYSTEM",
  "target": "UI",
  "timestamp": "2025-04-28T19:20:00.123456",
  "payload": {
    "status": "ok",
    "service": "llm_adapter",
    "version": "0.1.0",
    "claude_available": true,
    "message": "LLM Adapter is running"
  }
}
```

##### Error Response

```json
{
  "type": "ERROR",
  "source": "SYSTEM",
  "target": "UI",
  "timestamp": "2025-04-28T19:20:00.123456",
  "payload": {
    "error": "Error message",
    "context": "ergon"
  }
}
```

## API Parameter Reference

### Context IDs

The LLM Adapter supports different context IDs that determine the system prompt used:

| Context ID | Description | System Prompt |
|------------|-------------|---------------|
| `ergon` | Ergon AI assistant | Specializes in agent creation, automation, and tool configuration |
| `awt-team` | Advanced Workflow Team assistant | Specializes in workflow automation and process design |
| `agora` | Multi-component AI assistant | Coordinates between different AI systems |
| `default` | Default assistant | General-purpose assistant |

### LLM Options

Options that can be passed in the `options` object:

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `model` | string | `claude-3-sonnet-20240229` | The model to use |
| `temperature` | number | `0.7` | Controls randomness (0.0 to 1.0) |
| `max_tokens` | number | `4000` | Maximum tokens in the response |

### Available Models

#### Anthropic Claude Models

| Model ID | Display Name | Notes |
|----------|--------------|-------|
| `claude-3-sonnet-20240229` | Claude 3 Sonnet | Default model |
| `claude-3-opus-20240229` | Claude 3 Opus | Most capable model |
| `claude-3-haiku-20240307` | Claude 3 Haiku | Fastest model |

#### Simulated Models

| Model ID | Display Name | Notes |
|----------|--------------|-------|
| `simulated-fast` | Fast Simulation | Quick simulated responses |
| `simulated-standard` | Standard Simulation | Standard simulated responses |

## Error Handling

### HTTP Error Codes

| Status Code | Description |
|-------------|-------------|
| 200 | Success |
| 400 | Bad Request - Invalid parameters |
| 401 | Unauthorized - API key issues |
| 403 | Forbidden - Access denied |
| 404 | Not Found - Endpoint doesn't exist |
| 500 | Internal Server Error - Server-side error |

### WebSocket Error Handling

WebSocket errors are communicated through `ERROR` type messages with details in the payload.

### Common Error Scenarios

| Error | Possible Causes | Solution |
|-------|----------------|----------|
| API key error | Invalid or missing ANTHROPIC_API_KEY | Check environment variable |
| Connection refused | Server not running | Start the server |
| Timeout | Request took too long | Check network, increase timeout |
| Invalid request | Malformed message | Check message format |

## Usage Examples

### HTTP API Examples

#### curl Example

```bash
# Health check
curl http://localhost:8003/health

# Send a message
curl -X POST http://localhost:8003/api/message \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello", "context_id": "ergon", "streaming": false}'
```

#### Python Example

```python
import requests

# Base URL
base_url = "http://localhost:8003"

# Health check
response = requests.get(f"{base_url}/health")
print(response.json())

# Send a message
data = {
    "message": "Hello, how are you?",
    "context_id": "ergon",
    "streaming": False,
    "options": {
        "temperature": 0.7
    }
}
response = requests.post(f"{base_url}/api/message", json=data)
print(response.json())
```

### WebSocket Examples

#### JavaScript Example

```javascript
// Create WebSocket connection
const socket = new WebSocket('ws://localhost:8003/ws');

// Connection opened
socket.addEventListener('open', (event) => {
    console.log('Connected to LLM Adapter');
    
    // Send a message
    const request = {
        type: 'LLM_REQUEST',
        source: 'UI',
        target: 'LLM',
        timestamp: new Date().toISOString(),
        payload: {
            message: 'Hello, how are you?',
            context: 'ergon',
            streaming: true,
            options: {
                temperature: 0.7
            }
        }
    };
    
    socket.send(JSON.stringify(request));
});

// Listen for messages
socket.addEventListener('message', (event) => {
    const data = JSON.parse(event.data);
    
    if (data.type === 'UPDATE' && data.payload.chunk) {
        // Handle streaming chunk
        process.stdout.write(data.payload.chunk);
    } else if (data.type === 'UPDATE' && data.payload.done) {
        // Handle stream completion
        console.log('\nStream complete');
    } else if (data.type === 'RESPONSE') {
        // Handle complete message
        console.log('\nResponse:', data.payload.message);
    } else if (data.type === 'ERROR') {
        // Handle error
        console.error('Error:', data.payload.error);
    }
});

// Connection closed
socket.addEventListener('close', (event) => {
    console.log('Connection closed');
});

// Connection error
socket.addEventListener('error', (event) => {
    console.error('WebSocket error:', event);
});
```

#### Python Example

```python
import asyncio
import json
import websockets

async def send_message():
    uri = "ws://localhost:8003/ws"
    
    async with websockets.connect(uri) as websocket:
        # Send LLM request
        request = {
            "type": "LLM_REQUEST",
            "source": "TEST",
            "target": "LLM",
            "timestamp": "",
            "payload": {
                "message": "Hello, how are you?",
                "context": "ergon",
                "streaming": True,
                "options": {
                    "temperature": 0.7
                }
            }
        }
        
        await websocket.send(json.dumps(request))
        
        # Receive responses
        while True:
            response = await websocket.recv()
            data = json.loads(response)
            
            if data.get("type") == "UPDATE" and data.get("payload", {}).get("chunk"):
                # Print chunk
                print(data["payload"]["chunk"], end="", flush=True)
            elif data.get("type") == "UPDATE" and data.get("payload", {}).get("done"):
                # Stream complete
                print("\nStream complete")
                break
            elif data.get("type") == "ERROR"):
                # Error response
                print(f"\nError: {data.get('payload', {}).get('error')}")
                break
            elif data.get("type") == "RESPONSE"):
                # Complete message
                print(f"\nResponse: {data.get('payload', {}).get('message', '')}")
                break

asyncio.run(send_message())
```

## Rate Limiting and Performance

### Rate Limits

The LLM Adapter inherits rate limits from the underlying Anthropic API:

- Standard rate limits apply to Anthropic API requests
- No additional rate limiting is implemented in the adapter itself

### Performance Considerations

- **Concurrent Connections**: The adapter can handle multiple concurrent WebSocket connections
- **Memory Usage**: Higher with multiple streaming connections
- **CPU Usage**: Primarily dependent on server load and number of active connections
- **Network Bandwidth**: Scales with the number of streaming responses

## Version History

| Version | Changes |
|---------|---------|
| 0.1.0 | Initial implementation |

## Future API Enhancements

Planned enhancements for future versions:

1. **Authentication**: Token-based authentication for secure access
2. **Metrics Endpoints**: Performance and usage statistics
3. **Conversation History**: Endpoints for retrieving past conversations
4. **Batch Processing**: Support for processing multiple messages
5. **Model Switching**: Dynamic switching between different LLM providers
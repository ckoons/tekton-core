# LLMAdapter API Reference

## Overview

The LLMAdapter provides a unified API for communicating with various LLM providers. This document details the API endpoints, parameters, and response formats for integrating with the LLMAdapter service.

## Base URL

All API endpoints are relative to the base URL:

```
http://localhost:8004
```

## Authentication

Authentication is done via API keys in the Authorization header:

```
Authorization: Bearer YOUR_API_KEY
```

To obtain an API key, contact the system administrator or generate one through the administration interface.

## Common HTTP Status Codes

| Status Code | Description |
|-------------|-------------|
| 200 | Success |
| 400 | Bad Request - Invalid parameters |
| 401 | Unauthorized - Invalid or missing API key |
| 404 | Not Found - Resource does not exist |
| 429 | Too Many Requests - Rate limit exceeded |
| 500 | Internal Server Error - Server-side error |
| 503 | Service Unavailable - LLM provider is unavailable |

## API Endpoints

### LLM Provider Information

#### Get Available Providers

```
GET /api/providers
```

**Description:** Returns a list of all available LLM providers.

**Response:**
```json
{
  "providers": [
    {
      "id": "openai",
      "name": "OpenAI",
      "isAvailable": true,
      "models": [
        {
          "id": "gpt-4",
          "name": "GPT-4",
          "context_length": 8192,
          "isAvailable": true
        },
        {
          "id": "gpt-3.5-turbo",
          "name": "GPT-3.5 Turbo",
          "context_length": 4096,
          "isAvailable": true
        }
      ]
    },
    {
      "id": "anthropic",
      "name": "Anthropic",
      "isAvailable": true,
      "models": [
        {
          "id": "claude-3-opus",
          "name": "Claude 3 Opus",
          "context_length": 200000,
          "isAvailable": true
        },
        {
          "id": "claude-3-sonnet",
          "name": "Claude 3 Sonnet",
          "context_length": 200000,
          "isAvailable": true
        },
        {
          "id": "claude-3-haiku",
          "name": "Claude 3 Haiku",
          "context_length": 200000,
          "isAvailable": true
        }
      ]
    }
  ]
}
```

#### Get Provider Details

```
GET /api/providers/{provider_id}
```

**Description:** Returns detailed information about a specific provider.

**Parameters:**
- `provider_id` (path parameter): The ID of the provider (e.g., "openai", "anthropic")

**Response:**
```json
{
  "id": "openai",
  "name": "OpenAI",
  "isAvailable": true,
  "supportsStreaming": true,
  "supportsImageInput": true,
  "models": [
    {
      "id": "gpt-4",
      "name": "GPT-4",
      "context_length": 8192,
      "isAvailable": true,
      "capabilities": ["text-generation", "code-generation", "reasoning"]
    },
    {
      "id": "gpt-3.5-turbo",
      "name": "GPT-3.5 Turbo",
      "context_length": 4096,
      "isAvailable": true,
      "capabilities": ["text-generation", "code-generation", "reasoning"]
    }
  ],
  "usage": {
    "daily_tokens": 150000,
    "daily_limit": 500000,
    "monthly_tokens": 2500000,
    "monthly_limit": 5000000
  }
}
```

#### Get Model Details

```
GET /api/models/{model_id}
```

**Description:** Returns detailed information about a specific model.

**Parameters:**
- `model_id` (path parameter): The ID of the model (e.g., "gpt-4", "claude-3-opus")

**Response:**
```json
{
  "id": "gpt-4",
  "name": "GPT-4",
  "provider": "openai",
  "context_length": 8192,
  "isAvailable": true,
  "capabilities": ["text-generation", "code-generation", "reasoning"],
  "parameters": {
    "temperature": {
      "type": "float",
      "default": 0.7,
      "minimum": 0.0,
      "maximum": 2.0,
      "description": "Controls randomness. Higher values produce more creative outputs."
    },
    "top_p": {
      "type": "float",
      "default": 1.0,
      "minimum": 0.0,
      "maximum": 1.0,
      "description": "Controls diversity via nucleus sampling."
    },
    "max_tokens": {
      "type": "integer",
      "default": 256,
      "minimum": 1,
      "maximum": 4096,
      "description": "Maximum number of tokens to generate."
    }
  },
  "pricing": {
    "input_per_1k_tokens": 0.03,
    "output_per_1k_tokens": 0.06,
    "currency": "USD"
  },
  "performance": {
    "average_response_time_ms": 1200,
    "uptime_percent": 99.95
  }
}
```

### Completion Endpoints

#### Generate Completion

```
POST /api/completions
```

**Description:** Generates a completion for the given prompt.

**Request Body:**
```json
{
  "model": "gpt-4",
  "prompt": "Write a short poem about artificial intelligence.",
  "parameters": {
    "temperature": 0.7,
    "max_tokens": 256,
    "top_p": 1.0,
    "frequency_penalty": 0.0,
    "presence_penalty": 0.0
  }
}
```

**Response:**
```json
{
  "id": "comp_12345abcde",
  "object": "completion",
  "created": 1683123456,
  "model": "gpt-4",
  "content": "Silicon dreams in neural space,\nLines of code with human grace.\nThinking faster than light can travel,\nDigital minds that time unravel.\n\nLearning patterns, growing wise,\nArtificial, yet still alive.\nPartner in our shared tomorrow,\nA new intelligence we follow.",
  "usage": {
    "prompt_tokens": 8,
    "completion_tokens": 64,
    "total_tokens": 72
  },
  "finish_reason": "stop"
}
```

#### Generate Chat Completion

```
POST /api/chat/completions
```

**Description:** Generates a chat completion for the given messages.

**Request Body:**
```json
{
  "model": "claude-3-sonnet",
  "messages": [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What are the key benefits of using containerization in software development?"}
  ],
  "parameters": {
    "temperature": 0.7,
    "max_tokens": 1024,
    "top_p": 0.9
  }
}
```

**Response:**
```json
{
  "id": "chat_67890fghij",
  "object": "chat.completion",
  "created": 1683123789,
  "model": "claude-3-sonnet",
  "content": "The key benefits of using containerization in software development include:\n\n1. **Consistency across environments**: Containers package applications with all their dependencies, ensuring they run the same way in every environment - from development to testing to production. This eliminates the \"it works on my machine\" problem.\n\n2. **Isolation**: Containers isolate applications from each other and from the underlying system, preventing conflicts between dependencies and libraries.\n\n3. **Portability**: Containerized applications can run on any platform that supports the container runtime, regardless of the underlying operating system.\n\n4. **Efficiency**: Containers share the host OS kernel and use resources more efficiently than traditional virtual machines, allowing more applications to run on the same hardware.\n\n5. **Scalability**: Containers can be easily scaled horizontally by running multiple instances, and orchestration tools like Kubernetes automate scaling based on demand.\n\n6. **Faster deployment**: Containers start in seconds, enabling rapid deployment, scaling, and recovery from failures.\n\n7. **DevOps enablement**: Containers support CI/CD pipelines, infrastructure as code, and other DevOps practices.\n\n8. **Microservices architecture**: Containers are ideal for microservices, allowing teams to develop, deploy, and scale services independently.\n\n9. **Version control**: Container images can be versioned, allowing easy rollbacks and tracking of application history.\n\n10. **Resource utilization**: Containers allow setting specific resource limits (CPU, memory), improving resource utilization and cost efficiency.",
  "usage": {
    "prompt_tokens": 34,
    "completion_tokens": 320,
    "total_tokens": 354
  },
  "finish_reason": "stop"
}
```

#### Stream Chat Completion

```
POST /api/chat/completions/stream
```

**Description:** Streams a chat completion for the given messages. Returns a stream of server-sent events.

**Request Body:**
```json
{
  "model": "gpt-4",
  "messages": [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Explain quantum computing in simple terms."}
  ],
  "parameters": {
    "temperature": 0.7,
    "max_tokens": 1024,
    "top_p": 0.9
  }
}
```

**Response:**
A stream of server-sent events containing chunks of the completion. Each chunk is a JSON object:

```
event: message
data: {"id":"chunk_1","content":"Quantum","index":0}

event: message
data: {"id":"chunk_2","content":" computing","index":1}

event: message
data: {"id":"chunk_3","content":" is","index":2}

...

event: done
data: {"id":"chat_abcde12345","usage":{"prompt_tokens":26,"completion_tokens":312,"total_tokens":338}}
```

### Multi-Modal Endpoints

#### Generate Image-to-Text Completion

```
POST /api/completions/image-to-text
```

**Description:** Generates a completion based on an image and optional text prompt.

**Request Body (multipart/form-data):**
- `model` (string): Model ID (must support image input)
- `image` (file): Image file
- `prompt` (string, optional): Text prompt to accompany the image
- `parameters` (JSON string, optional): Model parameters

**Response:**
```json
{
  "id": "imgcomp_12345abcde",
  "object": "image.completion",
  "created": 1683124567,
  "model": "gpt-4-vision",
  "content": "The image shows a futuristic cityscape with tall skyscrapers and flying vehicles. The architecture is characterized by curved, sleek designs with blue and purple lighting. It appears to be nighttime, with the city illuminated against a dark sky. There are elevated roadways connecting buildings, and what looks like holographic advertisements displayed on some structures. This depicts a common sci-fi vision of a future metropolis with advanced transportation and building technology.",
  "usage": {
    "prompt_tokens": 85,
    "completion_tokens": 102,
    "total_tokens": 187
  },
  "finish_reason": "stop"
}
```

### Embedding Endpoints

#### Generate Embeddings

```
POST /api/embeddings
```

**Description:** Generates embeddings for the provided text.

**Request Body:**
```json
{
  "model": "text-embedding-ada-002",
  "input": ["The food was delicious and the service was excellent.", "The room was clean but the bathroom was dirty."]
}
```

**Response:**
```json
{
  "object": "list",
  "data": [
    {
      "object": "embedding",
      "embedding": [0.0023064255, -0.009327292, ...],
      "index": 0
    },
    {
      "object": "embedding",
      "embedding": [0.0072067517, -0.007545293, ...],
      "index": 1
    }
  ],
  "model": "text-embedding-ada-002",
  "usage": {
    "prompt_tokens": 23,
    "total_tokens": 23
  }
}
```

### Status Endpoints

#### System Status

```
GET /api/status
```

**Description:** Returns the current status of the LLMAdapter system and its providers.

**Response:**
```json
{
  "status": "operational",
  "version": "1.2.3",
  "uptime": 259200,
  "providers": {
    "openai": {
      "status": "operational",
      "latency_ms": 240
    },
    "anthropic": {
      "status": "operational",
      "latency_ms": 320
    },
    "local": {
      "status": "operational",
      "latency_ms": 150
    },
    "cohere": {
      "status": "degraded",
      "latency_ms": 850
    }
  }
}
```

#### Health Check

```
GET /health
```

**Description:** Simple health check endpoint for monitoring and load balancers.

**Response:**
```json
{
  "status": "ok"
}
```

### Administration Endpoints

#### Generate API Key

```
POST /api/admin/keys
```

**Description:** Generates a new API key with specified permissions.

**Request Body:**
```json
{
  "name": "Service Account - Dashboard",
  "permissions": ["read:models", "create:completions"],
  "expires_at": "2026-01-01T00:00:00Z"
}
```

**Response:**
```json
{
  "key_id": "key_12345abcde",
  "key": "llma_sk_abcdefghijklmnopqrstuvwxyz",
  "name": "Service Account - Dashboard",
  "permissions": ["read:models", "create:completions"],
  "created_at": "2025-05-01T12:00:00Z",
  "expires_at": "2026-01-01T00:00:00Z"
}
```

#### List API Keys

```
GET /api/admin/keys
```

**Description:** Lists all API keys (admin access required).

**Response:**
```json
{
  "keys": [
    {
      "key_id": "key_12345abcde",
      "name": "Service Account - Dashboard",
      "permissions": ["read:models", "create:completions"],
      "created_at": "2025-05-01T12:00:00Z",
      "expires_at": "2026-01-01T00:00:00Z"
    },
    {
      "key_id": "key_67890fghij",
      "name": "Development Environment",
      "permissions": ["*"],
      "created_at": "2025-04-15T09:30:00Z",
      "expires_at": "2025-07-15T09:30:00Z"
    }
  ]
}
```

#### Revoke API Key

```
DELETE /api/admin/keys/{key_id}
```

**Description:** Revokes an API key (admin access required).

**Parameters:**
- `key_id` (path parameter): The ID of the API key to revoke

**Response:**
```json
{
  "key_id": "key_12345abcde",
  "status": "revoked"
}
```

## WebSocket API

The LLMAdapter also provides a WebSocket API for real-time communication.

### WebSocket Connection

Connect to the WebSocket endpoint:

```
ws://localhost:8004/ws
```

Authentication is done with an API key query parameter:

```
ws://localhost:8004/ws?api_key=YOUR_API_KEY
```

### Message Format

All messages sent and received through the WebSocket connection must follow this JSON format:

```json
{
  "type": "command_name",
  "id": "request_123",
  "data": {}
}
```

### Supported Commands

#### chat.completion

Generate a chat completion.

**Client Message:**
```json
{
  "type": "chat.completion",
  "id": "req_123456",
  "data": {
    "model": "gpt-4",
    "messages": [
      {"role": "system", "content": "You are a helpful assistant."},
      {"role": "user", "content": "What are three interesting facts about the moon?"}
    ],
    "parameters": {
      "temperature": 0.7,
      "max_tokens": 512
    }
  }
}
```

**Server Response (progressive chunks):**
```json
{
  "type": "chat.completion.chunk",
  "id": "req_123456",
  "data": {
    "chunk_id": "chunk_1",
    "content": "Here",
    "index": 0
  }
}
```

```json
{
  "type": "chat.completion.chunk",
  "id": "req_123456",
  "data": {
    "chunk_id": "chunk_2",
    "content": " are",
    "index": 1
  }
}
```

**Final chunk:**
```json
{
  "type": "chat.completion.done",
  "id": "req_123456",
  "data": {
    "completion_id": "comp_abcde12345",
    "usage": {
      "prompt_tokens": 29,
      "completion_tokens": 156,
      "total_tokens": 185
    }
  }
}
```

#### cancel

Cancel an ongoing completion.

**Client Message:**
```json
{
  "type": "cancel",
  "id": "cancel_req_123456",
  "data": {
    "request_id": "req_123456"
  }
}
```

**Server Response:**
```json
{
  "type": "cancel.result",
  "id": "cancel_req_123456",
  "data": {
    "request_id": "req_123456",
    "status": "cancelled"
  }
}
```

## Error Handling

### Error Response Format

All API errors follow this JSON format:

```json
{
  "error": {
    "code": "error_code",
    "message": "Human-readable error message",
    "type": "error_type",
    "param": "parameter_name",
    "request_id": "req_123456abcdef"
  }
}
```

### Common Error Codes

| Code | Description |
|------|-------------|
| `invalid_request_error` | The request was malformed or missing required parameters |
| `authentication_error` | Invalid or expired API key |
| `permission_denied` | API key does not have permission for the requested operation |
| `rate_limit_exceeded` | Request rate limit has been exceeded |
| `model_not_found` | The requested model does not exist |
| `provider_not_available` | The requested provider is currently unavailable |
| `content_filter` | The request was flagged by content filters |
| `context_length_exceeded` | The input exceeded the model's context length |
| `server_error` | An unexpected error occurred on the server |
| `timeout` | The request timed out |

## Pagination

For endpoints that return lists of objects, pagination is supported with the following parameters:

- `limit`: Maximum number of objects to return (default: 20, max: 100)
- `offset`: Number of objects to skip (default: 0)
- `cursor`: Cursor for pagination (used instead of offset for efficient pagination)

Example request:
```
GET /api/completions?limit=10&offset=20
```

Paginated response format:
```json
{
  "data": [...],
  "pagination": {
    "total": 45,
    "limit": 10,
    "offset": 20,
    "has_more": true,
    "next_cursor": "cursor_abcdef123456"
  }
}
```

## Rate Limiting

The API implements rate limiting to ensure fair usage. Rate limits are applied per API key and are reset on a per-minute, per-hour, and per-day basis.

Rate limit headers are included in API responses:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1683129600
```

## Versioning

The API version can be specified in the request header:

```
X-API-Version: 2023-05-01
```

If not specified, the latest stable version will be used.

## Conclusion

This API reference covers the core functionality of the LLMAdapter service. For additional support or advanced use cases, please refer to the [Technical Documentation](./TECHNICAL_DOCUMENTATION.md) and [Integration Guide](./INTEGRATION.md).
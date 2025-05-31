# LLMAdapter User Guide

## Introduction

LLMAdapter is the central interface for Large Language Model interactions within the Tekton ecosystem. It provides a standardized way to interact with multiple LLM providers, handling authentication, model selection, streaming, and failover mechanisms. This guide will help you get started with LLMAdapter and learn how to effectively utilize its capabilities.

## Getting Started

### Installation

1. Ensure you have Python 3.9+ installed
2. Clone the LLMAdapter repository:
   ```bash
   git clone git@github.com:yourusername/Tekton.git
   cd Tekton/LLMAdapter
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Start the LLMAdapter server:
   ```bash
   python -m llm_adapter.server
   ```

By default, LLMAdapter runs on port 8004. You can change this by setting the `LLM_ADAPTER_PORT` environment variable.

### Basic Configuration

Create a configuration file named `config.json` in the LLMAdapter directory:

```json
{
  "server": {
    "host": "0.0.0.0",
    "port": 8004
  },
  "providers": [
    {
      "name": "openai",
      "type": "openai",
      "api_key": "YOUR_OPENAI_API_KEY",
      "enabled": true
    },
    {
      "name": "anthropic",
      "type": "anthropic",
      "api_key": "YOUR_ANTHROPIC_API_KEY",
      "enabled": true
    },
    {
      "name": "local",
      "type": "local",
      "model_path": "/path/to/local/model",
      "enabled": true
    }
  ],
  "cache": {
    "enabled": true,
    "max_size": 1000,
    "ttl_seconds": 3600
  },
  "rate_limits": {
    "default": {
      "minute": 100,
      "hour": 1000,
      "day": 10000
    },
    "embeddings": {
      "minute": 200,
      "hour": 2000,
      "day": 20000
    }
  }
}
```

Alternatively, you can use environment variables for configuration:

```bash
export LLM_ADAPTER_PORT=8004
export OPENAI_API_KEY=your_api_key
export ANTHROPIC_API_KEY=your_api_key
export ENABLE_CACHE=true
```

## Using the API

### Discovering Available Models

First, check which providers and models are available:

```bash
curl http://localhost:8004/api/providers
```

Response:
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
        }
      ]
    }
  ]
}
```

### Generating Completions

To generate a text completion with a specific model:

```bash
curl -X POST http://localhost:8004/api/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4",
    "messages": [
      {"role": "system", "content": "You are a helpful assistant."},
      {"role": "user", "content": "What is the capital of France?"}
    ],
    "parameters": {
      "temperature": 0.7,
      "max_tokens": 256
    }
  }'
```

Response:
```json
{
  "id": "chat_12345abcde",
  "object": "chat.completion",
  "created": 1683123456,
  "model": "gpt-4",
  "content": "The capital of France is Paris. Paris is located in the north-central part of the country on the Seine River and is known for landmarks like the Eiffel Tower, the Louvre Museum, and Notre-Dame Cathedral.",
  "usage": {
    "prompt_tokens": 27,
    "completion_tokens": 45,
    "total_tokens": 72
  },
  "finish_reason": "stop"
}
```

### Python Client Example

Here's a simple Python client for interacting with LLMAdapter:

```python
import requests
import json

class LLMAdapterClient:
    def __init__(self, base_url="http://localhost:8004", api_key=None):
        self.base_url = base_url
        self.api_key = api_key
        self.headers = {
            "Content-Type": "application/json"
        }
        
        if api_key:
            self.headers["Authorization"] = f"Bearer {api_key}"
            
    def get_providers(self):
        """Get available providers"""
        response = requests.get(
            f"{self.base_url}/api/providers",
            headers=self.headers
        )
        return response.json()
        
    def get_models(self):
        """Get available models"""
        providers = self.get_providers()
        models = []
        
        for provider in providers["providers"]:
            for model in provider["models"]:
                model["provider"] = provider["id"]
                models.append(model)
                
        return models
        
    def generate_completion(self, prompt, model="gpt-3.5-turbo", parameters=None):
        """Generate a completion for a prompt"""
        params = parameters or {
            "temperature": 0.7,
            "max_tokens": 256
        }
        
        payload = {
            "model": model,
            "prompt": prompt,
            "parameters": params
        }
        
        response = requests.post(
            f"{self.base_url}/api/completions",
            headers=self.headers,
            json=payload
        )
        
        return response.json()
        
    def generate_chat_completion(self, messages, model="gpt-3.5-turbo", parameters=None):
        """Generate a chat completion"""
        params = parameters or {
            "temperature": 0.7,
            "max_tokens": 256
        }
        
        payload = {
            "model": model,
            "messages": messages,
            "parameters": params
        }
        
        response = requests.post(
            f"{self.base_url}/api/chat/completions",
            headers=self.headers,
            json=payload
        )
        
        return response.json()

# Usage example
client = LLMAdapterClient()

# List available models
models = client.get_models()
for model in models:
    print(f"{model['id']} ({model['provider']})")

# Generate chat completion
response = client.generate_chat_completion(
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is the capital of France?"}
    ],
    model="gpt-4"
)

print(f"Response: {response['content']}")
```

## Streaming Responses

### WebSocket Streaming

For streaming responses, use the WebSocket API:

```javascript
// JavaScript WebSocket example
const socket = new WebSocket('ws://localhost:8004/ws');

socket.onopen = function(event) {
  console.log('Connected to LLMAdapter');
  
  // Send chat completion request
  socket.send(JSON.stringify({
    type: 'chat.completion',
    id: 'req_123456',
    data: {
      model: 'gpt-4',
      messages: [
        {role: 'system', content: 'You are a helpful assistant.'},
        {role: 'user', content: 'Write a short story about a robot discovering emotions.'}
      ],
      parameters: {
        temperature: 0.8,
        max_tokens: 1024
      }
    }
  }));
};

// Handle incoming messages
socket.onmessage = function(event) {
  const message = JSON.parse(event.data);
  
  if (message.type === 'chat.completion.chunk') {
    // Display chunk
    process.stdout.write(message.data.content);
  } else if (message.type === 'chat.completion.done') {
    // Completion finished
    console.log('\nCompletion finished!');
    console.log('Total tokens:', message.data.usage.total_tokens);
  } else if (message.type === 'error') {
    // Handle error
    console.error('Error:', message.data.message);
  }
};

// Handle connection close
socket.onclose = function(event) {
  console.log('Connection closed');
};
```

### Python WebSocket Client

Here's a Python client for WebSocket streaming:

```python
import asyncio
import websockets
import json
import sys

async def stream_completion():
    uri = "ws://localhost:8004/ws"
    
    async with websockets.connect(uri) as websocket:
        # Send chat completion request
        await websocket.send(json.dumps({
            "type": "chat.completion",
            "id": "req_123456",
            "data": {
                "model": "claude-3-sonnet",
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Write a short poem about artificial intelligence."}
                ],
                "parameters": {
                    "temperature": 0.8,
                    "max_tokens": 512
                }
            }
        }))
        
        # Process streaming response
        while True:
            response = await websocket.recv()
            message = json.loads(response)
            
            if message["type"] == "chat.completion.chunk":
                # Print chunk without newline
                sys.stdout.write(message["data"]["content"])
                sys.stdout.flush()
            elif message["type"] == "chat.completion.done":
                # Completion finished
                print("\n\nCompletion finished!")
                print(f"Total tokens: {message['data']['usage']['total_tokens']}")
                break
            elif message["type"] == "error":
                # Handle error
                print(f"\nError: {message['data']['message']}")
                break

# Run the async function
asyncio.run(stream_completion())
```

## Working with Multiple Providers

LLMAdapter makes it easy to work with multiple LLM providers.

### Provider Selection

You can select a specific provider by choosing the appropriate model ID:

```python
# Using OpenAI
response = client.generate_chat_completion(
    messages=[
        {"role": "user", "content": "What is the capital of France?"}
    ],
    model="gpt-4"  # OpenAI model
)

# Using Anthropic
response = client.generate_chat_completion(
    messages=[
        {"role": "user", "content": "What is the capital of France?"}
    ],
    model="claude-3-opus"  # Anthropic model
)

# Using local model
response = client.generate_chat_completion(
    messages=[
        {"role": "user", "content": "What is the capital of France?"}
    ],
    model="local-llama"  # Local model
)
```

### Automatic Failover

LLMAdapter provides automatic failover between providers:

```python
# If the primary provider (OpenAI) is unavailable, 
# it will automatically try the next compatible provider (Anthropic)
response = client.generate_chat_completion(
    messages=[
        {"role": "user", "content": "What is the capital of France?"}
    ],
    model="gpt-4"
)
```

## Advanced Features

### Image-to-Text Processing

For models that support image input:

```python
import requests
import json
import base64

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# API endpoint
url = "http://localhost:8004/api/completions/image-to-text"

# Prepare the request
headers = {
    "Content-Type": "application/json"
}

payload = {
    "model": "gpt-4-vision",
    "prompt": "What's in this image?",
    "image": encode_image("path/to/your/image.jpg"),
    "parameters": {
        "temperature": 0.7,
        "max_tokens": 300
    }
}

# Send the request
response = requests.post(url, headers=headers, json=payload)
print(response.json()["content"])
```

### Generating Embeddings

For text embeddings:

```python
import requests
import json

# API endpoint
url = "http://localhost:8004/api/embeddings"

# Prepare the request
headers = {
    "Content-Type": "application/json"
}

payload = {
    "model": "text-embedding-ada-002",
    "input": [
        "The food was delicious and the service was excellent.",
        "The room was clean but the bathroom was dirty."
    ]
}

# Send the request
response = requests.post(url, headers=headers, json=payload)
embeddings = response.json()["data"]

# First embedding vector
first_embedding = embeddings[0]["embedding"]
print(f"First embedding has {len(first_embedding)} dimensions")
```

### Batch Processing

For processing multiple queries efficiently:

```python
import requests
import json

# API endpoint
url = "http://localhost:8004/api/chat/completions/batch"

# Prepare the request
headers = {
    "Content-Type": "application/json"
}

payload = {
    "model": "gpt-3.5-turbo",
    "batch": [
        {
            "messages": [
                {"role": "user", "content": "What is the capital of France?"}
            ]
        },
        {
            "messages": [
                {"role": "user", "content": "What is the capital of Italy?"}
            ]
        },
        {
            "messages": [
                {"role": "user", "content": "What is the capital of Spain?"}
            ]
        }
    ],
    "parameters": {
        "temperature": 0.7,
        "max_tokens": 50
    }
}

# Send the request
response = requests.post(url, headers=headers, json=payload)
results = response.json()["results"]

for i, result in enumerate(results):
    print(f"Query {i+1}: {result['content']}")
```

## Integration with Tekton Components

### Using LLMAdapter in Tekton Components

Here's an example of how to integrate LLMAdapter with other Tekton components:

```python
from tekton_llm_client import TektonLLMClient

# Initialize the client
llm_client = TektonLLMClient(base_url="http://localhost:8004")

# Check if LLMAdapter is available
if llm_client.is_available():
    # Generate a completion
    response = llm_client.generate_chat_completion(
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What is the capital of France?"}
        ],
        model="gpt-4"
    )
    
    print(response.content)
else:
    print("LLMAdapter is not available")
```

### Using the JavaScript Client

For frontend components:

```javascript
// Import the Tekton LLM client
import { TektonLLMClient } from '/ui/scripts/tekton-llm-client.js';

// Initialize the client with environment configuration
const llmClient = new TektonLLMClient({
  baseUrl: window.env.LLM_ADAPTER_URL || 'http://localhost:8004'
});

// Generate a completion
async function generateCompletion() {
  try {
    const response = await llmClient.generateChatCompletion({
      model: 'gpt-3.5-turbo',
      messages: [
        {role: 'system', content: 'You are a helpful assistant.'},
        {role: 'user', content: 'What is the capital of France?'}
      ],
      parameters: {
        temperature: 0.7,
        max_tokens: 100
      }
    });
    
    console.log('Response:', response.content);
    return response.content;
  } catch (error) {
    console.error('Error generating completion:', error);
    return null;
  }
}

// Stream a completion
async function streamCompletion(onChunk) {
  try {
    const stream = await llmClient.streamChatCompletion({
      model: 'claude-3-sonnet',
      messages: [
        {role: 'system', content: 'You are a helpful assistant.'},
        {role: 'user', content: 'Write a short story about a robot discovering emotions.'}
      ],
      parameters: {
        temperature: 0.8,
        max_tokens: 1000
      }
    });
    
    // Process stream chunks
    for await (const chunk of stream) {
      onChunk(chunk.content);
    }
    
    return true;
  } catch (error) {
    console.error('Error streaming completion:', error);
    return false;
  }
}

// Usage example
const outputElement = document.getElementById('output');
streamCompletion((chunk) => {
  outputElement.textContent += chunk;
});
```

## Single Port Integration

LLMAdapter follows the Tekton Single Port Architecture for consistent component communication.

### URL Structure

```
http://localhost:8004/
  ├── api/                     # HTTP API endpoints
  │   ├── providers            # Provider info
  │   ├── models               # Model info
  │   ├── completions          # Completion endpoints
  │   └── chat/completions     # Chat completion endpoints
  ├── ws/                      # WebSocket endpoint
  └── health                   # Health check endpoint
```

### Environment Configuration

Configure the LLMAdapter URL in your environment:

```bash
export LLM_ADAPTER_URL=http://localhost:8004
```

In JavaScript:

```javascript
// env.js
window.env = {
  LLM_ADAPTER_URL: 'http://localhost:8004',
  // other environment variables
};
```

## Troubleshooting

### Common Issues

1. **Connection Refused**
   - Check that the LLMAdapter server is running
   - Verify the port configuration (default is 8004)
   - Ensure network connectivity between client and server

2. **Authentication Errors**
   - Check that your API key is valid
   - Verify the API key has the necessary permissions
   - Ensure the API key is correctly passed in the Authorization header

3. **Provider Unavailable**
   - Check that the provider's API key is valid
   - Verify the provider's service status
   - Check the LLMAdapter logs for provider connection issues

4. **Rate Limiting**
   - Reduce request frequency
   - Implement backoff and retry logic
   - Consider increasing rate limits in configuration

### Checking System Status

Check the LLMAdapter status:

```bash
curl http://localhost:8004/api/status
```

Response:
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
    }
  }
}
```

### Enabling Debug Logging

To enable debug logging:

```bash
export LOG_LEVEL=DEBUG
python -m llm_adapter.server
```

### Common Error Codes

| Code | Description | Solution |
|------|-------------|----------|
| `invalid_request_error` | The request was malformed | Check your request format and parameters |
| `authentication_error` | Invalid API key | Verify your API key |
| `permission_denied` | Insufficient permissions | Request additional permissions for your API key |
| `rate_limit_exceeded` | Too many requests | Reduce request frequency or implement retry logic |
| `model_not_found` | Model doesn't exist | Check the list of available models |
| `provider_not_available` | Provider is down | Try an alternative provider or model |
| `content_filter` | Content flagged by filters | Modify your request to comply with content policies |
| `context_length_exceeded` | Input too long | Reduce the size of your input |

## Best Practices

### Model Selection

1. **Match the model to the task**:
   - Use smaller models for simple tasks (gpt-3.5-turbo, claude-3-haiku)
   - Use powerful models for complex reasoning (gpt-4, claude-3-opus)
   - Use specialized models for specific tasks (embedding models, vision models)

2. **Consider cost and latency**:
   - Smaller models are faster and cheaper
   - Larger models provide better quality but with higher cost and latency

### Parameter Optimization

1. **Temperature setting**:
   - Lower (0.0-0.3): More deterministic, better for factual queries
   - Medium (0.4-0.7): Balanced creativity and coherence
   - Higher (0.8-1.0): More creative, varied outputs

2. **Token limits**:
   - Set reasonable `max_tokens` to control response length
   - Consider the model's context window size
   - Balance between thoroughness and efficiency

### Efficient Usage

1. **Use streaming for long responses**:
   - Improves perceived latency
   - Allows for early termination if necessary
   - Better user experience for chat interfaces

2. **Implement caching**:
   - Cache common queries to reduce API calls
   - Consider expiry time for time-sensitive information
   - Use request fingerprinting for effective cache keys

3. **Batch requests when possible**:
   - Use batch endpoints for multiple queries
   - Reduce overhead of multiple separate requests
   - Process results in parallel

### Error Handling

1. **Implement retry logic**:
   - Use exponential backoff for retries
   - Handle transient errors gracefully
   - Set reasonable timeout values

2. **Graceful degradation**:
   - Fall back to alternative models if primary is unavailable
   - Provide meaningful error messages to users
   - Have contingency for complete LLM unavailability

## Conclusion

This guide covers the basics of using LLMAdapter for LLM interactions. For more detailed information, check the [API Reference](./API_REFERENCE.md) and [Technical Documentation](./TECHNICAL_DOCUMENTATION.md).

If you encounter issues or need assistance, please refer to the [Tekton Documentation](../../README.md) for community support options.
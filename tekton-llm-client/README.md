# Tekton LLM Client

A unified client library for LLM integration in Tekton components.

## Overview

The `tekton-llm-client` package provides a standardized way to integrate with large language models (LLMs) in Tekton components. It uses the Rhetor component as the centralized LLM service, eliminating duplicate adapter implementations and providing consistent patterns across components.

## Installation

```bash
pip install tekton-llm-client
```

Or from the source code:

```bash
cd tekton-llm-client
pip install -e .
```

## Features

- Unified interface for LLM operations
- Support for synchronous and streaming responses
- HTTP and WebSocket protocols
- Built-in graceful degradation with fallbacks
- Comprehensive error handling
- Retry logic for reliability
- Token counting and optimization utilities
- JavaScript client for frontend components

## Usage

### Basic Usage

```python
import asyncio
from tekton_llm_client import TektonLLMClient

async def main():
    # Initialize the client
    client = TektonLLMClient(
        component_id="my-component",
        rhetor_url="http://localhost:8003"  # URL to your Rhetor service
    )
    
    # Initialize the connection
    await client.initialize()
    
    # Generate text
    response = await client.generate_text(
        prompt="What is the capital of France?",
        system_prompt="You are a helpful assistant that provides accurate information."
    )
    
    print(f"Response: {response.content}")
    
    # Clean up
    await client.shutdown()

# Run the async function
asyncio.run(main())
```

### Chat Conversation

```python
import asyncio
from tekton_llm_client import TektonLLMClient
from tekton_llm_client.models import Message, MessageRole

async def chat_example():
    # Initialize the client
    client = TektonLLMClient(component_id="my-component")
    await client.initialize()
    
    # Create a conversation
    messages = [
        Message(role=MessageRole.SYSTEM, content="You are a helpful assistant."),
        Message(role=MessageRole.USER, content="Hello, how are you?"),
        Message(role=MessageRole.ASSISTANT, content="I'm doing well! How can I help you today?"),
        Message(role=MessageRole.USER, content="What's the weather like in Paris?")
    ]
    
    # Get a response
    response = await client.generate_chat_response(messages=messages)
    
    print(f"Assistant: {response.content}")
    
    # Clean up
    await client.shutdown()

asyncio.run(chat_example())
```

### Streaming

```python
import asyncio
from tekton_llm_client import TektonLLMClient
from tekton_llm_client.models import StreamingChunk

async def streaming_example():
    # Initialize the client
    client = TektonLLMClient(component_id="my-component")
    await client.initialize()
    
    # Define a callback for streaming chunks
    def handle_chunk(chunk: StreamingChunk):
        print(chunk.chunk, end="", flush=True)
        if chunk.done:
            print("\n--- Streaming complete ---")
    
    # Stream a response
    prompt = "Write a short poem about artificial intelligence."
    
    print("Streaming response:\n")
    
    async for chunk in client.generate_text(
        prompt=prompt,
        streaming=True
    ):
        handle_chunk(chunk)
    
    # Clean up
    await client.shutdown()

asyncio.run(streaming_example())
```

### WebSocket Client

```python
import asyncio
from tekton_llm_client import TektonLLMWebSocketClient
from tekton_llm_client.models import StreamingChunk

async def websocket_example():
    # Initialize the WebSocket client
    client = TektonLLMWebSocketClient(
        component_id="my-component",
        on_message=lambda msg: print(f"Message received: {msg}"),
        on_error=lambda err: print(f"Error: {err}"),
        on_close=lambda: print("Connection closed")
    )
    
    # Connect to the server
    await client.connect()
    
    # Generate a response
    request_id = await client.generate(
        prompt="What is the meaning of life?",
        context_id="philosophy",
        callback=lambda chunk: print(chunk.chunk, end="", flush=True)
    )
    
    # Wait for a bit
    await asyncio.sleep(10)
    
    # Disconnect
    await client.disconnect()

asyncio.run(websocket_example())
```

### Advanced Features

```python
import asyncio
from tekton_llm_client import TektonLLMClient
from tekton_llm_client.utils import count_tokens, optimize_messages_for_token_limit

async def advanced_example():
    # Initialize the client
    client = TektonLLMClient(
        component_id="my-component",
        provider_id="anthropic",
        model_id="claude-3-sonnet-20240229",
        use_fallback=True  # Enable fallback if primary service is unavailable
    )
    await client.initialize()
    
    # Count tokens in text
    text = "This is a sample text that we'll count tokens for."
    token_count = count_tokens(text, model="claude-3-sonnet-20240229")
    print(f"Token count: {token_count}")
    
    # Create a long conversation
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Tell me about AI."},
        {"role": "assistant", "content": "Artificial Intelligence (AI) refers to systems designed to perform tasks that typically require human intelligence..."},
        # ... more messages ...
        {"role": "user", "content": "What are the ethical concerns?"}
    ]
    
    # Optimize for token limit
    optimized_messages = optimize_messages_for_token_limit(
        messages=messages,
        max_tokens=4000,
        model="claude-3-sonnet-20240229",
        keep_system_prompt=True
    )
    
    # Use optimized messages
    response = await client.generate_chat_response(
        messages=optimized_messages,
        options={
            "temperature": 0.5,
            "max_tokens": 1000,
            "fallback_provider": "simulated",  # Fallback provider if primary fails
            "retry_count": 2  # Number of retries on failure
        }
    )
    
    print(f"Response: {response.content}")
    
    # Clean up
    await client.shutdown()

asyncio.run(advanced_example())
```

## JavaScript Client

For frontend components, a JavaScript client is also provided. See the [JavaScript README](js/README.md) for more information.

## Error Handling

The client includes comprehensive error handling with specific exception types:

- `TektonLLMError`: Base exception for all client errors
- `ConnectionError`: Connection to the LLM service failed
- `TimeoutError`: Request timed out
- `AuthenticationError`: Authentication with the LLM service failed
- `ServiceUnavailableError`: LLM service is unavailable
- `RateLimitError`: Rate limit exceeded
- `InvalidRequestError`: Request was invalid
- `AdapterError`: Error with a specific LLM adapter
- `FallbackError`: All fallback options failed

Example:

```python
import asyncio
from tekton_llm_client import TektonLLMClient
from tekton_llm_client.exceptions import (
    TektonLLMError, ConnectionError, TimeoutError, 
    ServiceUnavailableError
)

async def error_handling_example():
    client = TektonLLMClient(component_id="my-component")
    
    try:
        await client.initialize()
        response = await client.generate_text("Hello, world!")
        print(f"Response: {response.content}")
    except ConnectionError:
        print("Failed to connect to the LLM service")
    except TimeoutError:
        print("Request timed out")
    except ServiceUnavailableError:
        print("LLM service is currently unavailable")
    except TektonLLMError as e:
        print(f"LLM error: {str(e)}")
    finally:
        await client.shutdown()

asyncio.run(error_handling_example())
```

## Environment Variables

The client uses these environment variables if set:

- `RHETOR_URL`: URL for the Rhetor API (default: `http://localhost:8003`)
- `RHETOR_WS_URL`: WebSocket URL for Rhetor (default: derived from `RHETOR_URL`)
- `RHETOR_DEFAULT_PROVIDER`: Default provider ID (default: `anthropic`)
- `RHETOR_DEFAULT_MODEL`: Default model ID
- `RHETOR_AUTH_TOKEN`: Authentication token for Rhetor API
- `RHETOR_TIMEOUT`: Default timeout in seconds (default: `30`)
- `RHETOR_MAX_RETRIES`: Default number of retries (default: `3`)

## License

MIT
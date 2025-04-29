# LLM Adapter Technical Documentation

## Overview

The LLM Adapter is a lightweight component in the Tekton ecosystem that serves as a bridge between the Hephaestus UI terminal interface and Language Model APIs, specifically Anthropic's Claude. It provides both HTTP and WebSocket interfaces for communication, allowing for synchronous requests and asynchronous streaming responses.

This adapter is designed as an interim solution to enable testing of terminal-to-LLM communication before the full Rhetor component is implemented, with an architecture that facilitates future replacement.

## Architecture

The LLM Adapter follows a layered architecture:

1. **Server Layer**: Handles HTTP and WebSocket connections
   - HTTP Server: REST API endpoints for non-streaming requests
   - WebSocket Server: Real-time communication for streaming responses

2. **Client Layer**: Interfaces with external LLM APIs
   - Claude Client: Communicates with Anthropic's API
   - Simulated Client: Provides fallback responses when API is unavailable

3. **Configuration Layer**: Manages environment variables and settings
   - API Keys: Securely manages authentication credentials
   - System Prompts: Context-specific prompts for different use cases
   - Port Configuration: Follows Tekton's Single Port Architecture

## Integration with Tekton

The LLM Adapter integrates with the Tekton system through:

1. **Hephaestus UI**:
   - Connects via WebSocket for real-time communication
   - Automatically establishes a connection when the Ergon tab is selected
   - Handles streaming responses for natural conversation flow

2. **Single Port Architecture**:
   - Uses the standardized Rhetor port (8003) by default
   - Path-based routing for different types of requests
   - Environment variable support for flexible configuration

## Component Structure

### Files Organization

```
LLMAdapter/
├── __main__.py                 # Entry point for running as a module
├── IMPLEMENTATION_SUMMARY.md   # Implementation details and files created
├── INTEGRATION.md              # Guide for integrating with Hephaestus
├── README.md                   # Overview and usage instructions
├── hephaestus_config.js        # Configuration for Hephaestus integration
├── requirements.txt            # Python dependencies
├── test_adapter.py             # Test script for the adapter
└── llm_adapter/               # Core implementation package
    ├── __init__.py            # Package initialization
    ├── config.py              # Configuration and environment variables
    ├── http_server.py         # HTTP API implementation
    ├── llm_client.py          # Client for LLM APIs (Claude)
    ├── server.py              # Main server module
    └── ws_server.py           # WebSocket server implementation
```

### Key Modules

#### 1. Server Module (`server.py`)

The central module that initializes and starts both HTTP and WebSocket servers:
- Configures logging
- Sets up the environment
- Starts the HTTP server in a separate thread
- Runs the WebSocket server in the main thread

#### 2. HTTP Server (`http_server.py`)

Implements a FastAPI-based HTTP server with the following endpoints:
- `/`: Root endpoint with basic information
- `/health`: Health check endpoint
- `/providers`: Endpoint to get available LLM providers and models
- `/provider`: Endpoint to set the active provider and model
- `/message`: Endpoint to send a message to the LLM
- `/stream`: Endpoint for streaming responses via Server-Sent Events

#### 3. WebSocket Server (`ws_server.py`)

Implements a WebSocket server for real-time communication:
- Manages client connections
- Handles LLM requests and streams responses
- Provides typing indicators and status updates
- Supports registration and status messages

#### 4. LLM Client (`llm_client.py`)

Interfaces with LLM APIs:
- Manages connection to Anthropic's Claude API
- Provides methods for both streaming and non-streaming completions
- Implements fallback to simulated responses when Claude is unavailable
- Exposes available providers and models

#### 5. Configuration (`config.py`)

Manages configuration through environment variables:
- API keys for LLM services
- Default model selection
- Server host and port settings
- Context-specific system prompts
- Default LLM options (max tokens, temperature)

## API Reference

### HTTP API

#### GET Endpoints

- **GET /** - Basic information about the adapter
  - Response: `{"name": "Tekton LLM Adapter", "version": "0.1.0", "status": "running", "endpoints": ["/message", "/stream", "/health"], "claude_available": true}`

- **GET /health** - Health check
  - Response: `{"status": "healthy", "version": "0.1.0", "claude_available": true, "providers": ["anthropic", "simulated"]}`

- **GET /providers** - Available LLM providers and models
  - Response: `{"providers": {...}, "current_provider": "anthropic", "current_model": "claude-3-sonnet-20240229"}`

#### POST Endpoints

- **POST /provider** - Set the active provider and model
  - Request Body: `{"provider_id": "anthropic", "model_id": "claude-3-sonnet-20240229"}`
  - Response: `{"success": true, "provider": "anthropic", "model": "claude-3-sonnet-20240229"}`

- **POST /message** - Send a message to the LLM
  - Request Body: `{"message": "Hello", "context_id": "ergon", "streaming": false, "options": {"temperature": 0.7}}`
  - Response: `{"message": "Hello! How can I help you today?", "context": "ergon", "model": "claude-3-sonnet-20240229", "finished": true, "timestamp": "2025-04-28T19:20:00.123456"}`

- **POST /stream** - Stream a response from the LLM
  - Request Body: `{"message": "Hello", "context_id": "ergon", "options": {"temperature": 0.7}}`
  - Response: Server-Sent Events with chunks of the response

### WebSocket API

The WebSocket interface accepts and returns JSON messages with the following structure:

#### Client-to-Server Messages

- **LLM Request**
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
        "temperature": 0.7
      }
    }
  }
  ```

- **Registration**
  ```json
  {
    "type": "REGISTER",
    "source": "UI",
    "timestamp": "2025-04-28T19:20:00.123456"
  }
  ```

- **Status Request**
  ```json
  {
    "type": "STATUS",
    "source": "UI",
    "timestamp": "2025-04-28T19:20:00.123456"
  }
  ```

#### Server-to-Client Messages

- **Chunk Update** (for streaming)
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

- **Stream Complete**
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

- **Complete Response** (for non-streaming)
  ```json
  {
    "type": "RESPONSE",
    "source": "ergon",
    "target": "UI",
    "timestamp": "2025-04-28T19:20:00.123456",
    "payload": {
      "message": "Hello! How can I help you today?",
      "context": "ergon"
    }
  }
  ```

- **Error Response**
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

## Configuration

The LLM Adapter is configured through environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `ANTHROPIC_API_KEY` | API key for Claude | (required for Claude) |
| `DEFAULT_MODEL` | Default Claude model | `claude-3-sonnet-20240229` |
| `HOST` | Host to bind to | `localhost` |
| `RHETOR_PORT` | Single Port Architecture port | `8003` |
| `HTTP_PORT` | HTTP port (falls back to `RHETOR_PORT`) | `8003` |

## Usage

### Running the Adapter

1. Install dependencies:
   ```bash
   cd LLMAdapter
   pip install -r requirements.txt
   ```

2. Set environment variables:
   ```bash
   export ANTHROPIC_API_KEY=your_api_key_here
   ```

3. Run the adapter:
   ```bash
   python3 -m llm_adapter
   ```

### Testing the Adapter

The `test_adapter.py` script provides a way to test the adapter:

```bash
./test_adapter.py --message "Hello, how are you?"
```

Options:
- `--host`: Host to connect to (default: localhost)
- `--http-port`: HTTP port (default: 8300)
- `--ws-port`: WebSocket port (default: 8301)
- `--message`: Message to send
- `--context`: Context ID (ergon, awt-team, agora)
- `--http`: Test HTTP interface (default is WebSocket)

## Integration with Hephaestus

The adapter is designed to easily integrate with the Hephaestus UI:

1. Include the `hephaestus_config.js` file in the Hephaestus UI
2. Update the `hermes-connector.js` file to connect to the LLM Adapter
3. Modify the UI to handle streaming responses

See the `INTEGRATION.md` file for detailed integration instructions.

## Future Plans

This adapter is an interim solution and will be replaced by the Rhetor component, which will provide:

1. More sophisticated prompt management
2. Context tracking and memory integration
3. Model selection logic
4. Evaluation and monitoring capabilities

The WebSocket and HTTP interfaces are designed to be compatible with Rhetor, allowing for a smooth transition.

## Troubleshooting

Common issues and solutions:

1. **Connection Refused**: Ensure the adapter is running and on the correct ports
2. **Authentication Error**: Check that the `ANTHROPIC_API_KEY` environment variable is set correctly
3. **No Response**: Verify that the WebSocket connection is established successfully
4. **Simulated Responses Only**: The adapter falls back to simulated responses when Claude is not available

## Known Limitations

1. Limited to Claude models from Anthropic
2. No persistent context or memory between requests
3. Basic error handling without retry mechanisms
4. Limited provider and model configuration options
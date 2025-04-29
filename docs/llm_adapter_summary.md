# LLM Adapter Technical Documentation

## Overview

This document provides a comprehensive guide to the LLM Adapter component of the Tekton system. The LLM Adapter serves as a bridge between the Hephaestus UI terminal interface and Language Model APIs, primarily Anthropic's Claude.

## Documentation Index

The complete LLM Adapter documentation consists of the following documents:

1. [**LLM Adapter Documentation**](llm_adapter_documentation.md): Comprehensive guide to the component
2. [**LLM Adapter Architecture**](llm_adapter_architecture.md): Visual diagrams and flow explanations
3. [**LLM Adapter Single Port Integration**](llm_adapter_single_port.md): Details on the Single Port Architecture
4. [**LLM Adapter API Reference**](llm_adapter_api_reference.md): Complete API documentation

## Key Features

- **HTTP and WebSocket Interfaces**: Provides both synchronous and streaming connections
- **Claude Integration**: Direct connection to Anthropic's Claude models
- **Graceful Degradation**: Falls back to simulated responses when Claude is unavailable
- **Context-Aware Prompting**: Different system prompts for different contexts
- **Single Port Architecture**: Follows Tekton's standardized port assignment

## Implementation Summary

### Core Components

The LLM Adapter consists of several key components:

1. **Server Module**: Initializes and manages both HTTP and WebSocket servers
2. **HTTP Server**: FastAPI-based server for REST endpoints
3. **WebSocket Server**: Real-time communication for streaming responses
4. **LLM Client**: Interface to Claude API with streaming support
5. **Configuration**: Environment-based configuration management

### Directory Structure

```
LLMAdapter/
├── __main__.py                 # Entry point for running as a module
├── IMPLEMENTATION_SUMMARY.md   # Implementation details
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

## Installation and Usage

### Installation

1. Clone the Tekton repository
2. Install dependencies:
   ```bash
   cd /Users/cskoons/projects/github/Tekton/LLMAdapter
   pip install -r requirements.txt
   ```

### Configuration

Set the following environment variables:

```bash
export ANTHROPIC_API_KEY=your_api_key_here
export RHETOR_PORT=8003  # Optional, defaults to 8003
```

### Running the Adapter

```bash
cd /Users/cskoons/projects/github/Tekton/LLMAdapter
python -m llm_adapter
```

### Testing the Adapter

```bash
./test_adapter.py --message "Hello, how are you?"
```

## Integration with Hephaestus

The LLM Adapter is designed to integrate seamlessly with the Hephaestus UI:

1. Hephaestus connects to the LLM Adapter via WebSocket when the Ergon tab is selected
2. Messages from the terminal are sent to the adapter
3. Responses are streamed back in real-time
4. The connection is managed by the Hermes connector

## API Overview

### HTTP Endpoints

- **GET /** - Basic information
- **GET /health** - Health check
- **GET /providers** - Available LLM providers and models
- **POST /provider** - Set the active provider and model
- **POST /message** - Send a message to the LLM
- **POST /stream** - Stream a response from the LLM

### WebSocket Messages

#### Client-to-Server
- **LLM_REQUEST** - Request LLM processing
- **REGISTER** - Register client
- **STATUS** - Request status

#### Server-to-Client
- **UPDATE** - Status updates and streaming chunks
- **RESPONSE** - Complete responses
- **ERROR** - Error messages

## Single Port Architecture

The LLM Adapter follows Tekton's Single Port Architecture:

1. Uses a single port (default: 8003) for all services
2. Implements path-based routing:
   - `/api/*` for HTTP endpoints
   - `/ws` for WebSocket connections
3. Follows standard port assignments as defined in `port_assignments.md`
4. Uses environment variables for configuration

## Limitations and Future Work

### Current Limitations

1. Limited to Claude models from Anthropic
2. No persistent context or memory between requests
3. Basic error handling without retry mechanisms
4. Limited provider and model configuration options

### Future Plans

This adapter is an interim solution and will be replaced by the Rhetor component, which will provide:

1. More sophisticated prompt management
2. Context tracking and memory integration
3. Model selection logic
4. Evaluation and monitoring capabilities

## Migration Path to Rhetor

When implementing Rhetor to replace this adapter:

1. Keep the same message format and WebSocket interface
2. Add more sophisticated prompt management
3. Add context tracking and memory
4. Implement model selection logic
5. Add evaluation and monitoring capabilities

Rhetor should be a drop-in replacement for this adapter from the UI's perspective, with the same interface but enhanced capabilities.

## Troubleshooting

### Common Issues

1. **Connection Refused**: Ensure the adapter is running and on the correct ports
2. **Authentication Error**: Check that the `ANTHROPIC_API_KEY` environment variable is set correctly
3. **No Response**: Verify that the WebSocket connection is established successfully
4. **Simulated Responses Only**: The adapter falls back to simulated responses when Claude is not available

### Debugging Tools

1. **Health Endpoint**: Check `http://localhost:8003/health` for adapter status
2. **Test Script**: Use `test_adapter.py` to test the adapter directly
3. **Browser Console**: Check for WebSocket errors in the browser console

## Conclusion

The LLM Adapter provides a crucial bridge between the Hephaestus UI and language models like Claude. While designed as an interim solution, it implements key architectural patterns that will be carried forward into the more comprehensive Rhetor component, ensuring a smooth transition path.
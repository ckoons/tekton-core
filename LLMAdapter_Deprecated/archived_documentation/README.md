# LLM Adapter

![LLM Adapter](../../../images/icon.jpg)

A lightweight adapter for connecting Tekton's Hephaestus terminal interface to LLM services.

## Overview

This adapter provides a simple bridge between the Hephaestus terminal interface and LLM APIs (specifically Claude). It is a temporary solution to enable testing of the terminal-to-LLM communication before the full Rhetor component is implemented.

## Installation

```bash
cd LLMAdapter
pip install -r requirements.txt
```

## Usage

1. Set your environment variables:

```bash
export ANTHROPIC_API_KEY=your_api_key_here
```

2. Start the adapter:

```bash
./run_adapter.sh
```

3. The adapter will now be available at:
   - HTTP: http://localhost:8300
   - WebSocket: ws://localhost:8301

4. The Hephaestus UI has been configured to automatically connect to this adapter when you open the Ergon chat tab.

## Running with Tekton

For convenience, you can use the provided script to run both the LLM Adapter and Tekton system together:

```bash
./run_with_tekton.sh
```

This will:
1. Start the LLM Adapter in the background
2. Launch the Tekton system
3. When Tekton is stopped, also stop the LLM Adapter

## Testing

You can test the adapter directly using the provided test script:

```bash
./test_adapter.py --message "Hello, how are you?"
```

## Configuration

The adapter is configured through environment variables:

- `ANTHROPIC_API_KEY`: API key for Claude (required)
- `DEFAULT_MODEL`: Default Claude model (default: "claude-3-sonnet-20240229")
- `HTTP_PORT`: HTTP port (default: 8300)
- `WS_PORT`: WebSocket port (default: 8301)
- `HOST`: Host to bind to (default: "localhost")

## Integration with Hephaestus

Hephaestus has been updated to connect to this adapter automatically when:

1. The Ergon tab is selected in the UI
2. A message is sent from the chat interface

The integration happens through the WebSocket interface, with the Hermes connector establishing a connection to the LLM Adapter and handling message streaming.

## Architecture

This adapter is intentionally minimal - it provides just enough functionality to test the terminal interface with real LLM responses. It will be replaced by the Rhetor component when it is implemented.

## License

This software is part of the Tekton project.
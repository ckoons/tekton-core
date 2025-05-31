# Tekton LLM Adapter [DEPRECATED]

**⚠️ DEPRECATION NOTICE: This component has been replaced by Rhetor (port 8003). Please use Rhetor for all LLM interactions.**

A lightweight adapter for connecting Tekton's Hephaestus terminal interface to LLM services.

## Overview

This adapter provides a simple bridge between the Hephaestus terminal interface and LLM APIs (specifically Claude). It was a temporary solution to enable testing of the terminal-to-LLM communication before the full Rhetor component was implemented.

**Status: DEPRECATED - Replaced by Rhetor**
- Rhetor provides a more comprehensive LLM management solution
- All new development should use Rhetor on port 8003
- This component will be removed in a future release

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

For more details, see `/MetaData/Development/LLMAdapter.md`

## License

This software is part of the Tekton project.

## Removal Guide

To completely remove LLM Adapter from the Tekton project, the following changes need to be made:

### 1. **Configuration Files**
- [ ] `/config/port_assignments.md` - Remove LLM Adapter port entries (8300, 8301)
- [ ] `/config/tekton_components.yaml` - Remove llm_adapter component configuration
- [ ] `/shared/utils/env_manager.py` - Remove LLM_ADAPTER_HTTP_PORT and LLM_ADAPTER_WS_PORT

### 2. **Launch and Management Scripts**
- [ ] `/scripts/lib/tekton-ports.sh` - Remove LLM_ADAPTER port exports and functions
- [ ] `/scripts/lib/tekton-config.sh` - Remove llm-adapter from port mappings
- [ ] `/scripts/bin/tekton-config-cli.py` - Remove llm-adapter entries
- [ ] `/scripts/enhanced_tekton_launcher.py` - Remove LLM Adapter from launch options
- [ ] `/scripts/tekton-launch.py` - Remove LLM Adapter from components list

### 3. **Component Integrations**
Most components have `llm_adapter.py` files that actually use Rhetor (port 8003), not LLM Adapter:
- [ ] Verify all component `llm_adapter.py` files use Rhetor
- [ ] Update any hardcoded references to ports 8300/8301

### 4. **UI Components**
- [ ] `/Hephaestus/ui/scripts/terma/terma-service.js` - Update to use Rhetor (8003) instead of 8300
- [ ] `/Terma/ui/js/terma-terminal.js` - Update to use Rhetor instead of 8300
- [ ] `/Terma/terma/utils/config.py` - Update adapter URLs to use Rhetor

### 5. **Documentation**
- [ ] Update all documentation files that reference LLM Adapter
- [ ] Remove LLM Adapter from architecture diagrams
- [ ] Update installation guides to use Rhetor

### 6. **Rhetor Client Libraries**
These incorrectly default to port 8300 and need updating:
- [ ] `/Rhetor/rhetor/clients/python/rhetor_client.py` - Change default from 8300 to 8003
- [ ] `/Rhetor/rhetor/clients/js/rhetor_client.js` - Change default from 8300 to 8003
- [ ] `/Rhetor/rhetor/utils/hermes_helper.py` - Change default from 8300 to 8003
- [ ] `/Hermes/registrations/rhetor.json` - Update ports from 8300 to 8003

### 7. **Final Steps**
- [ ] Remove the `/LLMAdapter` directory entirely
- [ ] Test all components to ensure they work with Rhetor
- [ ] Update CHANGELOG to document the removal

### Migration Path
For any components still using LLM Adapter:
1. Update connection URLs from `http://localhost:8300` to `http://localhost:8003`
2. Update WebSocket URLs from `ws://localhost:8301` to `ws://localhost:8003/ws`
3. Use Rhetor's comprehensive API instead of the simple pass-through

### Notes
- Most "llm_adapter.py" files in components are already using Rhetor (check for RHETOR_PORT usage)
- The main issue is hardcoded references in Terma UI components
- Rhetor provides all LLM Adapter functionality plus much more (MCP tools, multiple providers, etc.)
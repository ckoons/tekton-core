# LLMAdapter Documentation Index

## Overview

The LLMAdapter is the centralized interface for Large Language Model interactions within the Tekton ecosystem. It provides a standardized way to access various LLM providers, handling authentication, model selection, streaming, and failover mechanisms.

## Key Features

- Unified API for multiple LLM providers (OpenAI, Anthropic, local models)
- Synchronous and streaming interfaces for text generation
- Automatic failover between providers
- Response caching for improved performance
- Rate limiting and usage tracking
- Single port architecture integration

## Documentation

### User Documentation

- [README.md](./README.md): Overview and quick start guide
- [USER_GUIDE.md](./USER_GUIDE.md): Comprehensive guide for users
- [INTEGRATION.md](./INTEGRATION.md): How to integrate with LLMAdapter

### Technical Documentation

- [TECHNICAL_DOCUMENTATION.md](./TECHNICAL_DOCUMENTATION.md): Architecture and implementation details
- [API_REFERENCE.md](./API_REFERENCE.md): API endpoints and parameters
- [IMPLEMENTATION_SUMMARY.md](./IMPLEMENTATION_SUMMARY.md): Implementation status and summary

## Architecture

The LLMAdapter follows a layered architecture:

1. **API Layer**: HTTP and WebSocket interfaces for client communication
2. **Provider Layer**: Abstractions for different LLM providers
3. **Cache Layer**: Optimization through response caching
4. **Failover Layer**: Automatic provider switching when needed

## Component Relationships

LLMAdapter interacts with other Tekton components:

- **Terma**: Uses LLMAdapter for terminal chat interface
- **Athena**: Accesses LLMs for knowledge graph operations
- **Ergon**: Utilizes LLMs for task execution
- **Rhetor**: Leverages LLMs for prompt engineering
- **Codex**: Accesses code-specialized models for development

## Getting Started

To quickly start using LLMAdapter, refer to the [README.md](./README.md) file, which contains installation instructions and basic usage examples.

For more detailed information on usage patterns and best practices, see the [USER_GUIDE.md](./USER_GUIDE.md).

## API Endpoints

LLMAdapter provides the following main API endpoints:

- `/api/providers`: Information about available LLM providers
- `/api/models`: Details about available models
- `/api/completions`: Text completion generation
- `/api/chat/completions`: Chat completion generation
- `/ws`: WebSocket endpoint for streaming completions

For comprehensive API documentation, see the [API_REFERENCE.md](./API_REFERENCE.md).

## Single Port Architecture

LLMAdapter follows the Tekton Single Port Architecture for consistent component communication:

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

## Implementation Status

LLMAdapter is fully implemented with the following providers:

- OpenAI (GPT-4, GPT-3.5 Turbo)
- Anthropic (Claude 3 Opus, Claude 3 Sonnet, Claude 3 Haiku)
- Local models (Llama, Mistral)

For current implementation status, see [IMPLEMENTATION_SUMMARY.md](./IMPLEMENTATION_SUMMARY.md).

## Additional Resources

- [Tekton Documentation](../../README.md): Main Tekton documentation
- [SINGLE_PORT_ARCHITECTURE.md](../../docs/SINGLE_PORT_ARCHITECTURE.md): Details on the Single Port Architecture pattern
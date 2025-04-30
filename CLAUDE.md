# Tekton Development Notes

## Single Port Architecture Implementation (April 26, 2025)

We've implemented a new Single Port Architecture for all Tekton components, rationalizing the port assignments and simplifying cross-component communication. Key updates include:

1. **Port Standardization:**
   - Assigned sequential ports (8000-8010) to all components except Hephaestus UI
   - Kept Hephaestus UI on port 8080 following web development conventions
   - Created consistent environment variables for all ports
   - Updated all launch, status, and kill scripts to use the new port assignments

2. **Component Updates:**
   - Modified Hephaestus UI to use environment variables for port connections
   - Updated LLM Adapter and Rhetor to follow the Single Port Architecture pattern
   - Implemented path-based routing for different types of requests (HTTP, WebSocket, Events)
   - Created client-side environment variables for frontend components

3. **New Documentation:**
   - Created [port_assignments.md](./config/port_assignments.md) with the new port scheme
   - Added [SINGLE_PORT_ARCHITECTURE.md](./docs/SINGLE_PORT_ARCHITECTURE.md) detailing the design pattern
   - Documented port usage patterns and URL construction
   - Added comprehensive implementation guidelines for future components

Future architecture work should focus on:
- Standardizing API endpoints across components
- Creating a unified authentication and authorization model
- Implementing graceful degradation for unavailable components
- Adding automatic service discovery for dynamic port allocation

Details about the Single Port Architecture are available in the [SINGLE_PORT_ARCHITECTURE.md](./docs/SINGLE_PORT_ARCHITECTURE.md) document.

## Project Overview

Tekton is an intelligent orchestration system that coordinates multiple AI models and resources to efficiently solve complex software engineering problems. The project aims to:

1. Intelligently route tasks to the most appropriate AI model (local or remote)
2. Optimize resource usage based on task complexity
3. Maintain persistent context and memory across models and sessions
4. Create a seamless experience across different AI capabilities
5. Reduce dependency on costly remote API calls
6. Provide a unified interface for AI-assisted development

### LLM Architecture

Tekton employs a layered LLM integration architecture to provide unified, flexible access to various AI models:

1. **LLM Adapter Layer**: Serves as the centralized interface for all LLM interactions through:
   - HTTP API: Synchronous requests for immediate responses via `/api/` endpoints
   - WebSocket API: Asynchronous streaming for real-time interactions via `/ws` endpoint
   - Model-agnostic interface supporting multiple providers and models

2. **Component Integration**: Components like Terma connect to the LLM Adapter through:
   - Provider/model selection with a unified dropdown interface
   - Automatic adapter detection and connection
   - Graceful fallback when the adapter is unavailable

3. **Startup Management**: The `tekton-launch` script automatically:
   - Checks for LLM Adapter availability before launching components
   - Starts the adapter if not running, regardless of component selection
   - Ensures correct port configuration and availability

This architecture ensures consistent LLM access across all Tekton components while allowing easy switching between different AI models based on task requirements.

## Architecture Principles

- **Local First**: Prefer local resources when appropriate
- **Tiered Processing**: Use the simplest model that can handle the task
- **Memory Centricity**: All operations feed into and leverage a shared memory system
- **Graceful Degradation**: Fall back to simpler models when preferred ones are unavailable
- **Performance Learning**: Record and learn from past task performance to improve routing

## Integration Points

### Engram

- Use Engram for persistent memory across sessions and models
- Leverage structured memory for context categorization
- Use memory performance metrics to guide model selection

### Agenteer

- Leverage Agenteer for specialized agent creation
- Use workflow engine for complex task orchestration
- Create agents for specific domains (testing, debugging, etc.)

### Forge

- Integrate with Forge for code-specific tasks
- Share context between Tekton and Forge
- Use Forge as the software engineering specialist

## Model Tiers

1. **Tier 1 (Local Lightweight)**
   - File operations, codebase navigation, simple edits
   - Models: CodeLlama, Deepseek Coder
   - Preferred for: Quick operations, searching, basic analysis

2. **Tier 2 (Local Midweight)**
   - Code understanding, simple debugging, refactoring
   - Models: Local Claude Haiku, Qwen
   - Preferred for: More complex code tasks, initial problem analysis

3. **Tier 3 (Remote Heavyweight)**
   - Complex reasoning, architectural design, difficult debugging
   - Models: Claude 3.7 Sonnet, GPT-4
   - Preferred for: Tasks requiring deep reasoning or cross-domain knowledge

## Code Style and Conventions

### Python

- Use f-strings for string formatting
- Add type hints to function signatures
- Follow PEP 8 guidelines
- 4 spaces for indentation
- Use docstrings for all functions and classes

### Comments

- Include brief comments for complex sections
- Add TODOs for future improvements
- Document any workarounds or tricky implementations

### Error Handling

- Use try/except blocks for operations that could fail
- Log errors with appropriate level (info, warning, error)
- Return meaningful error messages

### Commit Messages

```
feat: Descriptive title for the changes

- Bullet point describing key implementation details
- Another bullet point with important design decisions
- Additional context about the implementation

🤖 Generated with [Claude Code](https://claude.ai/code)
Design & Engineering Guidance by Casey Koons <cskoons@gmail.com>
Co-Authored-By: Casey Koons <cskoons@gmail.com> & Claude <noreply@anthropic.com>
```

## Development Roadmap

1. **Initial Setup (Current Phase)**
   - Project structure and documentation
   - Core interfaces definition

2. **MVP (Phase 1)**
   - Basic model orchestration
   - Simple task routing
   - Integration with Engram
   - CLI interface

3. **Enhancement (Phase 2)**
   - Performance-based routing
   - Advanced workflow engine
   - Multiple model support
   - Agenteer integration

4. **Production (Phase 3)**
   - Full Forge integration
   - Extended model support
   - Advanced metrics and optimizations
   - Comprehensive documentation

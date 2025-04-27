# Phase 11.5: Unified LLM Adapter Integration

**Last Updated:** April 26, 2025

## Overview

This phase focuses on standardizing LLM integration across Tekton components by retrofitting Hermes, Engram, Ergon, and Telos to use the Rhetor LLM adapter and implementing consistent chat interfaces in their Hephaestus UI components. This unified approach will ensure consistent user experience, reduce code duplication, and provide a standardized pattern for LLM integration across the entire Tekton ecosystem.

This integration establishes a critical architectural pattern that all future Tekton components must follow. Every component in the Tekton ecosystem, both current and future, must integrate with the Rhetor LLM adapter for AI capabilities and implement a standardized chat interface in its Hephaestus UI tab. This requirement has been explicitly added to the roadmap for all upcoming phases.

## Objectives

1. Retrofit all components to use the Rhetor LLM adapter API
2. Implement chat GUI interfaces for all components in their Hephaestus UI tabs
3. Create consistent UI patterns for chat interactions
4. Document the integration patterns for future components

## Implementation Details

### 1. Hermes LLM Integration

#### Backend Integration
- Create a new `hermes/core/llm_adapter.py` module that interfaces with Rhetor
- Implement methods for sending messages to the LLM and handling responses
- Add configuration options for LLM provider selection
- Create integration with message bus for broadcasting LLM-related events

#### UI Implementation
- Create a new "Chat" tab in the Hermes Hephaestus component
- Implement a chat interface with message history display
- Add user input field with send button and keyboard shortcuts
- Implement streaming response display with typing indicator
- Create chat history persistence using the state management system

#### Testing
- Create unit tests for LLM adapter integration
- Implement UI tests for chat interface functionality
- Add integration tests for end-to-end message flow

**Reference:** Use Telos' `telos/core/llm_adapter.py` as an example for API usage.

### 2. Engram LLM Integration

#### Backend Integration
- Create an `engram/core/llm_integration.py` module
- Implement memory-augmented chat capabilities using Engram's existing memory systems
- Add methods for context-aware LLM interactions
- Create integration between memory operations and LLM processing

#### UI Implementation
- Add a "Memory Chat" tab to the Engram Hephaestus component
- Implement a chat interface with memory context display
- Add user input field with send button and keyboard shortcuts
- Create a memory context panel showing which memories are being used
- Implement controls for adjusting memory context size and relevance

#### Testing
- Create unit tests for memory-augmented LLM interactions
- Implement UI tests for the chat interface
- Add integration tests for memory-LLM interaction

**Reference:** Use the existing Engram memory system as the foundation for context-aware chat.

### 3. Ergon LLM Adapter Update

#### Backend Changes
- Update `ergon/core/llm/client.py` to exclusively use the Rhetor LLM adapter
- Standardize the API call patterns to match other components
- Implement streaming response handling via WebSocket
- Add configuration for different LLM models through Rhetor

#### UI Enhancements
- Enhance the existing chat UI with additional capabilities
- Add model selection dropdown for switching between available models
- Implement message tagging for different agent contexts
- Create visualization for agent thinking/reasoning processes
- Add a system message editor for controlling agent behavior

#### Testing
- Update existing tests to work with the new LLM adapter
- Add tests for model switching functionality
- Implement UI tests for enhanced chat capabilities

**Reference:** The current implementation already has a chat interface; focus on enhancing it and standardizing the backend.

### 4. Telos Chat Interface

#### UI Implementation
- Create a "Requirements Chat" tab in the Telos Hephaestus component
- Implement a chat interface focused on requirements analysis
- Add user input field with send button and keyboard shortcuts
- Create integration with the existing requirement management system
- Implement context awareness of the current requirement being discussed
- Add requirement creation/editing capabilities directly from chat

#### Testing
- Create UI tests for the new chat interface
- Implement integration tests for chat-driven requirement management
- Add tests for context-awareness features

**Reference:** The backend LLM integration already exists; focus on creating the UI component.

### 5. Shared Components and Patterns

#### Shared UI Components
- Create a `chat-interface.js` utility in the shared component utilities
- Implement reusable chat UI components (message list, input field, etc.)
- Add standardized styling for chat interfaces
- Create common keyboard shortcuts and controls

#### Standardized API Patterns
- Create a `llm_adapter_client.js` utility for frontend-to-backend communication
- Implement standardized error handling for LLM interactions
- Add common rate limiting and retry logic
- Create response streaming utilities

#### Documentation
- Document the standard chat UI patterns
- Create API reference for LLM adapter integration
- Add examples of common chat interaction patterns
- Document best practices for context management

## Implementation Process

### Step 1: Preparation and Analysis
1. Study the Telos LLM adapter implementation as a reference
2. Analyze the Ergon chat implementation for UI patterns
3. Create a detailed implementation plan for each component
4. Define the standard chat UI components and patterns

### Step 2: Backend Implementation
1. Implement or update LLM adapter modules for each component
2. Create integration tests for backend functionality
3. Implement common utilities for LLM interaction
4. Add configuration options for LLM provider selection

### Step 3: Frontend Implementation
1. Create shared chat UI components
2. Implement component-specific chat interfaces
3. Add state management for chat history and preferences
4. Implement response streaming and formatting

### Step 4: Integration and Testing
1. Integrate the backend and frontend implementations
2. Create comprehensive tests for all components
3. Implement end-to-end testing for chat functionality
4. Verify cross-component consistency

### Step 5: Documentation and Finalization
1. Create comprehensive documentation for the implementation
2. Add examples and usage patterns
3. Update the component registry
4. Create session log documentation

## File Structure Changes

### New Files

#### Backend
- `/Users/cskoons/projects/github/Tekton/Hermes/hermes/core/llm_adapter.py`
- `/Users/cskoons/projects/github/Tekton/Engram/engram/core/llm_integration.py`
- `/Users/cskoons/projects/github/Tekton/docs/llm_integration_guide.md`

#### Frontend
- `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/scripts/shared/chat-interface.js`
- `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/scripts/shared/llm_adapter_client.js`
- `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/styles/shared/chat-interface.css`
- `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/components/hermes/hermes-chat-tab.html`
- `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/components/engram/engram-chat-tab.html`
- `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/components/telos/telos-chat-tab.html`

### Updated Files

#### Backend
- `/Users/cskoons/projects/github/Tekton/Ergon/ergon/core/llm/client.py`
- `/Users/cskoons/projects/github/Tekton/Tekton_Roadmap.md`

#### Frontend
- `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/components/hermes/hermes-component.html`
- `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/components/hermes/hermes-component.js`
- `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/components/engram/engram-component.html`
- `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/components/engram/engram-component.js`
- `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/components/ergon/ergon-component.html`
- `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/components/ergon/ergon-component.js`
- `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/components/telos/telos-component.html`
- `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/components/telos/telos-component.js`
- `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/server/component_registry.json`

## Documentation Requirements

The following documentation must be updated at the end of this phase:

### 1. Implementation Status Documentation
- Update `IMPLEMENTATION_STATUS.md` to include Phase 11.5 completion
- Add detailed list of completed tasks for each component
- Update "Current State" section with new capabilities
- Update component migration status table

### 2. Session Log Documentation
- Create `session_logs/session_11.5_completed.md` with detailed implementation notes
- Include code examples, architecture decisions, and challenges encountered
- Document patterns used for each component
- Include screenshots of the implemented chat interfaces

### 3. LLM Integration Guide
- Create `docs/llm_integration_guide.md` detailing the standard patterns
- Include API references for the Rhetor LLM adapter
- Add examples of common chat interaction patterns
- Document best practices for context management

### 4. Component Registry Updates
- Update `component_registry.json` to include new chat capabilities
- Add paths to new JavaScript and CSS files
- Update component dependencies

### 5. UI Pattern Documentation
- Add chat interface patterns to `COMPONENT_PATTERNS.md`
- Document standard UI elements and their usage
- Add keyboard shortcut documentation
- Include accessibility considerations

### 6. Test Documentation
- Document test coverage for the new functionality
- Include examples of test cases for chat interfaces
- Add notes on testing approach for LLM interactions

## Success Criteria

Phase 11.5 will be considered complete when:

1. All four components (Hermes, Engram, Ergon, Telos) are using the Rhetor LLM adapter
2. Each component has a functioning chat interface in its Hephaestus UI
3. Chat interfaces follow consistent UI patterns and keyboard shortcuts
4. Backend LLM integration follows standardized patterns
5. Comprehensive documentation has been created
6. All tests pass with good coverage

## Technical Considerations

### WebSocket vs. HTTP API
- Use WebSocket for streaming responses where real-time updates are important
- Use HTTP API for single-request operations like requirement analysis
- Document the appropriate use cases for each approach

### State Management
- Leverage the existing state management system for chat history and preferences
- Use namespaced state to isolate component-specific chat state
- Implement persistence for chat history where appropriate

### Performance
- Implement response streaming to improve perceived performance
- Add request batching for frequent small requests
- Implement caching for repeated identical requests

### Security
- Sanitize user inputs before sending to LLM
- Implement rate limiting for LLM requests
- Add authentication for sensitive operations

## Resources

- Example of Rhetor LLM adapter integration: `telos/core/llm_adapter.py`
- Example of chat UI implementation: Ergon component
- State management reference: `state-manager.js` and `component-utils-state.js`
- Single Port Architecture documentation: `SINGLE_PORT_ARCHITECTURE.md`

## Timeline

- **Backend Implementation**: 3 days
- **Frontend Implementation**: 4 days
- **Integration and Testing**: 2 days
- **Documentation**: 1 day
- **Total Estimated Time**: 10 days

## Team Allocation

- Backend Implementation: 2 developers
- Frontend Implementation: 2 developers
- Testing: 1 developer
- Documentation: 1 developer

## Next Steps After Completion

After completing Phase 11.5, the team will move on to Phase 12 (Prometheus Planning System) with a unified approach to LLM integration, making future LLM-related development more consistent and efficient.
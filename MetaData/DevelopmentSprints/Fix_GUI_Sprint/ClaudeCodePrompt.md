# Fix GUI Sprint - Claude Code Prompt (SESSION 2: ERGON COMPONENT)

## Overview
This document serves as the prompt for the second Claude Code session working on the Fix GUI Sprint for the Tekton project. In our previous session, we successfully implemented the Athena component using the Direct HTML Injection approach. Now we'll focus on implementing the Ergon component using the same pattern and addressing some outstanding issues.

Tekton is an intelligent orchestration system that coordinates multiple AI models and resources to efficiently solve complex software engineering problems. This Development Sprint focuses on simplifying and standardizing the Hephaestus UI architecture to create a more reliable component integration system.

## Current Progress

We've made significant progress on our revised UI architecture:

1. **Direct HTML Injection Pattern**: Successfully implemented for the Athena component
2. **WebSocket Connection**: Fixed WebSocket protocol handling in server.py
3. **UI Refinements**: Created a compact, clean UI for Athena with improved chat interface
4. **Component Structure**: Established a clear pattern for component implementation

Our approach uses direct HTML injection within a clear two-panel layout:
- **LEFT PANEL:** Navigation tabs and component selection (with corrected Ergon label: "Ergon - Agents/Tools/MCP")
- **RIGHT PANEL:** Main content area for component UIs using direct HTML injection

## Implementation Strategy - Component-by-Component Approach

We'll tackle this work methodically, component by component, with defined checkpoints for review and approval:

### Phase 1: Core Architecture and First Component (Athena)

1. Create Dedicated Component Loader in UI Manager
   - Implement direct HTML injection strategy in `ui-manager.js`
   - Create a template pattern for component loading
   - Get approval for the approach

2. Fix WebSocket Connection Handling
   - Properly handle WebSocket protocol in server.py
   - Fix connection parameters in websocket.js
   - Test and get approval

3. Athena Component Implementation
   - Evaluate Tab Structure: Header, Footer, and Content Tabs
   - Extract existing HTML content from component files
   - Create dedicated `loadAthenaComponent()` function with direct HTML injection
   - Test and get approval

### Phase 2: Additional Component Migration (One-by-One)

For each component (Ergon, Terma, Rhetor, etc.):

1. Component Analysis
   - Examine current implementation
   - Identify tab structure and required functionality
   - Create migration plan
   - Get approval for component-specific approach

2. Create Dedicated Loader
   - Implement dedicated loader function in ui-manager.js
   - Extract HTML content from existing components
   - Preserve existing JavaScript functionality
   - Get approval for implementation

3. Test and Refine
   - Test component functionality
   - Fix any issues
   - Document component-specific requirements
   - Get final approval before moving to next component

### Phase 3: Standardization and Chat Interface

1. Create Shared Utilities
   - Develop common tab handling functionality
   - Create shared styling patterns
   - Document standards
   - Get approval

2. Chat Interface Integration
   - Create shared chat template for component-specific chats
   - Add Team Chat to all components (always the last tab)
   - Implement shared chat functionality for both component-specific and Team Chat
   - Make Clear Chat button work contextually with the active chat
   - Connect to LLM adapter
   - Test and get approval

## Key Files

### Core UI Files
- `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/scripts/ui-manager.js`
- `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/server/component_registry.json`
- `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/scripts/websocket.js`
- `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/server/server.py`
- `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/styles/main.css`

### Athena Component Files
- `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/components/athena/athena-component.html`
- `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/scripts/athena/athena-component.js`
- `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/scripts/athena/athena-service.js`
- `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/styles/athena/athena-component.css`

### Chat Interface Files
- `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/scripts/shared/chat-interface.js`
- `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/styles/shared/chat-interface.css`
- `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/scripts/shared/llm_adapter_client.js`

## Testing Strategy

After each implementation step:
1. Restart the Hephaestus UI server
2. Test component loading
3. Verify WebSocket connections
4. Check for console errors
5. Test functionality of the modified components

## Key Architectural Decisions

1. **Two-Panel Layout:** Clear separation of navigation (left) and content (right)
2. **Minimal DOM Manipulation:** Use simple HTML-based components
3. **Component Templates:** Standardized structure for new components
4. **Terma for Terminal:** Use Terma for dedicated terminal functionality
5. **Standardized Chat:** Add chat interface to all components

## Code Style and Conventions

### HTML
- Use semantic HTML5 elements
- Keep templates clean and minimal
- Include clear class names for styling

### CSS
- Follow BEM naming convention (Block__Element--Modifier)
- Use CSS variables for theming
- Organize by component with shared styles

### JavaScript
- Use ES6+ features
- Implement standard lifecycle methods
- Properly manage event listeners
- Use clear error handling

## Deliverables

1. **Refactored UI Manager** with simplified component loading
2. **Fixed WebSocket connection** handling
3. **Standardized component templates** for HTML and JavaScript
4. **Fixed Athena component** integration
5. **Chat interface component** for integration with all components
6. **Documentation** for component development and integration

## Success Metrics

1. Athena component loads and functions correctly in the main content area
2. WebSocket connections establish without errors
3. Component loading is reliable and consistent
4. Chat interfaces work correctly with LLM Adapter
5. UI architecture is simplified and documented

## Implementation Approach

1. Start with the core UI architecture changes
2. Fix WebSocket connection issues
3. Update component registry
4. Create standardized component templates
5. Fix Athena component integration
6. Add chat interface integration

The goal is to create a simple, reliable UI architecture that minimizes complexity while providing all necessary functionality.

## Issues to Address

### WebSocket Connection
The WebSocket connection issues are likely due to improper handling of the WebSocket protocol. Look for how the server is handling the Connection header and ensure it's properly handling WebSocket protocol upgrades.

### Athena Component Loading
The Athena component is currently being loaded with `defaultMode: "terminal"` instead of `defaultMode: "html"`. Update the component registration and ensure the UI Manager is loading it in the correct panel.

### Shadow DOM Complexity
The Shadow DOM implementation is causing conflicts with the component loader. Consider simplifying or removing Shadow DOM usage for most components, using simpler HTML-based components instead.

## Documentation Requirements

As you implement changes, please document:
1. The architectural changes made
2. How to create new components using the standardized templates
3. How to integrate the chat interface with components
4. Any configuration changes required for WebSocket connections

This documentation should be clear and concise, focusing on what developers need to know to work with the system.

## Final Notes

The goal is to simplify the UI architecture while maintaining functionality. Focus on creating a reliable, maintainable system rather than adding new features. The priority is fixing the Athena component integration and ensuring all components load correctly.
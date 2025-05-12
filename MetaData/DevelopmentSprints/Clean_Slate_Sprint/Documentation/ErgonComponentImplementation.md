# Ergon Component Implementation

## Overview

The Ergon component has been completely refactored to follow the new Clean Slate architecture and BEM naming conventions. This document outlines the changes made and the new structure of the component.

## BEM Naming Convention Implementation

The component now follows Block-Element-Modifier (BEM) naming conventions:

- Block: `ergon`
- Elements: `ergon__header`, `ergon__title`, `ergon__tabs-container`, etc.
- Modifiers: `ergon__tab--active`, `ergon__message--system`, etc.

Example:
```html
<div class="ergon__header">
    <div class="ergon__title-container">
        <img src="/images/hexagon.jpg" alt="Tekton" class="ergon__icon">
        <h2 class="ergon__title">
            <span class="ergon__title-main">Ergon</span>
            <span class="ergon__title-sub">Agents/Tools/MCP</span>
        </h2>
    </div>
</div>
```

## Component Structure

The component now follows a standard structure:

1. **Header**: Contains the component title and icon
2. **Menu Bar**: Tab navigation with ordered tabs (Agents, Tools, MCP, Memory, Tool Chat, Team Chat)
3. **Content Panels**: Individual panels for each tab content
4. **Footer**: Chat input area consistent across all panels

## Key Changes

### 1. Header Implementation

Added a proper header with the Tekton hexagon icon and a title that respects the `SHOW_GREEK_NAMES` environment variable:

```html
<div class="ergon__header">
    <div class="ergon__title-container">
        <img src="/images/hexagon.jpg" alt="Tekton" class="ergon__icon">
        <h2 class="ergon__title">
            <span class="ergon__title-main">Ergon</span>
            <span class="ergon__title-sub">Agents/Tools/MCP</span>
        </h2>
    </div>
</div>
```

The JavaScript dynamically handles the display:

```javascript
handleGreekNames() {
    // Get the title element
    const titleElement = container.querySelector('.ergon__title-main');
    const subtitleElement = container.querySelector('.ergon__title-sub');
    
    // Check environment setting
    if (window.ENV && window.ENV.SHOW_GREEK_NAMES === 'false') {
        // Hide the Greek name
        titleElement.style.display = 'none';
        // Make the modern name more prominent
        subtitleElement.style.fontWeight = 'bold';
        subtitleElement.style.fontSize = '1.5rem';
    }
}
```

### 2. Menu Bar and Tab Order

Tabs have been reordered as specified and icons have been removed:

```html
<div class="ergon__tabs-container">
    <div class="ergon__tab" data-tab="agents">
        <span class="ergon__tab-label">Agents</span>
    </div>
    <div class="ergon__tab" data-tab="tools">
        <span class="ergon__tab-label">Tools</span>
    </div>
    <div class="ergon__tab" data-tab="mcp">
        <span class="ergon__tab-label">MCP</span>
    </div>
    <div class="ergon__tab" data-tab="memory">
        <span class="ergon__tab-label">Memory</span>
    </div>
    <div class="ergon__tab" data-tab="ergon">
        <span class="ergon__tab-label">Tool Chat</span>
    </div>
    <div class="ergon__tab" data-tab="awt-team">
        <span class="ergon__tab-label">Team Chat</span>
    </div>
</div>
```

The new order is:
1. Agents
2. Tools
3. MCP (new)
4. Memory
5. Tool Chat (previously Ergon Chat)
6. Team Chat (previously Symposium)

### 3. Chat Panel Structure

Standardized chat panel structure for proper scrolling:

```html
<div id="ergon-panel" class="ergon__panel">
    <div id="ergon-messages" class="ergon__chat-messages">
        <!-- Chat messages go here -->
    </div>
    
    <!-- Footer with chat input -->
    <div class="ergon__footer">
        <div class="ergon__chat-input-container">
            <div class="ergon__chat-prompt">></div>
            <input type="text" class="ergon__chat-input" data-context="ergon" placeholder="Enter message...">
            <button class="ergon__send-button">
                <span class="ergon__send-icon">➤</span>
            </button>
        </div>
    </div>
</div>
```

The CSS positioning ensures proper scrolling:

```css
.ergon__panel {
    position: relative;
    height: 100%;
    overflow: hidden;
}

.ergon__chat-messages {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 70px; /* Height of the footer */
    overflow-y: auto;
    padding: 16px;
    display: flex;
    flex-direction: column;
}

.ergon__footer {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    height: 70px;
    background-color: var(--bg-secondary);
    border-top: 1px solid var(--border-color);
    padding: 12px;
}
```

### 4. MCP Tab

Added a new MCP (Multi-Cloud Platform) tab with appropriate structure and functionality:

```html
<div id="mcp-panel" class="ergon__panel">
    <div id="mcp-messages" class="ergon__chat-messages">
        <!-- Welcome message -->
        <div class="ergon__message ergon__message--system">
            <div class="ergon__message-content">
                <div class="ergon__message-text">
                    <h3>MCP Management Interface</h3>
                    <p>This interface allows you to manage multi-cloud platforms and integrations.</p>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Footer with chat input -->
    <div class="ergon__footer">
        <div class="ergon__chat-input-container">
            <div class="ergon__chat-prompt">></div>
            <input type="text" class="ergon__chat-input" data-context="mcp" placeholder="Enter MCP commands...">
            <button class="ergon__send-button">
                <span class="ergon__send-icon">➤</span>
            </button>
        </div>
    </div>
</div>
```

The JavaScript includes MCP context in all message handling:

```javascript
// Message history tracking for chat
this.messageHistory = {
    'ergon': [],
    'awt-team': [],
    'mcp': []
};

// Handle chunk based on context
if (contextId === 'ergon' || contextId === 'awt-team' || contextId === 'mcp') {
    this.handleStreamChunk(contextId, chunk);
}
```

### 5. Chat Footers

Standardized chat input footers have been added to all panels:

```html
<!-- Footer with chat input -->
<div class="ergon__footer">
    <div class="ergon__chat-input-container">
        <div class="ergon__chat-prompt">></div>
        <input type="text" class="ergon__chat-input" data-context="context-name" placeholder="Enter message...">
        <button class="ergon__send-button">
            <span class="ergon__send-icon">➤</span>
        </button>
    </div>
</div>
```

This creates a consistent interface across all panels.

## DOM Scoping

All DOM operations are now properly scoped to the component container:

```javascript
// Find the Ergon container (scope all DOM operations to this container)
const container = document.querySelector('.ergon');
if (!container) {
    console.error('Ergon container not found!');
    return;
}

// Get elements within the container
const tabButton = container.querySelector(`.ergon__tab[data-tab="${tabId}"]`);
```

This prevents conflicts with other components.

## Event Delegation

Event handlers are properly attached and container-scoped:

```javascript
// Add event listeners to all chat inputs
chatInputs.forEach(input => {
    const context = input.getAttribute('data-context');
    
    // Store the chat input element for each context
    this[`${context}ChatInput`] = input;
    
    // Send button
    const sendButton = input.parentElement.querySelector(`.ergon__send-button`);
    if (sendButton) {
        sendButton.addEventListener('click', () => {
            const message = input.value.trim();
            if (message) {
                this.sendChatMessage(context, message);
                input.value = '';
            }
        });
    }
});
```

## LLM Integration

The component now integrates with the Hermes LLM connector to provide AI chat capabilities:

```javascript
// Use LLM integration if available
if (window.hermesConnector) {
    // Register stream event handlers if not already done
    if (!this.streamHandlersRegistered) {
        this.setupStreamHandlers();
    }
    
    // Send to LLM via Hermes connector
    window.hermesConnector.sendLLMMessage(context, message, true, {
        // Additional options can be configured here
        temperature: 0.7
    });
}
```

## Future Improvements

1. Add proper error handling for LLM connections
2. Implement caching for previous conversations
3. Add message formatting support (markdown, code blocks)
4. Implement user preferences for chat behavior
5. Add real-time status indicators for remote systems

## Conclusion

The Ergon component has been fully refactored to match the new Clean Slate architecture. It now features:

- Complete BEM naming convention implementation
- Proper component structure with header, menu, content, and footer
- Consistent chat interfaces across all panels
- MCP tab for multi-cloud platform management
- Improved chat scrolling behavior
- Greek/modern name handling based on environment variables

This implementation can serve as a reference for other components in the Tekton ecosystem.
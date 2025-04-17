# Terminal Implementation for Tekton UI

## Original Terminal Implementation (Terminal.md)

### Core Design Elements

1. Scrollable Container: A dedicated div with fixed height, overflow-y set to auto, and flex-direction: column-reverse (to keep newest content visible)
2. Message Types: Different styling for:
   - User messages
   - AI responses
   - System notifications
   - Command outputs (if applicable)
3. Real-time Updates: WebSocket connection to stream AI responses with typing indicators

### HTML Structure

```html
<div class="ai-terminal-container">
  <div id="ai-terminal-messages" class="ai-terminal-messages">
    <!-- Messages will be added here dynamically -->
  </div>
  <div class="ai-terminal-status">
    <!-- Typing indicator, connection status -->
    <div id="ai-typing-indicator" class="ai-typing hidden">
      <span class="dot"></span><span class="dot"></span><span class="dot"></span>
    </div>
  </div>
</div>
```

### CSS Styling

```css
.ai-terminal-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  background-color: var(--terminal-bg, #1e1e1e);
  color: var(--terminal-text, #f8f8f8);
  font-family: 'Menlo', 'Monaco', 'Courier New', monospace;
  border-radius: var(--border-radius);
}

.ai-terminal-messages {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column-reverse; /* Keep newest content visible */
  padding: 12px;
}

.message {
  margin: 8px 0;
  padding: 8px 12px;
  border-radius: 4px;
  max-width: 85%;
  word-wrap: break-word;
  line-height: 1.4;
}

.message-user {
  align-self: flex-end;
  background-color: var(--accent-primary);
  color: white;
}

.message-ai {
  align-self: flex-start;
  background-color: var(--bg-tertiary);
  white-space: pre-wrap; /* Preserve formatting */
}

.message-system {
  align-self: center;
  background-color: rgba(255, 255, 255, 0.1);
  font-style: italic;
  padding: 4px 8px;
  font-size: 0.85rem;
}

.ai-typing {
  padding: 8px;
  display: flex;
  align-items: center;
}

.ai-typing .dot {
  background-color: #aaa;
  border-radius: 50%;
  display: inline-block;
  width: 8px;
  height: 8px;
  margin: 0 3px;
  animation: typing-animation 1.4s infinite ease-in-out;
}

.ai-typing .dot:nth-child(2) {
  animation-delay: 0.2s;
}

.ai-typing .dot:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing-animation {
  0%, 60%, 100% { transform: translateY(0); }
  30% { transform: translateY(-6px); }
}

.hidden {
  display: none;
}

/* Code blocks */
.message-ai pre {
  background-color: rgba(0, 0, 0, 0.3);
  padding: 8px;
  border-radius: 4px;
  overflow-x: auto;
}

/* Make sure code doesn't overflow */
.message-ai code {
  white-space: pre-wrap;
  word-break: break-word;
}
```

### JavaScript Functions

```javascript
// Initialize the terminal
function initAITerminal(componentId) {
  // Clear existing messages
  const messagesContainer = document.getElementById('ai-terminal-messages');
  messagesContainer.innerHTML = '';

  // Add welcome message
  addSystemMessage(componentId, "Connected to " + componentId + " AI assistant.");

  // Set up input handlers (already in your footer area)
  setupChatInputHandlers(componentId);
}

// Add a user message to the terminal
function addUserMessage(componentId, text) {
  const messagesContainer = document.getElementById('ai-terminal-messages');
  const messageElement = document.createElement('div');
  messageElement.className = 'message message-user';
  messageElement.textContent = text;

  // Add to top (since we're using column-reverse)
  messagesContainer.prepend(messageElement);

  // Store in conversation history
  storeMessage(componentId, 'user', text);

  // Show typing indicator
  showTypingIndicator();
}

// Add an AI message to the terminal
function addAIMessage(componentId, text) {
  // Hide typing indicator
  hideTypingIndicator();

  const messagesContainer = document.getElementById('ai-terminal-messages');
  const messageElement = document.createElement('div');
  messageElement.className = 'message message-ai';

  // Process markdown/code if needed
  // This could use a simple library like marked.js
  // For now, just handle code blocks with simple regex
  text = text.replace(/```([^`]+)```/g, '<pre><code>$1</code></pre>');

  messageElement.innerHTML = text;

  // Add to top (since we're using column-reverse)
  messagesContainer.prepend(messageElement);

  // Store in conversation history
  storeMessage(componentId, 'ai', text);
}

// Add a system message
function addSystemMessage(componentId, text) {
  const messagesContainer = document.getElementById('ai-terminal-messages');
  const messageElement = document.createElement('div');
  messageElement.className = 'message message-system';
  messageElement.textContent = text;

  // Add to top (since we're using column-reverse)
  messagesContainer.prepend(messageElement);
}

// Show typing indicator
function showTypingIndicator() {
  const indicator = document.getElementById('ai-typing-indicator');
  indicator.classList.remove('hidden');
}

// Hide typing indicator
function hideTypingIndicator() {
  const indicator = document.getElementById('ai-typing-indicator');
  indicator.classList.add('hidden');
}

// Store messages for persistence
function storeMessage(componentId, role, text) {
  const conversationHistory = JSON.parse(localStorage.getItem(`tekton_conversation_${componentId}`) || '[]');
  conversationHistory.push({
    role: role,
    content: text,
    timestamp: new Date().toISOString()
  });

  // Keep only last 50 messages to prevent localStorage overflow
  if (conversationHistory.length > 50) {
    conversationHistory.shift();
  }

  localStorage.setItem(`tekton_conversation_${componentId}`, JSON.stringify(conversationHistory));
}

// Load past conversation
function loadConversation(componentId) {
  const conversationHistory = JSON.parse(localStorage.getItem(`tekton_conversation_${componentId}`) || '[]');
  const messagesContainer = document.getElementById('ai-terminal-messages');
  messagesContainer.innerHTML = '';

  // Display in reverse order (newest at bottom)
  for (let i = conversationHistory.length - 1; i >= 0; i--) {
    const message = conversationHistory[i];
    if (message.role === 'user') {
      const messageElement = document.createElement('div');
      messageElement.className = 'message message-user';
      messageElement.textContent = message.content;
      messagesContainer.prepend(messageElement);
    } else if (message.role === 'ai') {
      const messageElement = document.createElement('div');
      messageElement.className = 'message message-ai';
      // Process markdown/code if needed
      let content = message.content.replace(/```([^`]+)```/g, '<pre><code>$1</code></pre>');
      messageElement.innerHTML = content;
      messagesContainer.prepend(messageElement);
    }
  }

  // Add a divider
  if (conversationHistory.length > 0) {
    addSystemMessage(componentId, "Previous conversation loaded");
  }
}
```

## Simplified Terminal Chat Interface (Terminal2.md)

### Chat Flow

1. User Input: User types in the chat input at the bottom (shared across all components)
2. Send Button: User clicks Send or presses Enter
3. Message Routing:
   - Current active component receives the message
   - WebSocket sends the message to the correct AI backend
4. AI Response:
   - Received via WebSocket
   - Displayed in the active component's chat area
   - Formatted with proper markdown/styling

### Simple Terminal Implementation

```javascript
// Component activation (when user clicks on a component in left panel)
function activateComponent(componentId) {
  // Update active component
  window.activeComponent = componentId;

  // Show greeting if first time
  if (!localStorage.getItem(`tekton_greeted_${componentId}`)) {
    displayAIMessage(componentId, getGreetingForComponent(componentId));
    localStorage.setItem(`tekton_greeted_${componentId}`, 'true');
  }

  // Load existing chat history
  loadComponentChatHistory(componentId);

  // Restore any draft message
  document.getElementById('chat-input').value =
    localStorage.getItem(`tekton_draft_${componentId}`) || '';
}

// Save draft message when switching components
function saveDraftMessage(componentId) {
  const inputField = document.getElementById('chat-input');
  localStorage.setItem(`tekton_draft_${componentId}`, inputField.value);
}

// Display message from user
function displayUserMessage(message) {
  const componentId = window.activeComponent;
  const terminalContainer = document.getElementById('terminal');

  // Create message element
  const messageElement = document.createElement('div');
  messageElement.className = 'user-message';
  messageElement.innerHTML = `<span class="user-prefix">You:</span> ${message}`;

  // Add to terminal
  terminalContainer.appendChild(messageElement);

  // Scroll to bottom
  terminalContainer.scrollTop = terminalContainer.scrollHeight;

  // Save to history
  saveChatMessage(componentId, 'user', message);
}

// Display message from AI
function displayAIMessage(componentId, message) {
  const terminalContainer = document.getElementById('terminal');

  // Create message element
  const messageElement = document.createElement('div');
  messageElement.className = 'ai-message';

  // Format message (basic markdown)
  const formattedMessage = formatMessage(message);

  // Set content
  messageElement.innerHTML = `<span class="ai-prefix">${componentId}:</span> ${formattedMessage}`;

  // Add to terminal
  terminalContainer.appendChild(messageElement);

  // Scroll to bottom
  terminalContainer.scrollTop = terminalContainer.scrollHeight;

  // Save to history
  saveChatMessage(componentId, 'ai', message);
}

// Format message with markdown and code highlighting
function formatMessage(message) {
  // Handle code blocks
  message = message.replace(/```(\w+)?\n([\s\S]+?)\n```/g, (match, language, code) => {
    return `<pre class="code-block${language ? ` language-${language}` : ''}"><code>${code}</code></pre>`;
  });

  // Handle bold
  message = message.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

  // Handle italics
  message = message.replace(/\*(.*?)\*/g, '<em>$1</em>');

  return message;
}
```

## Terminal Implementation Plan (TerminalProposal.md)

### Component Design

The core component will be terminal-chat.js with the following structure:

```javascript
/**
 * Terminal Chat Component
 * Enhanced terminal with AI chat capabilities
 */
class TerminalChatManager {
    constructor(containerId, options = {}) {
        this.containerId = containerId;
        this.container = null;
        this.options = {
            showTimestamps: true,
            showTypingIndicator: true,
            markdownFormatting: true,
            ...options
        };
        this.history = {};
        this.isTyping = false;
        this.typingTimer = null;
    }

    /**
     * Initialize the chat terminal
     */
    init() {
        this.container = document.getElementById(this.containerId);
        // Setup event handlers
        // Initialize styling
    }

    /**
     * Add a user message to the chat
     */
    addUserMessage(text) {
        this.addMessage('user', text);
    }

    /**
     * Add an AI message to the chat
     */
    addAIMessage(text, componentId) {
        this.addMessage('ai', text, componentId);
    }

    /**
     * Add a message to the chat
     */
    addMessage(type, text, componentId = null) {
        // Create message element
        // Format text (markdown)
        // Add to container
        // Scroll to bottom
        // Store in history
    }

    /**
     * Show typing indicator
     */
    showTypingIndicator(componentId) {
        // Show animated typing indicator
    }

    /**
     * Hide typing indicator
     */
    hideTypingIndicator() {
        // Remove typing indicator
    }

    /**
     * Load chat history for a component
     */
    loadHistory(componentId) {
        // Clear chat
        // Load history
        // Replay messages
    }

    /**
     * Save chat history
     */
    saveHistory(componentId) {
        // Save to localStorage
    }
}
```

### HTML Structure for Chat Interface

```html
<div class="terminal-chat">
  <div class="chat-messages">
    <!-- System message -->
    <div class="chat-message system-message">
      <div class="message-content">Welcome to the Ergon AI Assistant. How can I help you today?</div>
      <div class="message-timestamp">12:34 PM</div>
    </div>

    <!-- User message -->
    <div class="chat-message user-message">
      <div class="message-header">
        <span class="message-sender">You</span>
        <span class="message-timestamp">12:35 PM</span>
      </div>
      <div class="message-content">How do I create a new agent?</div>
    </div>

    <!-- AI message -->
    <div class="chat-message ai-message">
      <div class="message-header">
        <span class="message-sender">Ergon</span>
        <span class="message-timestamp">12:35 PM</span>
      </div>
      <div class="message-content">
        <p>Creating a new agent is simple. You can:</p>
        <ol>
          <li>Navigate to the Agents tab</li>
          <li>Click "Create Agent" button</li>
          <li>Fill in the required fields</li>
          <li>Click "Create"</li>
        </ol>
        <p>Would you like me to help you set up a specific type of agent?</p>
      </div>
    </div>

    <!-- Typing indicator -->
    <div class="chat-message typing-indicator">
      <div class="typing-dots">
        <span class="dot"></span>
        <span class="dot"></span>
        <span class="dot"></span>
      </div>
    </div>
  </div>
</div>
```

## Terminal-Focused UI Implementation (TerminaGiveUp.md)

### Overview

We will simplify the Tekton UI by removing the header and footer from the right panel, expanding the terminal to fill the entire right side, and removing any trace of the separate chat interface. This will provide a more reliable and maintainable UI.

### Files to Modify

1. CSS Files:
   - main.css: Remove styles for content-header and content-footer
   - Adjust terminal panel to fill entire area

2. HTML Structure:
   - index.html: Remove content-header section and content-footer section with chat-input

3. JavaScript Files:
   - main.js: Remove chat input event handlers and functions
   - terminal.js: Enhance with input capability within the terminal itself
   - websocket.js: Update to send messages directly to terminal

### Debug Logging Strategy

- Add comprehensive logging at key points:
  - Input capture
  - Message processing
  - WebSocket communication
  - Component interaction
  - Terminal rendering

### Expected Outcome

A simplified UI with:
- Full-height terminal panel on the right side
- Direct input/output through the terminal
- No separate chat interface
- Clear visual distinction between user commands and AI responses
- Improved reliability and maintainability

## Advanced Terminal Implementation (TerminalNext.md)

### Context Management

1. Create Template Component:
   - Use the Ergon implementation as a base template
   - Extract common chat functionality into a shared module
   - Define standard interfaces for component registration

2. Component Registration System:
   - Create a central registry for all AI components
   - Implement standardized lifecycle management
   - Add context switching with proper state preservation

### Advanced UI Features

1. Streaming Responses:
   - Enhance WebSocket protocol to support chunked responses
   - Add character-by-character rendering for AI responses
   - Implement typewriter effect with natural timing

2. Rich Media Support:
   - Add support for embedded images and diagrams
   - Implement interactive code execution blocks
   - Add syntax highlighting for more languages

### Performance Optimization

1. Efficient History Storage:
   - Implement message compression for long-term storage
   - Add pagination for large conversation histories
   - Create memory pruning strategies for old content

2. Optimized Rendering:
   - Implement virtual scrolling for long conversations
   - Add lazy loading for rich media content
   - Optimize animations for smoother performance
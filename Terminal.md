ilding a Terminal-based AI Chat Interface for Tekton Components

  To create a reliable scrolling terminal interface for AI-user chat in the Tekton components, I'd
  recommend the following approach, built on your existing vanilla JavaScript architecture:

  Core Design Elements

  1. Scrollable Container: A dedicated div with fixed height, overflow-y set to auto, and
  flex-direction: column-reverse (to keep newest content visible)
  2. Message Types: Different styling for:
    - User messages
    - AI responses
    - System notifications
    - Command outputs (if applicable)
  3. Real-time Updates: WebSocket connection to stream AI responses with typing indicators

  Implementation Steps

  1. HTML Structure

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

  2. CSS Styling

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

  3. JavaScript Functions

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
    const conversationHistory =
  JSON.parse(localStorage.getItem(`tekton_conversation_${componentId}`) || '[]');
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
    const conversationHistory =
  JSON.parse(localStorage.getItem(`tekton_conversation_${componentId}`) || '[]');
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

  // Setup WebSocket handlers for receiving AI messages
  function setupWebSocketHandlers(componentId) {
    // Get existing WebSocket or create new one
    const ws = window.tektonWebSocket || new WebSocket(`ws://localhost:8081`);
    window.tektonWebSocket = ws;

    ws.addEventListener('message', function(event) {
      const message = JSON.parse(event.data);

      // Only process messages for current component
      if (message.target !== componentId && message.target !== 'UI') return;

      if (message.type === 'RESPONSE') {
        if (message.payload.typing_start) {
          showTypingIndicator();
        } else if (message.payload.typing_end) {
          hideTypingIndicator();
        } else if (message.payload.message) {
          addAIMessage(componentId, message.payload.message);
        }
      } else if (message.type === 'ERROR') {
        addSystemMessage(componentId, `Error: ${message.payload.message}`);
      }
    });

    // Handle connection errors
    ws.addEventListener('error', function(error) {
      addSystemMessage(componentId, "Connection error. Please refresh the page.");
    });

    // Handle reconnection
    ws.addEventListener('close', function() {
      addSystemMessage(componentId, "Connection closed. Attempting to reconnect...");
      setTimeout(() => {
        setupWebSocketHandlers(componentId);
      }, 2000);
    });
  }

  // Handle sending messages
  function sendMessage(componentId, message) {
    // Add to UI immediately
    addUserMessage(componentId, message);

    // Send via WebSocket
    const ws = window.tektonWebSocket;
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({
        type: "COMMAND",
        source: "UI",
        target: componentId,
        timestamp: new Date().toISOString(),
        payload: {
          command: "process_message",
          message: message
        }
      }));
    } else {
      addSystemMessage(componentId, "Connection issue. Message not sent.");
      hideTypingIndicator();
    }
  }

  4. WebSocket Protocol for Streaming Responses

  For a smooth typing effect, you could implement a protocol extension where the AI can send partial
   response updates:

  // On the server side, send typing indicator
  ws.send(JSON.stringify({
    type: "RESPONSE",
    source: "componentId",
    target: "UI",
    timestamp: new Date().toISOString(),
    payload: {
      typing_start: true
    }
  }));

  // Send chunks as they become available
  for (const chunk of responseChunks) {
    ws.send(JSON.stringify({
      type: "RESPONSE",
      source: "componentId",
      target: "UI",
      timestamp: new Date().toISOString(),
      payload: {
        message_chunk: chunk
      }
    }));

    // Simulate typing delay
    await new Promise(resolve => setTimeout(resolve, calculateTypingDelay(chunk)));
  }

  // End typing
  ws.send(JSON.stringify({
    type: "RESPONSE",
    source: "componentId",
    target: "UI",
    timestamp: new Date().toISOString(),
    payload: {
      typing_end: true,
      message: completeMessage // Send the full message at the end
    }
  }));

  Integration with Existing UI

  To integrate this terminal into your component tab system:

  1. Create a template for the AI tab in /ui/components/:

  <!-- ergon-ai-tab.html -->
  <div class="ai-terminal-wrapper">
    <div class="terminal-controls">
      <button id="clear-terminal" class="control-button">Clear Chat</button>
      <button id="copy-terminal" class="control-button">Copy to Clipboard</button>
    </div>
    <div class="ai-terminal-container">
      <div id="ai-terminal-messages" class="ai-terminal-messages">
        <!-- Messages will be added here dynamically -->
      </div>
      <div class="ai-terminal-status">
        <div id="ai-typing-indicator" class="ai-typing hidden">
          <span class="dot"></span><span class="dot"></span><span class="dot"></span>
        </div>
      </div>
    </div>
  </div>

  2. Update the component's script to load and initialize the terminal:

  window.ergonComponent = {
    // ... existing code ...

    // Initialize AI tab
    initializeAITab: function() {
      // Load the AI tab template
      fetch('components/ergon-ai-tab.html')
        .then(response => response.text())
        .then(html => {
          const aiTabContainer = document.getElementById('ergon-ai-tab');
          aiTabContainer.innerHTML = html;

          // Initialize terminal
          initAITerminal('ergon');

          // Load past conversation
          loadConversation('ergon');

          // Set up WebSocket handlers
          setupWebSocketHandlers('ergon');

          // Set up control buttons
          document.getElementById('clear-terminal').addEventListener('click', () => {
            document.getElementById('ai-terminal-messages').innerHTML = '';
            localStorage.removeItem('tekton_conversation_ergon');
            addSystemMessage('ergon', 'Conversation cleared');
          });

          document.getElementById('copy-terminal').addEventListener('click', () => {
            const messages = document.querySelectorAll('.ai-terminal-messages .message');
            let text = '';
            messages.forEach(message => {
              if (message.classList.contains('message-user')) {
                text += `User: ${message.textContent}\n\n`;
              } else if (message.classList.contains('message-ai')) {
                text += `Ergon AI: ${message.textContent}\n\n`;
              }
            });
            navigator.clipboard.writeText(text).then(() => {
              addSystemMessage('ergon', 'Conversation copied to clipboard');
            });
          });
        });
    }
  };

  3. Ensure the chat input in the footer connects to the active component:

  document.getElementById('send-button').addEventListener('click', function() {
    const inputField = document.getElementById('chat-input');
    const message = inputField.value.trim();

    if (message) {
      const activeComponent = window.activeComponent; // You should track this globally
      sendMessage(activeComponent, message);
      inputField.value = ''; // Clear input
    }
  });

  // Handle Enter key
  document.getElementById('chat-input').addEventListener('keydown', function(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      document.getElementById('send-button').click();
    }
  });

  Special Features to Consider

  1. Markdown Support: Use a library like marked.js for rich formatting in AI responses
  2. Code Highlighting: Add syntax highlighting for code blocks with highlight.js
  3. Multiple AI Personalities: Add subtle visual cues for different AI personalities
  4. Conversation Exports: Allow saving chat logs to files
  5. Threading View: For related message chains
  6. Typing Indicators: Show when AI is generating a response

  Hermes Integration

  Your existing WebSocket handlers already connect to Hermes. The key is ensuring proper message
  routing:

  1. Each component's AI terminal connects to its specific AI via Hermes
  2. When in AI_TEAM mode, the primary AI should coordinate with other AIs through Hermes
  3. All AI responses back to UI should come through the same WebSocket connection

  This approach gives you a clean, maintainable terminal interface that integrates well with your
  existing architecture while providing an excellent user experience.


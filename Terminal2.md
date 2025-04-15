You're right - this is a simpler approach than I initially described. Let me clarify and simplify
  based on your needs:

  Simplified Terminal Chat Interface

  What we're building is essentially an HTML-based chat display that looks like a terminal but isn't
   an actual terminal emulator. This will occupy only the right panel of the UI, and each component
  (Ergon, Athena, etc.) has its own chat history.

  Here's how it fits together in a simplified way:

  1. Navigation and Component Structure

  1. Left Panel Navigation: User clicks "Ergon" in the left panel
  2. Right Panel Updates:
    - Component title changes to "Ergon"
    - Right panel shows the Ergon UI with tabs
    - One tab is "Ergon AI" for the chat interface
    - Initial greeting message appears

  2. Chat Flow

  1. User Input: User types in the chat input at the bottom (shared across all components)
  2. Send Button: User clicks Send or presses Enter
  3. Message Routing:
    - Current active component receives the message
    - WebSocket sends the message to the correct AI backend
  4. AI Response:
    - Received via WebSocket
    - Displayed in the active component's chat area
    - Formatted with proper markdown/styling

  3. Simple Terminal Implementation

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
      return `<pre class="code-block${language ? ` language-${language}` : 
  ''}"><code>${code}</code></pre>`;
    });

    // Handle bold
    message = message.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

    // Handle italics
    message = message.replace(/\*(.*?)\*/g, '<em>$1</em>');

    return message;
  }

  // Save chat message to history
  function saveChatMessage(componentId, role, content) {
    const history = JSON.parse(localStorage.getItem(`tekton_chat_${componentId}`) || '[]');
    history.push({ role, content, timestamp: new Date().toISOString() });
    localStorage.setItem(`tekton_chat_${componentId}`, JSON.stringify(history));
  }

  // Load chat history for component
  function loadComponentChatHistory(componentId) {
    const history = JSON.parse(localStorage.getItem(`tekton_chat_${componentId}`) || '[]');
    const terminalContainer = document.getElementById('terminal');

    // Clear terminal
    terminalContainer.innerHTML = '';

    // Display each message
    history.forEach(message => {
      if (message.role === 'user') {
        const messageElement = document.createElement('div');
        messageElement.className = 'user-message';
        messageElement.innerHTML = `<span class="user-prefix">You:</span> ${message.content}`;
        terminalContainer.appendChild(messageElement);
      } else {
        const messageElement = document.createElement('div');
        messageElement.className = 'ai-message';
        const formattedMessage = formatMessage(message.content);
        messageElement.innerHTML = `<span class="ai-prefix">${componentId}:</span> 
  ${formattedMessage}`;
        terminalContainer.appendChild(messageElement);
      }
    });

    // Scroll to bottom
    terminalContainer.scrollTop = terminalContainer.scrollHeight;
  }

  // Handle send button click
  document.getElementById('send-button').addEventListener('click', function() {
    const inputField = document.getElementById('chat-input');
    const message = inputField.value.trim();

    if (message) {
      // Display user message
      displayUserMessage(message);

      // Clear input field
      inputField.value = '';

      // Clear draft
      localStorage.removeItem(`tekton_draft_${window.activeComponent}`);

      // Send to AI via WebSocket
      sendToAI(window.activeComponent, message);
    }
  });

  // Send message to AI
  function sendToAI(componentId, message) {
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
      // Handle connection issue
      displayAIMessage(componentId, "Connection issue. Please refresh the page.");
    }
  }

  // Get greeting message for component
  function getGreetingForComponent(componentId) {
    const greetings = {
      'ergon': "Hello! I'm Ergon, your agent and workflow assistant. How can I help you today?",
      'athena': "Welcome to Athena. I can help you with knowledge graph queries and information 
  retrieval.",
      'prometheus': "Prometheus planning assistant at your service. What would you like to plan 
  today?",
      // Add more greetings for other components
    };

    return greetings[componentId] || `Welcome to ${componentId}. How can I assist you?`;
  }

  4. CSS for Simple Chat UI

  /* Terminal chat styling */
  .terminal {
    height: 100%;
    overflow-y: auto;
    padding: 12px;
    font-family: 'Menlo', 'Monaco', 'Courier New', monospace;
    font-size: 14px;
    line-height: 1.4;
    color: #f0f0f0;
    background-color: #1e1e1e;
  }

  /* User messages */
  .user-message {
    margin: 8px 0;
    padding: 8px 12px;
    border-radius: 4px;
    background-color: rgba(0, 123, 255, 0.2);
    border-left: 3px solid #007bff;
  }

  .user-prefix {
    font-weight: bold;
    color: #007bff;
    margin-right: 8px;
  }

  /* AI messages */
  .ai-message {
    margin: 8px 0;
    padding: 8px 12px;
    border-radius: 4px;
    background-color: rgba(75, 75, 75, 0.3);
    border-left: 3px solid #aaa;
  }

  .ai-prefix {
    font-weight: bold;
    color: #4CAF50;
    margin-right: 8px;
  }

  /* Code blocks */
  .code-block {
    background-color: rgba(0, 0, 0, 0.3);
    padding: 12px;
    border-radius: 4px;
    overflow-x: auto;
    margin: 8px 0;
  }

  /* Make the terminal scrollable but keep the input fixed */
  .content-main {
    display: flex;
    flex-direction: column;
  }

  .terminal-panel {
    flex: 1;
    overflow: hidden;
  }

  5. Connecting Component UIs and AIs

  Each component has its own section in the UI, but they all share the same chat input at the
  bottom. The key is to track which component is currently active and route messages accordingly:

  // Component tab system example (for Ergon)
  document.addEventListener('DOMContentLoaded', function() {
    // Set up tab switching
    const tabButtons = document.querySelectorAll('.component-tab-button');
    tabButtons.forEach(button => {
      button.addEventListener('click', function() {
        const tabId = this.getAttribute('data-tab');

        // Hide all tabs
        document.querySelectorAll('.component-tab-content').forEach(tab => {
          tab.classList.remove('active');
        });

        // Show selected tab
        document.getElementById(tabId).classList.add('active');

        // Update active tab
        tabButtons.forEach(btn => btn.classList.remove('active'));
        this.classList.add('active');
      });
    });

    // Connect AI tab with terminal
    document.querySelector('[data-tab="ergon-ai-tab"]').addEventListener('click', function() {
      // Ensure terminal is visible
      document.getElementById('terminal-panel').classList.add('active');
      document.getElementById('html-panel').classList.remove('active');
    });

    // Connect other tabs with HTML panel
    document.querySelector('[data-tab="ergon-agents-tab"]').addEventListener('click', function() {
      // Show HTML panel instead of terminal
      document.getElementById('terminal-panel').classList.remove('active');
      document.getElementById('html-panel').classList.add('active');

      // Load agents UI
      loadAgentsUI();
    });
  });

  6. WebSocket Communication

  // Set up WebSocket connection
  function initializeWebSocket() {
    const ws = new WebSocket('ws://localhost:8081');

    ws.addEventListener('open', function() {
      console.log('WebSocket connected');
    });

    ws.addEventListener('message', function(event) {
      try {
        const message = JSON.parse(event.data);

        // Only process messages for current component or UI
        if (message.target !== window.activeComponent && message.target !== 'UI') return;

        if (message.type === 'RESPONSE') {
          if (message.payload.message) {
            displayAIMessage(message.source, message.payload.message);
          }
        } else if (message.type === 'ERROR') {
          displayAIMessage(message.source || 'System', `Error: ${message.payload.message}`);
        }
      } catch (error) {
        console.error('Error processing message:', error);
      }
    });

    ws.addEventListener('close', function() {
      console.log('WebSocket disconnected');
      // Reconnect after delay
      setTimeout(initializeWebSocket, 3000);
    });

    window.tektonWebSocket = ws;
  }

  This simplified approach maintains the key aspects you need:

  1. Component-specific chat histories
  2. Shared input field with context saving
  3. Proper message routing to the correct AI
  4. Simple but attractive display of messages
  5. Basic markdown formatting for code and styling

  The terminal is really just a styled div that displays messages in a chat-like format, but with
  terminal aesthetics. It's very similar to the Claude Code interface you're familiar with - clean,
  simple, and focused on the conversation.


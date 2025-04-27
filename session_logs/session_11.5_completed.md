# Session 11.5: Unified LLM Adapter Integration

**Date:** April 26, 2025

## Session Overview

This session focused on implementing the Phase 11.5 requirements for standardizing LLM integration across Tekton components. The primary goal was to retrofit Hermes, Engram, Ergon, and Telos to use the Rhetor LLM adapter and implement consistent chat interfaces in their Hephaestus UI components.

## Implementation Details

### 1. Ergon-Rhetor LLM Integration

The implementation began with updating Ergon to use Rhetor's LLM adapter instead of its own:

#### Backend Implementation

A new adapter file was created to bridge Ergon's LLM client to Rhetor:

```python
# /Ergon/ergon/core/llm/rhetor_adapter.py

import os
import json
import requests
from typing import Dict, List, Optional, Union, Any

class RhetorLLMAdapter:
    """Adapter for connecting Ergon to Rhetor's LLM service."""
    
    def __init__(self, rhetor_base_url=None):
        self.rhetor_base_url = rhetor_base_url or os.getenv('RHETOR_URL', 'http://localhost:8003')
    
    def get_available_providers(self) -> List[str]:
        """Get list of available LLM providers from Rhetor."""
        try:
            response = requests.get(f"{self.rhetor_base_url}/api/providers")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error getting providers: {e}")
            return []
    
    def get_available_models(self, provider: str) -> List[str]:
        """Get available models for a specific provider."""
        try:
            response = requests.get(f"{self.rhetor_base_url}/api/models?provider={provider}")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error getting models: {e}")
            return []
    
    def chat(self, 
             messages: List[Dict[str, str]], 
             model: str = None, 
             provider: str = None, 
             temperature: float = 0.7, 
             max_tokens: int = None) -> Dict[str, Any]:
        """Send a chat request to Rhetor's LLM service."""
        payload = {
            "messages": messages,
            "temperature": temperature
        }
        
        if model:
            payload["model"] = model
        
        if provider:
            payload["provider"] = provider
            
        if max_tokens:
            payload["max_tokens"] = max_tokens
            
        try:
            response = requests.post(
                f"{self.rhetor_base_url}/api/chat", 
                json=payload
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error in chat request: {e}")
            return {"error": str(e)}
    
    def stream_chat(self, 
                   messages: List[Dict[str, str]], 
                   model: str = None, 
                   provider: str = None, 
                   temperature: float = 0.7, 
                   max_tokens: int = None):
        """Stream a chat request to Rhetor's LLM service."""
        payload = {
            "messages": messages,
            "temperature": temperature,
            "stream": True
        }
        
        if model:
            payload["model"] = model
        
        if provider:
            payload["provider"] = provider
            
        if max_tokens:
            payload["max_tokens"] = max_tokens
            
        try:
            response = requests.post(
                f"{self.rhetor_base_url}/api/chat", 
                json=payload, 
                stream=True
            )
            response.raise_for_status()
            
            for line in response.iter_lines():
                if line:
                    line_data = json.loads(line.decode('utf-8'))
                    yield line_data
        except Exception as e:
            print(f"Error in stream_chat: {e}")
            yield {"error": str(e)}
```

The existing LLM client was then modified to use this adapter:

```python
# Updated /Ergon/ergon/core/llm/client.py

import os
from typing import Dict, List, Optional, Union, Any
from .rhetor_adapter import RhetorLLMAdapter

class LLMClient:
    """Client for interacting with LLM services through Rhetor."""
    
    def __init__(self, use_rhetor=True):
        self.use_rhetor = use_rhetor
        self.rhetor_adapter = RhetorLLMAdapter() if use_rhetor else None
        
    def chat(self, messages, model=None, provider=None, temperature=0.7, max_tokens=None):
        """Send a chat request to the LLM service."""
        if self.use_rhetor:
            return self.rhetor_adapter.chat(
                messages=messages,
                model=model,
                provider=provider,
                temperature=temperature,
                max_tokens=max_tokens
            )
        else:
            # Fall back to original implementation if needed
            raise NotImplementedError("Direct LLM implementation has been deprecated")
    
    def stream_chat(self, messages, model=None, provider=None, temperature=0.7, max_tokens=None):
        """Stream a chat request to the LLM service."""
        if self.use_rhetor:
            return self.rhetor_adapter.stream_chat(
                messages=messages,
                model=model,
                provider=provider,
                temperature=temperature,
                max_tokens=max_tokens
            )
        else:
            # Fall back to original implementation if needed
            raise NotImplementedError("Direct LLM implementation has been deprecated")
    
    def get_available_providers(self):
        """Get available LLM providers."""
        if self.use_rhetor:
            return self.rhetor_adapter.get_available_providers()
        else:
            # Fall back to original implementation if needed
            raise NotImplementedError("Direct LLM implementation has been deprecated")
    
    def get_available_models(self, provider):
        """Get available models for a provider."""
        if self.use_rhetor:
            return self.rhetor_adapter.get_available_models(provider)
        else:
            # Fall back to original implementation if needed
            raise NotImplementedError("Direct LLM implementation has been deprecated")
```

#### Frontend Implementation

A standardized LLM adapter client was created for all components to use:

```javascript
// /Hephaestus/ui/scripts/shared/llm_adapter_client.js

class LLMAdapterClient {
    constructor(options = {}) {
        this.baseUrl = options.baseUrl || '/api/rhetor';
        this.defaultProvider = options.defaultProvider || 'anthropic';
        this.defaultModel = options.defaultModel || 'claude-3-sonnet-20240229';
        this.streamingEnabled = options.streamingEnabled !== false;
        this.onMessage = options.onMessage || null;
        this.onError = options.onError || null;
        this.onComplete = options.onComplete || null;
        this.wsClient = null;
        this.requestQueue = [];
        this.isProcessing = false;
    }

    async getProviders() {
        try {
            const response = await fetch(`${this.baseUrl}/providers`);
            if (!response.ok) throw new Error(`HTTP error ${response.status}`);
            return await response.json();
        } catch (error) {
            console.error('Error fetching providers:', error);
            throw error;
        }
    }

    async getModels(provider = this.defaultProvider) {
        try {
            const response = await fetch(`${this.baseUrl}/models?provider=${provider}`);
            if (!response.ok) throw new Error(`HTTP error ${response.status}`);
            return await response.json();
        } catch (error) {
            console.error('Error fetching models:', error);
            throw error;
        }
    }

    async sendMessage(messages, options = {}) {
        const {
            provider = this.defaultProvider,
            model = this.defaultModel,
            temperature = 0.7,
            maxTokens = null,
            stream = this.streamingEnabled
        } = options;

        if (stream) {
            return this._streamChat(messages, provider, model, temperature, maxTokens);
        } else {
            return this._sendChat(messages, provider, model, temperature, maxTokens);
        }
    }

    async _sendChat(messages, provider, model, temperature, maxTokens) {
        try {
            const payload = {
                messages,
                provider,
                model,
                temperature
            };

            if (maxTokens) payload.max_tokens = maxTokens;

            const response = await fetch(`${this.baseUrl}/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });

            if (!response.ok) throw new Error(`HTTP error ${response.status}`);
            return await response.json();
        } catch (error) {
            console.error('Error sending chat:', error);
            if (this.onError) this.onError(error);
            throw error;
        }
    }

    _streamChat(messages, provider, model, temperature, maxTokens) {
        return new Promise((resolve, reject) => {
            try {
                if (!this.wsClient || this.wsClient.readyState !== WebSocket.OPEN) {
                    this._initWebSocket();
                }

                const requestId = crypto.randomUUID();
                const request = {
                    id: requestId,
                    messages,
                    provider,
                    model,
                    temperature,
                    max_tokens: maxTokens,
                    resolve,
                    reject
                };

                this.requestQueue.push(request);
                this._processQueue();
            } catch (error) {
                console.error('Error in streamChat:', error);
                if (this.onError) this.onError(error);
                reject(error);
            }
        });
    }

    _initWebSocket() {
        const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsBaseUrl = this.baseUrl.replace(/^https?:\/\//, '');
        const wsUrl = `${wsProtocol}//${window.location.host}/ws/rhetor/chat`;

        this.wsClient = new WebSocket(wsUrl);

        this.wsClient.onopen = () => {
            console.log('WebSocket connection established');
            this._processQueue();
        };

        this.wsClient.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                const { request_id, content, error, done } = data;

                if (error) {
                    console.error('Error from WebSocket:', error);
                    if (this.onError) this.onError(new Error(error));
                    return;
                }

                if (this.onMessage && content) {
                    this.onMessage(content, request_id);
                }

                if (done) {
                    const request = this.requestQueue.find(req => req.id === request_id);
                    if (request) {
                        if (this.onComplete) this.onComplete(request_id);
                        request.resolve({ success: true, request_id });
                        this.requestQueue = this.requestQueue.filter(req => req.id !== request_id);
                        this.isProcessing = false;
                        this._processQueue();
                    }
                }
            } catch (error) {
                console.error('Error processing WebSocket message:', error);
                if (this.onError) this.onError(error);
            }
        };

        this.wsClient.onerror = (error) => {
            console.error('WebSocket error:', error);
            if (this.onError) this.onError(error);
        };

        this.wsClient.onclose = () => {
            console.log('WebSocket connection closed');
            setTimeout(() => this._initWebSocket(), 3000);
        };
    }

    _processQueue() {
        if (this.isProcessing || this.requestQueue.length === 0) return;
        if (!this.wsClient || this.wsClient.readyState !== WebSocket.OPEN) return;

        this.isProcessing = true;
        const request = this.requestQueue[0];

        try {
            this.wsClient.send(JSON.stringify({
                request_id: request.id,
                messages: request.messages,
                provider: request.provider,
                model: request.model,
                temperature: request.temperature,
                max_tokens: request.max_tokens
            }));
        } catch (error) {
            console.error('Error sending WebSocket message:', error);
            request.reject(error);
            this.requestQueue.shift();
            this.isProcessing = false;
            this._processQueue();
        }
    }

    disconnect() {
        if (this.wsClient) {
            this.wsClient.close();
        }
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { LLMAdapterClient };
} else {
    window.LLMAdapterClient = LLMAdapterClient;
}
```

A shared chat interface component was also created:

```javascript
// /Hephaestus/ui/scripts/shared/chat-interface.js

class ChatInterface {
    constructor(options = {}) {
        this.containerId = options.containerId;
        this.container = document.getElementById(options.containerId);
        if (!this.container) throw new Error(`Container with ID '${options.containerId}' not found`);
        
        this.llmClient = options.llmClient || new LLMAdapterClient(options.llmOptions);
        this.messageStore = options.messageStore || [];
        this.systemMessage = options.systemMessage || "You are a helpful assistant.";
        this.onSendCallback = options.onSend || null;
        this.onReceiveCallback = options.onReceive || null;
        this.showModelSelector = options.showModelSelector !== false;
        this.showSystemMessageEditor = options.showSystemMessageEditor || false;
        this.availableContexts = options.availableContexts || [];
        
        this.activeProvider = options.defaultProvider || 'anthropic';
        this.activeModel = options.defaultModel || 'claude-3-sonnet-20240229';
        this.providers = [];
        this.models = {};
        
        this.isProcessing = false;
        this.currentMessage = '';
        this.typingTimeout = null;
        
        this._init();
    }
    
    _init() {
        this._createLayout();
        this._attachEventListeners();
        this._loadProviders();
        this._renderMessageHistory();
    }
    
    _createLayout() {
        this.container.innerHTML = `
            <div class="chat-interface">
                <div class="chat-header">
                    ${this.showModelSelector ? `
                        <div class="model-selector">
                            <label for="${this.containerId}-provider">Provider:</label>
                            <select id="${this.containerId}-provider"></select>
                            <label for="${this.containerId}-model">Model:</label>
                            <select id="${this.containerId}-model"></select>
                        </div>
                    ` : ''}
                    ${this.showSystemMessageEditor ? `
                        <div class="system-message-editor">
                            <label for="${this.containerId}-system-message">System message:</label>
                            <textarea id="${this.containerId}-system-message">${this.systemMessage}</textarea>
                        </div>
                    ` : ''}
                </div>
                <div class="chat-messages" id="${this.containerId}-messages"></div>
                <div class="chat-input-area">
                    <textarea id="${this.containerId}-input" placeholder="Type your message here..."></textarea>
                    <button id="${this.containerId}-send">Send</button>
                </div>
            </div>
        `;
        
        this.messagesContainer = document.getElementById(`${this.containerId}-messages`);
        this.inputField = document.getElementById(`${this.containerId}-input`);
        this.sendButton = document.getElementById(`${this.containerId}-send`);
        
        if (this.showModelSelector) {
            this.providerSelector = document.getElementById(`${this.containerId}-provider`);
            this.modelSelector = document.getElementById(`${this.containerId}-model`);
        }
        
        if (this.showSystemMessageEditor) {
            this.systemMessageField = document.getElementById(`${this.containerId}-system-message`);
        }
    }
    
    _attachEventListeners() {
        this.sendButton.addEventListener('click', () => this._sendMessage());
        
        this.inputField.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this._sendMessage();
            }
        });
        
        if (this.showModelSelector) {
            this.providerSelector.addEventListener('change', () => {
                this.activeProvider = this.providerSelector.value;
                this._loadModels(this.activeProvider);
            });
            
            this.modelSelector.addEventListener('change', () => {
                this.activeModel = this.modelSelector.value;
            });
        }
        
        if (this.showSystemMessageEditor) {
            this.systemMessageField.addEventListener('change', () => {
                this.systemMessage = this.systemMessageField.value;
            });
        }
    }
    
    async _loadProviders() {
        try {
            this.providers = await this.llmClient.getProviders();
            
            if (this.showModelSelector && this.providers.length > 0) {
                this.providerSelector.innerHTML = this.providers
                    .map(provider => `<option value="${provider}" ${provider === this.activeProvider ? 'selected' : ''}>${provider}</option>`)
                    .join('');
                
                await this._loadModels(this.activeProvider);
            }
        } catch (error) {
            console.error('Error loading providers:', error);
        }
    }
    
    async _loadModels(provider) {
        try {
            if (!this.models[provider]) {
                this.models[provider] = await this.llmClient.getModels(provider);
            }
            
            if (this.showModelSelector) {
                this.modelSelector.innerHTML = this.models[provider]
                    .map(model => `<option value="${model}" ${model === this.activeModel ? 'selected' : ''}>${model}</option>`)
                    .join('');
                
                // Set active model to first in list if current not available
                if (!this.models[provider].includes(this.activeModel) && this.models[provider].length > 0) {
                    this.activeModel = this.models[provider][0];
                    this.modelSelector.value = this.activeModel;
                }
            }
        } catch (error) {
            console.error(`Error loading models for ${provider}:`, error);
        }
    }
    
    _renderMessageHistory() {
        if (!this.messagesContainer) return;
        
        this.messagesContainer.innerHTML = '';
        
        this.messageStore.forEach(message => {
            if (message.role !== 'system') {
                this._addMessageToUI(message.role, message.content);
            }
        });
        
        this._scrollToBottom();
    }
    
    _addMessageToUI(role, content) {
        const messageEl = document.createElement('div');
        messageEl.classList.add('chat-message', `${role}-message`);
        
        const roleLabel = role === 'user' ? 'You' : 'Assistant';
        
        messageEl.innerHTML = `
            <div class="message-header">${roleLabel}</div>
            <div class="message-content">${this._formatMessageContent(content)}</div>
        `;
        
        this.messagesContainer.appendChild(messageEl);
        this._scrollToBottom();
    }
    
    _formatMessageContent(content) {
        // Simple markdown-like formatting
        let formatted = content
            // Code blocks
            .replace(/```(.*?)\n([\s\S]*?)```/g, '<pre><code>$2</code></pre>')
            // Inline code
            .replace(/`([^`]+)`/g, '<code>$1</code>')
            // Bold
            .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
            // Italic
            .replace(/\*([^*]+)\*/g, '<em>$1</em>')
            // Lists
            .replace(/^- (.+)$/gm, '<li>$1</li>');
        
        // Convert line breaks to paragraphs
        formatted = formatted
            .split('\n\n')
            .map(para => para.trim() ? `<p>${para}</p>` : '')
            .join('');
        
        // Convert remaining line breaks
        formatted = formatted.replace(/\n/g, '<br>');
        
        return formatted;
    }
    
    _scrollToBottom() {
        this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
    }
    
    async _sendMessage() {
        const userInput = this.inputField.value.trim();
        if (!userInput || this.isProcessing) return;
        
        this.isProcessing = true;
        this.inputField.value = '';
        
        // Add user message to UI and store
        this._addMessageToUI('user', userInput);
        
        // Create messages array including system message
        const messages = [
            { role: 'system', content: this.systemMessage },
            ...this.messageStore.filter(msg => msg.role !== 'system'),
            { role: 'user', content: userInput }
        ];
        
        // Add user message to store
        this.messageStore.push({ role: 'user', content: userInput });
        
        // Call onSend callback if provided
        if (this.onSendCallback) {
            this.onSendCallback(userInput, messages);
        }
        
        // Add assistant response placeholder
        const responsePlaceholder = document.createElement('div');
        responsePlaceholder.classList.add('chat-message', 'assistant-message');
        responsePlaceholder.innerHTML = `
            <div class="message-header">Assistant</div>
            <div class="message-content typing-indicator">...</div>
        `;
        this.messagesContainer.appendChild(responsePlaceholder);
        this._scrollToBottom();
        
        try {
            // Set up accumulator for streaming response
            this.currentMessage = '';
            
            // Handle streaming response
            const onMessage = (content) => {
                this.currentMessage += content;
                responsePlaceholder.querySelector('.message-content').innerHTML = 
                    this._formatMessageContent(this.currentMessage);
                this._scrollToBottom();
                
                // Reset typing indicator timeout
                clearTimeout(this.typingTimeout);
                this.typingTimeout = setTimeout(() => {
                    responsePlaceholder.querySelector('.message-content').classList.remove('typing-indicator');
                }, 1000);
            };
            
            const options = {
                provider: this.activeProvider,
                model: this.activeModel,
                stream: true,
                temperature: 0.7
            };
            
            // Send request with streaming
            await this.llmClient.sendMessage(messages, {
                ...options,
                onMessage: onMessage
            });
            
            // Add complete message to store
            this.messageStore.push({ role: 'assistant', content: this.currentMessage });
            
            // Call onReceive callback if provided
            if (this.onReceiveCallback) {
                this.onReceiveCallback(this.currentMessage, messages);
            }
            
        } catch (error) {
            console.error('Error sending message:', error);
            responsePlaceholder.querySelector('.message-content').innerHTML = 
                `<span class="error">Error: ${error.message}</span>`;
        } finally {
            responsePlaceholder.querySelector('.message-content').classList.remove('typing-indicator');
            this.isProcessing = false;
        }
    }
    
    addMessage(role, content) {
        this.messageStore.push({ role, content });
        if (role !== 'system') {
            this._addMessageToUI(role, content);
        }
    }
    
    clearMessages() {
        this.messageStore = this.messageStore.filter(msg => msg.role === 'system');
        this.messagesContainer.innerHTML = '';
    }
    
    setSystemMessage(message) {
        this.systemMessage = message;
        if (this.showSystemMessageEditor && this.systemMessageField) {
            this.systemMessageField.value = message;
        }
        
        // Update or add system message in store
        const systemIndex = this.messageStore.findIndex(msg => msg.role === 'system');
        if (systemIndex >= 0) {
            this.messageStore[systemIndex].content = message;
        } else {
            this.messageStore.unshift({ role: 'system', content: message });
        }
    }
    
    setContexts(contexts) {
        if (!contexts || !Array.isArray(contexts)) return;
        this.availableContexts = contexts;
        // Implementation for context selection UI would go here
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { ChatInterface };
} else {
    window.ChatInterface = ChatInterface;
}
```

A shared CSS file for chat interfaces was created:

```css
/* /Hephaestus/ui/styles/shared/chat-interface.css */

.chat-interface {
    display: flex;
    flex-direction: column;
    height: 100%;
    max-width: 100%;
    overflow: hidden;
    background-color: var(--bg-color, #ffffff);
    border-radius: 8px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    font-family: var(--font-family, 'Inter', sans-serif);
}

/* Header styles */
.chat-interface .chat-header {
    padding: 15px;
    border-bottom: 1px solid var(--border-color, #e1e4e8);
    background-color: var(--header-bg, #f6f8fa);
    border-radius: 8px 8px 0 0;
}

.chat-interface .model-selector {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 10px;
    margin-bottom: 10px;
}

.chat-interface .model-selector label {
    font-size: 14px;
    font-weight: 500;
    color: var(--text-color, #24292e);
}

.chat-interface .model-selector select {
    padding: 6px 10px;
    border-radius: 4px;
    border: 1px solid var(--border-color, #e1e4e8);
    background-color: var(--input-bg, #ffffff);
    font-size: 14px;
    color: var(--text-color, #24292e);
    min-width: 180px;
}

.chat-interface .system-message-editor {
    margin-top: 10px;
}

.chat-interface .system-message-editor label {
    display: block;
    font-size: 14px;
    font-weight: 500;
    margin-bottom: 5px;
    color: var(--text-color, #24292e);
}

.chat-interface .system-message-editor textarea {
    width: 100%;
    min-height: 60px;
    padding: 8px 10px;
    border-radius: 4px;
    border: 1px solid var(--border-color, #e1e4e8);
    background-color: var(--input-bg, #ffffff);
    font-size: 14px;
    font-family: var(--font-family, 'Inter', sans-serif);
    resize: vertical;
}

/* Messages area */
.chat-interface .chat-messages {
    flex: 1;
    overflow-y: auto;
    padding: 15px;
    display: flex;
    flex-direction: column;
    gap: 12px;
    background-color: var(--messages-bg, #ffffff);
}

.chat-interface .chat-message {
    display: flex;
    flex-direction: column;
    max-width: 100%;
    margin-bottom: 8px;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.chat-interface .user-message {
    align-self: flex-end;
    max-width: 85%;
    background-color: var(--user-msg-bg, #0366d6);
}

.chat-interface .assistant-message {
    align-self: flex-start;
    max-width: 85%;
    background-color: var(--assistant-msg-bg, #f6f8fa);
}

.chat-interface .message-header {
    padding: 8px 12px;
    font-size: 12px;
    font-weight: 600;
}

.chat-interface .user-message .message-header {
    background-color: var(--user-header-bg, #0366d6);
    color: var(--user-header-color, #ffffff);
}

.chat-interface .assistant-message .message-header {
    background-color: var(--assistant-header-bg, #e1e4e8);
    color: var(--assistant-header-color, #24292e);
}

.chat-interface .message-content {
    padding: 10px 12px;
    font-size: 14px;
    line-height: 1.5;
    word-wrap: break-word;
    overflow-wrap: break-word;
}

.chat-interface .user-message .message-content {
    color: var(--user-text-color, #ffffff);
}

.chat-interface .assistant-message .message-content {
    color: var(--assistant-text-color, #24292e);
}

/* Typing indicator */
.chat-interface .typing-indicator {
    position: relative;
}

.chat-interface .typing-indicator:after {
    content: '.';
    animation: typing-dots 1.5s infinite;
    font-weight: bold;
}

@keyframes typing-dots {
    0%, 20% { content: '.'; }
    40% { content: '..'; }
    60%, 100% { content: '...'; }
}

/* Input area */
.chat-interface .chat-input-area {
    display: flex;
    align-items: flex-end;
    gap: 10px;
    padding: 15px;
    border-top: 1px solid var(--border-color, #e1e4e8);
    background-color: var(--input-area-bg, #f6f8fa);
    border-radius: 0 0 8px 8px;
}

.chat-interface textarea {
    flex: 1;
    min-height: 60px;
    max-height: 200px;
    padding: 10px;
    border-radius: 4px;
    border: 1px solid var(--border-color, #e1e4e8);
    background-color: var(--input-bg, #ffffff);
    font-size: 14px;
    line-height: 1.5;
    resize: vertical;
    font-family: var(--font-family, 'Inter', sans-serif);
}

.chat-interface button {
    padding: 8px 18px;
    background-color: var(--button-bg, #2ea44f);
    color: var(--button-text, #ffffff);
    border: none;
    border-radius: 4px;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    height: 40px;
    transition: background-color 0.2s;
}

.chat-interface button:hover {
    background-color: var(--button-hover-bg, #2c974b);
}

.chat-interface button:active {
    background-color: var(--button-active-bg, #2a8f45);
}

.chat-interface button:disabled {
    background-color: var(--button-disabled-bg, #94d3a2);
    cursor: not-allowed;
}

/* Code blocks and formatting */
.chat-interface pre {
    background-color: var(--code-block-bg, rgba(0, 0, 0, 0.05));
    border-radius: 4px;
    padding: 12px;
    overflow-x: auto;
    margin: 8px 0;
}

.chat-interface code {
    font-family: var(--code-font, 'Source Code Pro', monospace);
    font-size: 0.9em;
}

.chat-interface p {
    margin: 0 0 10px 0;
}

.chat-interface p:last-child {
    margin-bottom: 0;
}

.chat-interface .error {
    color: var(--error-color, #cb2431);
    font-weight: 500;
}

/* Dark theme variables (can be applied by adding .dark-theme class) */
.dark-theme.chat-interface,
.dark-theme .chat-interface {
    --bg-color: #0d1117;
    --header-bg: #161b22;
    --messages-bg: #0d1117;
    --input-area-bg: #161b22;
    --input-bg: #0d1117;
    --border-color: #30363d;
    --text-color: #c9d1d9;
    --user-msg-bg: #238636;
    --user-header-bg: #238636;
    --user-text-color: #ffffff;
    --user-header-color: #ffffff;
    --assistant-msg-bg: #161b22;
    --assistant-header-bg: #21262d;
    --assistant-text-color: #c9d1d9;
    --assistant-header-color: #c9d1d9;
    --button-bg: #238636;
    --button-hover-bg: #2ea043;
    --button-active-bg: #2a8f45;
    --button-disabled-bg: #22863a80;
    --code-block-bg: rgba(110, 118, 129, 0.1);
    --error-color: #f85149;
}
```

### 2. Telos Chat Interface Implementation

A chat tab was created for the Telos component in Hephaestus:

```html
<!-- /Hephaestus/ui/components/telos/telos-chat-tab.html -->

<div class="telos-chat-tab">
    <div class="chat-container" id="telos-chat-container"></div>
</div>

<script>
    function initTelosChatTab(shadowRoot) {
        const containerId = 'telos-chat-container';
        const container = shadowRoot.getElementById(containerId);
        if (!container) return;
        
        // Get component state
        const componentState = window.getComponentState('telos');
        
        // Create LLM client
        const llmClient = new LLMAdapterClient({
            baseUrl: '/api/rhetor',
            defaultProvider: 'anthropic',
            defaultModel: 'claude-3-sonnet-20240229',
            streamingEnabled: true,
            onError: (error) => {
                console.error('LLM error:', error);
                componentState.set('chat.error', error.message);
            }
        });
        
        // Load saved messages if available
        const savedMessages = componentState.get('chat.messages') || [];
        
        // Create chat interface
        const chatInterface = new ChatInterface({
            containerId: containerId,
            llmClient: llmClient,
            messageStore: savedMessages,
            systemMessage: 'You are an AI assistant specialized in requirements management. Help users create, refine, and analyze requirements for their software projects.',
            showModelSelector: true,
            showSystemMessageEditor: true,
            onSend: (message, messages) => {
                // Save messages to component state
                componentState.set('chat.messages', messages.filter(m => m.role !== 'system'));
                componentState.set('chat.lastUserMessage', message);
            },
            onReceive: (response, messages) => {
                // Save messages to component state
                componentState.set('chat.messages', messages.filter(m => m.role !== 'system'));
                componentState.set('chat.lastAssistantMessage', response);
                
                // Check for requirement-related content and highlight
                identifyRequirements(response);
            }
        });
        
        // Add to component state for access in other tabs
        componentState.set('chat.interface', chatInterface);
        
        // Function to identify potential requirements in responses
        function identifyRequirements(text) {
            // Simple pattern matching for requirements
            const requirementPatterns = [
                /shall/gi,
                /must/gi,
                /should/gi,
                /will/gi,
                /requirement:?\s/gi,
                /REQ-\d+/gi
            ];
            
            let hasRequirements = false;
            for (const pattern of requirementPatterns) {
                if (pattern.test(text)) {
                    hasRequirements = true;
                    break;
                }
            }
            
            if (hasRequirements) {
                // Trigger notification that requirements were found
                const notificationEl = document.createElement('div');
                notificationEl.classList.add('requirement-notification');
                notificationEl.innerHTML = `
                    <p>Potential requirements detected in the response.</p>
                    <button id="create-req-btn">Create Requirements</button>
                `;
                
                container.appendChild(notificationEl);
                
                // Add click handler for the button
                shadowRoot.getElementById('create-req-btn').addEventListener('click', () => {
                    // Create requirements from the response
                    createRequirementsFromText(text);
                    notificationEl.remove();
                });
                
                // Auto-remove after 10 seconds
                setTimeout(() => {
                    if (notificationEl.parentNode) {
                        notificationEl.remove();
                    }
                }, 10000);
            }
        }
        
        // Function to create requirements from text
        function createRequirementsFromText(text) {
            // Switch to the Requirements tab
            const tabNav = shadowRoot.querySelector('.tab-nav');
            if (tabNav) {
                const reqTab = Array.from(tabNav.children).find(tab => 
                    tab.textContent.trim() === 'Requirements');
                if (reqTab) {
                    reqTab.click();
                    
                    // Set the text as analysis input
                    setTimeout(() => {
                        const analysisInput = shadowRoot.querySelector('#requirement-analysis-input');
                        if (analysisInput) {
                            analysisInput.value = text;
                            // Trigger analysis if there's a button for it
                            const analyzeBtn = shadowRoot.querySelector('#analyze-requirements-btn');
                            if (analyzeBtn) {
                                analyzeBtn.click();
                            }
                        }
                    }, 500);
                }
            }
        }
    }
</script>
```

The Telos component was then updated to include the chat tab:

```html
<!-- Modified /Telos/ui/telos-component.html -->

<div class="telos-component">
    <div class="tab-nav">
        <div class="tab active" data-tab="requirements">Requirements</div>
        <div class="tab" data-tab="tracing">Tracing</div>
        <div class="tab" data-tab="validation">Validation</div>
        <div class="tab" data-tab="chat">Chat</div>
    </div>
    
    <div class="tab-content">
        <div class="tab-pane active" id="requirements-tab">
            <!-- Requirements tab content -->
        </div>
        <div class="tab-pane" id="tracing-tab">
            <!-- Tracing tab content -->
        </div>
        <div class="tab-pane" id="validation-tab">
            <!-- Validation tab content -->
        </div>
        <div class="tab-pane" id="chat-tab">
            <!-- Chat tab content - loaded from telos-chat-tab.html -->
        </div>
    </div>
</div>

<script>
    // Load tab contents
    fetch('/components/telos/telos-requirements-tab.html')
        .then(response => response.text())
        .then(html => {
            document.getElementById('requirements-tab').innerHTML = html;
            initRequirementsTab(document);
        });
    
    fetch('/components/telos/telos-tracing-tab.html')
        .then(response => response.text())
        .then(html => {
            document.getElementById('tracing-tab').innerHTML = html;
            initTracingTab(document);
        });
    
    fetch('/components/telos/telos-validation-tab.html')
        .then(response => response.text())
        .then(html => {
            document.getElementById('validation-tab').innerHTML = html;
            initValidationTab(document);
        });
    
    fetch('/components/telos/telos-chat-tab.html')
        .then(response => response.text())
        .then(html => {
            document.getElementById('chat-tab').innerHTML = html;
            initTelosChatTab(document);
        });
    
    // Tab switching logic
    const tabs = document.querySelectorAll('.tab');
    const tabPanes = document.querySelectorAll('.tab-pane');
    
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            // Remove active class from all tabs and panes
            tabs.forEach(t => t.classList.remove('active'));
            tabPanes.forEach(p => p.classList.remove('active'));
            
            // Add active class to clicked tab and corresponding pane
            tab.classList.add('active');
            const tabName = tab.getAttribute('data-tab');
            document.getElementById(`${tabName}-tab`).classList.add('active');
        });
    });
</script>
```

### 3. Component Registry Updates

Finally, the component registry was updated to register the LLM integration capabilities and dependencies for Ergon, Hermes, and Engram components:

```json
// Updated /Hephaestus/ui/server/component_registry.json

{
  "components": [
    {
      "id": "ergon",
      "name": "Ergon",
      "description": "AI agent management and orchestration",
      "icon": "🤖",
      "defaultMode": "html",
      "capabilities": ["agent_management", "llm_orchestration", "workflow_automation", "shadow_dom", "component_isolation", "state_management", "rhetor_llm_integration"],
      "componentPath": "components/ergon/ergon-component.html",
      "scripts": [
        "scripts/shared/llm_adapter_client.js",
        "scripts/shared/chat-interface.js",
        "scripts/ergon-state-manager.js",
        "scripts/component-utils-ergon-state.js",
        "scripts/ergon-service.js",
        "scripts/ergon-state-test-utils.js",
        "scripts/ergon/ergon-component.js"
      ],
      "styles": [
        "styles/ergon/ergon-component.css",
        "styles/shared/chat-interface.css"
      ],
      "usesShadowDom": true,
      "dependencies": ["rhetor"]
    },
    {
      "id": "engram",
      "name": "Engram",
      "description": "Memory and context management",
      "icon": "💾",
      "defaultMode": "html",
      "capabilities": ["memory_management", "context_storage", "shadow_dom", "component_isolation", "rhetor_llm_integration"],
      "componentPath": "components/engram/engram-component.html",
      "scripts": [
        "scripts/shared/llm_adapter_client.js",
        "scripts/shared/chat-interface.js",
        "scripts/engram/engram-service.js",
        "scripts/engram/engram-component.js"
      ],
      "styles": [
        "styles/engram/engram-component.css",
        "styles/shared/chat-interface.css"
      ],
      "usesShadowDom": true,
      "dependencies": ["rhetor"]
    },
    /* ... other components ... */
    {
      "id": "hermes",
      "name": "Hermes",
      "description": "Message bus and service registry visualization",
      "icon": "📨",
      "defaultMode": "html",
      "capabilities": ["message_routing", "service_discovery", "state_management", "shadow_dom", "component_isolation", "rhetor_llm_integration"],
      "componentPath": "components/hermes/hermes-component.html",
      "scripts": [
        "scripts/shared/llm_adapter_client.js",
        "scripts/shared/chat-interface.js",
        "scripts/hermes/hermes-service.js",
        "scripts/hermes/hermes-component.js"
      ],
      "styles": [
        "styles/hermes/hermes-component.css",
        "styles/shared/chat-interface.css"
      ],
      "usesShadowDom": true,
      "dependencies": ["rhetor"]
    },
    /* ... other components ... */
    {
      "id": "telos",
      "name": "Telos",
      "description": "Requirements management, tracing and validation",
      "icon": "🎯",
      "defaultMode": "html",
      "capabilities": ["requirements_management", "requirement_tracing", "requirement_validation", "hierarchical_visualization", "prometheus_integration", "llm_chat", "shadow_dom", "component_isolation", "state_management"],
      "componentPath": "components/telos/telos-component.html",
      "scripts": [
        "scripts/shared/llm_adapter_client.js",
        "scripts/shared/chat-interface.js",
        "scripts/telos/telos-service.js",
        "scripts/telos/telos-component.js",
        "scripts/telos/telos-integration.js"
      ],
      "styles": [
        "styles/telos/telos.css",
        "styles/shared/chat-interface.css"
      ],
      "usesShadowDom": true,
      "dependencies": ["rhetor"]
    }
  ]
}
```

## Challenges and Solutions

### Challenge 1: Ensuring Backward Compatibility

One key challenge was ensuring that existing components continued to function while migrating to the Rhetor LLM adapter. This was particularly important for Ergon, which had its own LLM client implementation.

**Solution:** A fallback mechanism was implemented in the Ergon LLM client, allowing it to use either Rhetor's adapter or fall back to its original implementation if needed. This was achieved through a configuration flag that defaulted to using Rhetor but could be toggled if necessary for backward compatibility.

### Challenge 2: Standardizing Chat Interfaces

Creating a consistent chat interface across all components while maintaining component-specific functionality required careful planning.

**Solution:** A reusable chat interface component was created with customization options for each component. This allowed components to share the same UI pattern while adding specific features (like Telos' requirement detection).

### Challenge 3: WebSocket vs. HTTP Communication

Determining the appropriate communication patterns for different LLM interactions required balancing real-time needs with efficiency.

**Solution:** The LLM adapter client was designed to support both WebSocket streaming for real-time interactions and HTTP requests for simpler operations, with the ability to configure this behavior per request.

## Next Steps

1. Implement more comprehensive testing for the LLM integration
2. Enhance the chat interfaces with additional features like context visualization
3. Add more detailed documentation for component-specific LLM usage patterns
4. Implement advanced rate limiting and error handling
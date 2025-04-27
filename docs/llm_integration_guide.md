# LLM Adapter Integration Guide

**Last Updated:** April 26, 2025

## Overview

This guide provides comprehensive instructions for integrating the Rhetor LLM adapter into Tekton components. The Rhetor LLM adapter provides a standardized interface for interacting with various large language models (LLMs) and manages aspects such as provider selection, token counting, request formatting, and response handling.

## Key Principles

1. **Unified Interface**: All components should interact with LLMs exclusively through the Rhetor adapter
2. **Consistent Patterns**: Follow standard patterns for request formatting and response handling
3. **Resource Efficiency**: Implement appropriate caching and batching strategies
4. **Graceful Degradation**: Handle service unavailability and errors appropriately
5. **Context Management**: Manage context effectively to optimize token usage and response quality

## Backend Integration

### Basic LLM Adapter Client

Here's a template for a basic LLM adapter client that can be used in any Tekton component:

```python
import requests
import json
import logging
from typing import Dict, Any, List, Optional, Generator, Union

class LLMAdapterClient:
    """Client for interacting with the Rhetor LLM adapter."""
    
    def __init__(
        self, 
        base_url: str = "http://localhost:8003", 
        default_model: str = "gpt-4",
        timeout: int = 30
    ):
        """Initialize the LLM adapter client.
        
        Args:
            base_url: Base URL for the Rhetor API
            default_model: Default model to use if not specified
            timeout: Request timeout in seconds
        """
        self.base_url = base_url
        self.default_model = default_model
        self.timeout = timeout
        self.logger = logging.getLogger("llm_adapter_client")
    
    def generate_text(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stop_sequences: Optional[List[str]] = None,
        chat_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """Generate text using the LLM adapter.
        
        Args:
            prompt: The user prompt
            system_prompt: Optional system instructions
            model: Model to use (defaults to self.default_model)
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            stop_sequences: Optional stop sequences
            chat_history: Optional chat history for context
            
        Returns:
            Dict containing the response and metadata
        """
        url = f"{self.base_url}/api/v1/generate"
        
        payload = {
            "model": model or self.default_model,
            "messages": [],
            "temperature": temperature,
        }
        
        # Add system prompt if provided
        if system_prompt:
            payload["messages"].append({"role": "system", "content": system_prompt})
        
        # Add chat history if provided
        if chat_history:
            payload["messages"].extend(chat_history)
        
        # Add user prompt
        payload["messages"].append({"role": "user", "content": prompt})
        
        # Add optional parameters
        if max_tokens:
            payload["max_tokens"] = max_tokens
        
        if stop_sequences:
            payload["stop"] = stop_sequences
            
        try:
            response = requests.post(
                url, 
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error calling LLM adapter: {str(e)}")
            return {
                "error": str(e),
                "success": False,
                "content": "Sorry, I encountered an error while processing your request."
            }
    
    def generate_stream(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stop_sequences: Optional[List[str]] = None,
        chat_history: Optional[List[Dict[str, str]]] = None
    ) -> Generator[Dict[str, Any], None, None]:
        """Generate streaming text using the LLM adapter.
        
        Args:
            prompt: The user prompt
            system_prompt: Optional system instructions
            model: Model to use (defaults to self.default_model)
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            stop_sequences: Optional stop sequences
            chat_history: Optional chat history for context
            
        Returns:
            Generator yielding response chunks
        """
        url = f"{self.base_url}/api/v1/generate_stream"
        
        payload = {
            "model": model or self.default_model,
            "messages": [],
            "temperature": temperature,
        }
        
        # Add system prompt if provided
        if system_prompt:
            payload["messages"].append({"role": "system", "content": system_prompt})
        
        # Add chat history if provided
        if chat_history:
            payload["messages"].extend(chat_history)
        
        # Add user prompt
        payload["messages"].append({"role": "user", "content": prompt})
        
        # Add optional parameters
        if max_tokens:
            payload["max_tokens"] = max_tokens
        
        if stop_sequences:
            payload["stop"] = stop_sequences
            
        try:
            with requests.post(
                url, 
                json=payload,
                timeout=self.timeout,
                stream=True
            ) as response:
                response.raise_for_status()
                for line in response.iter_lines():
                    if line:
                        line_text = line.decode('utf-8')
                        if line_text.startswith('data: '):
                            line_text = line_text[6:]  # Remove 'data: ' prefix
                            if line_text == '[DONE]':
                                break
                            try:
                                chunk = json.loads(line_text)
                                yield chunk
                            except json.JSONDecodeError:
                                self.logger.error(f"Error decoding JSON: {line_text}")
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error streaming from LLM adapter: {str(e)}")
            yield {
                "error": str(e),
                "success": False,
                "content": "Sorry, I encountered an error while processing your request."
            }
```

### WebSocket Integration

For components that require real-time streaming responses, use WebSocket integration:

```python
import websocket
import json
import threading
import uuid
import logging
from typing import Dict, Any, Optional, List, Callable

class LLMWebSocketClient:
    """Client for interacting with the Rhetor LLM adapter via WebSocket."""
    
    def __init__(
        self, 
        ws_url: str = "ws://localhost:8003/ws/generate",
        default_model: str = "gpt-4"
    ):
        """Initialize the LLM WebSocket client.
        
        Args:
            ws_url: WebSocket URL for the Rhetor API
            default_model: Default model to use if not specified
        """
        self.ws_url = ws_url
        self.default_model = default_model
        self.logger = logging.getLogger("llm_websocket_client")
        self.ws = None
        self.callbacks = {}
        self.running = False
        self.ws_thread = None
    
    def connect(self):
        """Connect to the WebSocket server."""
        if self.ws is not None:
            return
            
        self.ws = websocket.WebSocketApp(
            self.ws_url,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close,
            on_open=self._on_open
        )
        
        self.running = True
        self.ws_thread = threading.Thread(target=self.ws.run_forever)
        self.ws_thread.daemon = True
        self.ws_thread.start()
    
    def disconnect(self):
        """Disconnect from the WebSocket server."""
        if self.ws is not None:
            self.running = False
            self.ws.close()
            self.ws = None
            if self.ws_thread is not None:
                self.ws_thread.join(timeout=1)
                self.ws_thread = None
    
    def generate(
        self,
        prompt: str,
        callback: Callable[[Dict[str, Any]], None],
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stop_sequences: Optional[List[str]] = None,
        chat_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """Generate text using the LLM WebSocket.
        
        Args:
            prompt: The user prompt
            callback: Callback function to handle response chunks
            system_prompt: Optional system instructions
            model: Model to use (defaults to self.default_model)
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            stop_sequences: Optional stop sequences
            chat_history: Optional chat history for context
            
        Returns:
            Request ID that can be used to match responses
        """
        if self.ws is None:
            self.connect()
            
        request_id = str(uuid.uuid4())
        self.callbacks[request_id] = callback
        
        payload = {
            "request_id": request_id,
            "model": model or self.default_model,
            "messages": [],
            "temperature": temperature,
        }
        
        # Add system prompt if provided
        if system_prompt:
            payload["messages"].append({"role": "system", "content": system_prompt})
        
        # Add chat history if provided
        if chat_history:
            payload["messages"].extend(chat_history)
        
        # Add user prompt
        payload["messages"].append({"role": "user", "content": prompt})
        
        # Add optional parameters
        if max_tokens:
            payload["max_tokens"] = max_tokens
        
        if stop_sequences:
            payload["stop"] = stop_sequences
            
        try:
            self.ws.send(json.dumps(payload))
            return request_id
        except Exception as e:
            self.logger.error(f"Error sending WebSocket message: {str(e)}")
            if callback:
                callback({
                    "request_id": request_id,
                    "error": str(e),
                    "success": False,
                    "content": "Sorry, I encountered an error while processing your request.",
                    "done": True
                })
            return request_id
    
    def cancel(self, request_id: str):
        """Cancel an ongoing generation request.
        
        Args:
            request_id: The request ID to cancel
        """
        if self.ws is not None:
            try:
                self.ws.send(json.dumps({
                    "request_id": request_id,
                    "action": "cancel"
                }))
            except Exception as e:
                self.logger.error(f"Error canceling request: {str(e)}")
                
        if request_id in self.callbacks:
            del self.callbacks[request_id]
    
    def _on_message(self, ws, message):
        """Handle incoming WebSocket messages."""
        try:
            data = json.loads(message)
            request_id = data.get("request_id")
            
            if request_id and request_id in self.callbacks:
                callback = self.callbacks[request_id]
                callback(data)
                
                if data.get("done", False):
                    del self.callbacks[request_id]
        except json.JSONDecodeError:
            self.logger.error(f"Error decoding WebSocket message: {message}")
        except Exception as e:
            self.logger.error(f"Error handling WebSocket message: {str(e)}")
    
    def _on_error(self, ws, error):
        """Handle WebSocket errors."""
        self.logger.error(f"WebSocket error: {error}")
        
        # Notify all callbacks of the error
        for request_id, callback in list(self.callbacks.items()):
            callback({
                "request_id": request_id,
                "error": str(error),
                "success": False,
                "content": "Sorry, I encountered a WebSocket error.",
                "done": True
            })
            del self.callbacks[request_id]
    
    def _on_close(self, ws, close_status_code, close_msg):
        """Handle WebSocket connection closure."""
        self.logger.info(f"WebSocket closed: {close_status_code} - {close_msg}")
        
        # Notify all callbacks of the closure
        for request_id, callback in list(self.callbacks.items()):
            callback({
                "request_id": request_id,
                "error": "WebSocket connection closed",
                "success": False,
                "content": "Sorry, the WebSocket connection was closed.",
                "done": True
            })
            del self.callbacks[request_id]
            
        # Attempt to reconnect if still running
        if self.running:
            threading.Timer(5.0, self.connect).start()
    
    def _on_open(self, ws):
        """Handle WebSocket connection opening."""
        self.logger.info("WebSocket connection established")
```

### Example Usage in a Component

Here's an example of how to use the LLM adapter client in a component:

```python
from .llm_adapter import LLMAdapterClient

class RequirementAnalyzer:
    def __init__(self):
        self.llm_client = LLMAdapterClient()
        
    def analyze_requirement(self, requirement_text):
        """Analyze a requirement using the LLM adapter."""
        system_prompt = """
        You are a requirements analysis assistant. Analyze the given requirement 
        and provide feedback on its clarity, completeness, and testability.
        Format your response as JSON with the following fields:
        - clarity: A score from 1-10
        - completeness: A score from 1-10
        - testability: A score from 1-10
        - feedback: Specific feedback to improve the requirement
        - suggestions: List of suggested improvements
        """
        
        response = self.llm_client.generate_text(
            prompt=requirement_text,
            system_prompt=system_prompt,
            temperature=0.2,  # Lower temperature for more deterministic outputs
            model="gpt-4"  # Explicitly specify the model
        )
        
        if response.get("error"):
            return {
                "success": False,
                "error": response["error"],
                "message": "Failed to analyze requirement"
            }
            
        return {
            "success": True,
            "analysis": response["content"]
        }
```

## Frontend Integration

### JavaScript Client for LLM Adapter

Here's a template for a JavaScript client that can be used in the frontend:

```javascript
class LLMAdapterClient {
    /**
     * Client for interacting with the Rhetor LLM adapter from the frontend.
     * @param {Object} options Configuration options
     * @param {string} options.baseUrl Base URL for the Rhetor API (default: '/api/llm')
     * @param {string} options.defaultModel Default model to use if not specified (default: 'gpt-4')
     * @param {number} options.timeout Request timeout in seconds (default: 30)
     */
    constructor(options = {}) {
        this.baseUrl = options.baseUrl || '/api/llm';
        this.defaultModel = options.defaultModel || 'gpt-4';
        this.timeout = options.timeout || 30;
        this.pendingRequests = new Map();
    }
    
    /**
     * Generate text using the LLM adapter.
     * @param {Object} params Request parameters
     * @param {string} params.prompt The user prompt
     * @param {string} [params.systemPrompt] Optional system instructions
     * @param {string} [params.model] Model to use (defaults to this.defaultModel)
     * @param {number} [params.temperature=0.7] Sampling temperature (0.0 to 1.0)
     * @param {number} [params.maxTokens] Maximum tokens to generate
     * @param {string[]} [params.stopSequences] Optional stop sequences
     * @param {Array<Object>} [params.chatHistory] Optional chat history for context
     * @returns {Promise<Object>} Promise resolving to the response
     */
    async generateText(params) {
        const { 
            prompt, 
            systemPrompt, 
            model = this.defaultModel, 
            temperature = 0.7,
            maxTokens,
            stopSequences,
            chatHistory = []
        } = params;
        
        const url = `${this.baseUrl}/generate`;
        
        const payload = {
            model,
            messages: [],
            temperature
        };
        
        // Add system prompt if provided
        if (systemPrompt) {
            payload.messages.push({ role: 'system', content: systemPrompt });
        }
        
        // Add chat history
        if (chatHistory && chatHistory.length > 0) {
            payload.messages = payload.messages.concat(chatHistory);
        }
        
        // Add user prompt
        payload.messages.push({ role: 'user', content: prompt });
        
        // Add optional parameters
        if (maxTokens) {
            payload.max_tokens = maxTokens;
        }
        
        if (stopSequences && stopSequences.length > 0) {
            payload.stop = stopSequences;
        }
        
        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), this.timeout * 1000);
            
            const requestId = Math.random().toString(36).substring(2, 15);
            this.pendingRequests.set(requestId, controller);
            
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload),
                signal: controller.signal
            });
            
            clearTimeout(timeoutId);
            this.pendingRequests.delete(requestId);
            
            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`HTTP error ${response.status}: ${errorText}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error calling LLM adapter:', error);
            return {
                error: error.message,
                success: false,
                content: 'Sorry, I encountered an error while processing your request.'
            };
        }
    }
    
    /**
     * Generate streaming text using the LLM adapter.
     * @param {Object} params Request parameters
     * @param {string} params.prompt The user prompt
     * @param {Function} params.onChunk Callback for each chunk received
     * @param {Function} [params.onComplete] Callback when generation is complete
     * @param {Function} [params.onError] Callback for errors
     * @param {string} [params.systemPrompt] Optional system instructions
     * @param {string} [params.model] Model to use (defaults to this.defaultModel)
     * @param {number} [params.temperature=0.7] Sampling temperature (0.0 to 1.0)
     * @param {number} [params.maxTokens] Maximum tokens to generate
     * @param {string[]} [params.stopSequences] Optional stop sequences
     * @param {Array<Object>} [params.chatHistory] Optional chat history for context
     * @returns {string} Request ID that can be used to cancel the request
     */
    generateStream(params) {
        const { 
            prompt,
            onChunk,
            onComplete,
            onError,
            systemPrompt, 
            model = this.defaultModel, 
            temperature = 0.7,
            maxTokens,
            stopSequences,
            chatHistory = []
        } = params;
        
        if (!onChunk) {
            throw new Error('onChunk callback is required for streaming');
        }
        
        const url = `${this.baseUrl}/generate_stream`;
        
        const payload = {
            model,
            messages: [],
            temperature
        };
        
        // Add system prompt if provided
        if (systemPrompt) {
            payload.messages.push({ role: 'system', content: systemPrompt });
        }
        
        // Add chat history
        if (chatHistory && chatHistory.length > 0) {
            payload.messages = payload.messages.concat(chatHistory);
        }
        
        // Add user prompt
        payload.messages.push({ role: 'user', content: prompt });
        
        // Add optional parameters
        if (maxTokens) {
            payload.max_tokens = maxTokens;
        }
        
        if (stopSequences && stopSequences.length > 0) {
            payload.stop = stopSequences;
        }
        
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), this.timeout * 1000);
        
        const requestId = Math.random().toString(36).substring(2, 15);
        this.pendingRequests.set(requestId, controller);
        
        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload),
            signal: controller.signal
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error ${response.status}`);
            }
            
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let buffer = '';
            
            const processChunks = ({done, value}) => {
                if (done) {
                    clearTimeout(timeoutId);
                    this.pendingRequests.delete(requestId);
                    if (onComplete) onComplete();
                    return;
                }
                
                // Decode the chunk and append to buffer
                const chunk = decoder.decode(value, {stream: true});
                buffer += chunk;
                
                // Process any complete lines in the buffer
                const lines = buffer.split('\n');
                buffer = lines.pop() || ''; // Keep the last (potentially incomplete) line in the buffer
                
                for (const line of lines) {
                    if (line.trim() === '') continue;
                    
                    if (line.startsWith('data: ')) {
                        const data = line.substring(6); // Remove 'data: ' prefix
                        
                        if (data === '[DONE]') {
                            clearTimeout(timeoutId);
                            this.pendingRequests.delete(requestId);
                            if (onComplete) onComplete();
                            return;
                        }
                        
                        try {
                            const parsedData = JSON.parse(data);
                            onChunk(parsedData);
                        } catch (error) {
                            console.error('Error parsing SSE data:', error, data);
                        }
                    }
                }
                
                // Continue reading
                return reader.read().then(processChunks);
            };
            
            return reader.read().then(processChunks);
        })
        .catch(error => {
            clearTimeout(timeoutId);
            this.pendingRequests.delete(requestId);
            console.error('Error streaming from LLM adapter:', error);
            if (onError) {
                onError(error);
            }
        });
        
        return requestId;
    }
    
    /**
     * Cancel an ongoing generation request.
     * @param {string} requestId The request ID to cancel
     */
    cancelRequest(requestId) {
        const controller = this.pendingRequests.get(requestId);
        if (controller) {
            controller.abort();
            this.pendingRequests.delete(requestId);
            return true;
        }
        return false;
    }
    
    /**
     * Get available models from the LLM adapter.
     * @returns {Promise<Array<Object>>} Promise resolving to the list of available models
     */
    async getAvailableModels() {
        try {
            const response = await fetch(`${this.baseUrl}/models`);
            if (!response.ok) {
                throw new Error(`HTTP error ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error('Error fetching available models:', error);
            return [];
        }
    }
}
```

### WebSocket Client for Frontend

For real-time streaming in the frontend:

```javascript
class LLMWebSocketClient {
    /**
     * Client for interacting with the Rhetor LLM adapter via WebSocket from the frontend.
     * @param {Object} options Configuration options
     * @param {string} options.wsUrl WebSocket URL for the Rhetor API (default: 'ws://localhost:8003/ws/generate')
     * @param {string} options.defaultModel Default model to use if not specified (default: 'gpt-4')
     * @param {number} options.reconnectInterval Interval in ms to attempt reconnection (default: 5000)
     */
    constructor(options = {}) {
        this.wsUrl = options.wsUrl || 'ws://localhost:8003/ws/generate';
        this.defaultModel = options.defaultModel || 'gpt-4';
        this.reconnectInterval = options.reconnectInterval || 5000;
        this.ws = null;
        this.callbacks = new Map();
        this.isConnected = false;
        this.isConnecting = false;
        this.reconnectTimer = null;
        this.connectionQueue = [];
    }
    
    /**
     * Connect to the WebSocket server.
     * @returns {Promise<void>} Promise that resolves when connection is established
     */
    connect() {
        if (this.isConnected) {
            return Promise.resolve();
        }
        
        if (this.isConnecting) {
            return new Promise((resolve, reject) => {
                this.connectionQueue.push({ resolve, reject });
            });
        }
        
        return new Promise((resolve, reject) => {
            this.isConnecting = true;
            this.connectionQueue.push({ resolve, reject });
            
            try {
                this.ws = new WebSocket(this.wsUrl);
                
                this.ws.onopen = () => {
                    this.isConnected = true;
                    this.isConnecting = false;
                    console.log('WebSocket connection established');
                    
                    // Resolve all queued connection promises
                    while (this.connectionQueue.length > 0) {
                        const { resolve } = this.connectionQueue.shift();
                        resolve();
                    }
                };
                
                this.ws.onmessage = (event) => {
                    try {
                        const data = JSON.parse(event.data);
                        const requestId = data.request_id;
                        
                        if (requestId && this.callbacks.has(requestId)) {
                            const { onChunk, onComplete } = this.callbacks.get(requestId);
                            
                            if (onChunk) {
                                onChunk(data);
                            }
                            
                            if (data.done && onComplete) {
                                onComplete(data);
                                this.callbacks.delete(requestId);
                            }
                        }
                    } catch (error) {
                        console.error('Error handling WebSocket message:', error);
                    }
                };
                
                this.ws.onerror = (error) => {
                    console.error('WebSocket error:', error);
                    
                    // Reject all queued connection promises if still connecting
                    if (this.isConnecting) {
                        this.isConnecting = false;
                        while (this.connectionQueue.length > 0) {
                            const { reject } = this.connectionQueue.shift();
                            reject(error);
                        }
                    }
                    
                    // Notify all callbacks of the error
                    for (const [requestId, { onError }] of this.callbacks.entries()) {
                        if (onError) {
                            onError(error);
                        }
                        this.callbacks.delete(requestId);
                    }
                };
                
                this.ws.onclose = (event) => {
                    console.log(`WebSocket closed: ${event.code} - ${event.reason}`);
                    this.isConnected = false;
                    
                    // Reject all queued connection promises if still connecting
                    if (this.isConnecting) {
                        this.isConnecting = false;
                        while (this.connectionQueue.length > 0) {
                            const { reject } = this.connectionQueue.shift();
                            reject(new Error('WebSocket connection closed'));
                        }
                    }
                    
                    // Notify all callbacks of the closure
                    for (const [requestId, { onError }] of this.callbacks.entries()) {
                        if (onError) {
                            onError(new Error('WebSocket connection closed'));
                        }
                        this.callbacks.delete(requestId);
                    }
                    
                    // Attempt to reconnect
                    this.reconnectTimer = setTimeout(() => {
                        this.connect();
                    }, this.reconnectInterval);
                };
            } catch (error) {
                this.isConnecting = false;
                console.error('Error creating WebSocket:', error);
                
                // Reject all queued connection promises
                while (this.connectionQueue.length > 0) {
                    const { reject } = this.connectionQueue.shift();
                    reject(error);
                }
                
                // Attempt to reconnect
                this.reconnectTimer = setTimeout(() => {
                    this.connect();
                }, this.reconnectInterval);
            }
        });
    }
    
    /**
     * Disconnect from the WebSocket server.
     */
    disconnect() {
        if (this.reconnectTimer) {
            clearTimeout(this.reconnectTimer);
            this.reconnectTimer = null;
        }
        
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
        
        this.isConnected = false;
        this.isConnecting = false;
        this.callbacks.clear();
        this.connectionQueue = [];
    }
    
    /**
     * Generate text using the LLM WebSocket.
     * @param {Object} params Request parameters
     * @param {string} params.prompt The user prompt
     * @param {Function} params.onChunk Callback for each chunk received
     * @param {Function} [params.onComplete] Callback when generation is complete
     * @param {Function} [params.onError] Callback for errors
     * @param {string} [params.systemPrompt] Optional system instructions
     * @param {string} [params.model] Model to use (defaults to this.defaultModel)
     * @param {number} [params.temperature=0.7] Sampling temperature (0.0 to 1.0)
     * @param {number} [params.maxTokens] Maximum tokens to generate
     * @param {string[]} [params.stopSequences] Optional stop sequences
     * @param {Array<Object>} [params.chatHistory] Optional chat history for context
     * @returns {Promise<string>} Promise resolving to the request ID
     */
    async generate(params) {
        const { 
            prompt,
            onChunk,
            onComplete,
            onError,
            systemPrompt, 
            model = this.defaultModel, 
            temperature = 0.7,
            maxTokens,
            stopSequences,
            chatHistory = []
        } = params;
        
        if (!onChunk) {
            throw new Error('onChunk callback is required for WebSocket streaming');
        }
        
        // Ensure we're connected
        await this.connect();
        
        const requestId = Math.random().toString(36).substring(2, 15);
        
        // Store callbacks
        this.callbacks.set(requestId, {
            onChunk,
            onComplete,
            onError
        });
        
        const payload = {
            request_id: requestId,
            model,
            messages: [],
            temperature
        };
        
        // Add system prompt if provided
        if (systemPrompt) {
            payload.messages.push({ role: 'system', content: systemPrompt });
        }
        
        // Add chat history
        if (chatHistory && chatHistory.length > 0) {
            payload.messages = payload.messages.concat(chatHistory);
        }
        
        // Add user prompt
        payload.messages.push({ role: 'user', content: prompt });
        
        // Add optional parameters
        if (maxTokens) {
            payload.max_tokens = maxTokens;
        }
        
        if (stopSequences && stopSequences.length > 0) {
            payload.stop = stopSequences;
        }
        
        try {
            this.ws.send(JSON.stringify(payload));
            return requestId;
        } catch (error) {
            this.callbacks.delete(requestId);
            console.error('Error sending WebSocket message:', error);
            
            if (onError) {
                onError(error);
            }
            
            throw error;
        }
    }
    
    /**
     * Cancel an ongoing generation request.
     * @param {string} requestId The request ID to cancel
     * @returns {boolean} Whether the cancellation was successful
     */
    cancel(requestId) {
        if (!this.isConnected || !this.callbacks.has(requestId)) {
            return false;
        }
        
        try {
            this.ws.send(JSON.stringify({
                request_id: requestId,
                action: 'cancel'
            }));
            
            this.callbacks.delete(requestId);
            return true;
        } catch (error) {
            console.error('Error canceling WebSocket request:', error);
            return false;
        }
    }
}
```

### Chat Interface Component

Here's a template for a reusable chat interface component:

```javascript
/**
 * Creates a chat interface that can be used in any component.
 * @param {HTMLElement} container The container element for the chat interface
 * @param {Object} options Configuration options
 * @returns {Object} Chat interface API
 */
function createChatInterface(container, options = {}) {
    const {
        initialMessages = [],
        theme = 'light',
        placeholder = 'Type a message...',
        showTypingIndicator = true,
        showUserAvatar = true,
        showTimestamps = true,
        wsClient = null,
        httpClient = null,
        defaultModel = 'gpt-4',
        systemPrompt = '',
        onSend = null,
        onMessageReceived = null,
        onError = null
    } = options;
    
    // Create chat elements
    const chatContainer = document.createElement('div');
    chatContainer.className = 'chat-container';
    
    const messagesContainer = document.createElement('div');
    messagesContainer.className = 'messages-container';
    
    const inputContainer = document.createElement('div');
    inputContainer.className = 'input-container';
    
    const textarea = document.createElement('textarea');
    textarea.className = 'chat-input';
    textarea.placeholder = placeholder;
    textarea.rows = 1;
    
    const sendButton = document.createElement('button');
    sendButton.className = 'send-button';
    sendButton.innerHTML = '<svg width="24" height="24" viewBox="0 0 24 24"><path fill="currentColor" d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"></path></svg>';
    
    // Append elements
    inputContainer.appendChild(textarea);
    inputContainer.appendChild(sendButton);
    
    chatContainer.appendChild(messagesContainer);
    chatContainer.appendChild(inputContainer);
    
    container.appendChild(chatContainer);
    
    // Initialize state
    let messages = [...initialMessages];
    let isGenerating = false;
    let currentRequestId = null;
    let fullResponse = '';
    
    // Apply theme
    applyTheme(theme);
    
    // Render initial messages
    renderMessages();
    
    // Setup event listeners
    textarea.addEventListener('keydown', handleKeyDown);
    sendButton.addEventListener('click', handleSend);
    
    // Ensure we have at least one client
    if (!wsClient && !httpClient) {
        console.error('At least one client (wsClient or httpClient) must be provided');
    }
    
    /**
     * Apply theme to the chat interface.
     * @param {string} themeName Theme name ('light' or 'dark')
     */
    function applyTheme(themeName) {
        const isDark = themeName === 'dark';
        
        // Apply theme classes
        chatContainer.className = `chat-container ${isDark ? 'dark' : 'light'}`;
        
        // Additional theme-specific styles can be applied here
    }
    
    /**
     * Render messages in the messages container.
     */
    function renderMessages() {
        // Clear messages container
        messagesContainer.innerHTML = '';
        
        // Add messages
        messages.forEach(message => {
            const messageElement = createMessageElement(message);
            messagesContainer.appendChild(messageElement);
        });
        
        // Scroll to bottom
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
    
    /**
     * Create a message element.
     * @param {Object} message Message object
     * @returns {HTMLElement} Message element
     */
    function createMessageElement(message) {
        const { role, content, timestamp } = message;
        
        const messageElement = document.createElement('div');
        messageElement.className = `message ${role}`;
        
        // Add avatar if enabled
        if (showUserAvatar) {
            const avatarElement = document.createElement('div');
            avatarElement.className = 'avatar';
            
            // Use different avatars for different roles
            let avatarContent = '';
            if (role === 'user') {
                avatarContent = '<svg width="24" height="24" viewBox="0 0 24 24"><path fill="currentColor" d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"></path></svg>';
            } else if (role === 'assistant') {
                avatarContent = '<svg width="24" height="24" viewBox="0 0 24 24"><path fill="currentColor" d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-5.44 3.53c.24-.24.58-.35.92-.35.34 0 .68.11.92.35.24.24.35.58.35.92 0 .34-.11.68-.35.92-.24.24-.58.35-.92.35-.34 0-.68-.11-.92-.35-.24-.24-.35-.58-.35-.92 0-.34.11-.68.35-.92zM7.5 7.5h2v2h-2V7.5zm9 9H7.5v-2h9V16.5z"></path></svg>';
            } else {
                avatarContent = '<svg width="24" height="24" viewBox="0 0 24 24"><path fill="currentColor" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 3c1.66 0 3 1.34 3 3s-1.34 3-3 3-3-1.34-3-3 1.34-3 3-3zm0 14.2c-2.5 0-4.71-1.28-6-3.22.03-1.99 4-3.08 6-3.08 1.99 0 5.97 1.09 6 3.08-1.29 1.94-3.5 3.22-6 3.22z"></path></svg>';
            }
            
            avatarElement.innerHTML = avatarContent;
            messageElement.appendChild(avatarElement);
        }
        
        const contentElement = document.createElement('div');
        contentElement.className = 'content';
        
        // Add markdown rendering if needed
        contentElement.innerHTML = content;
        
        messageElement.appendChild(contentElement);
        
        // Add timestamp if enabled
        if (showTimestamps && timestamp) {
            const timestampElement = document.createElement('div');
            timestampElement.className = 'timestamp';
            timestampElement.textContent = formatTimestamp(timestamp);
            messageElement.appendChild(timestampElement);
        }
        
        return messageElement;
    }
    
    /**
     * Format timestamp for display.
     * @param {number} timestamp Timestamp in milliseconds
     * @returns {string} Formatted timestamp
     */
    function formatTimestamp(timestamp) {
        const date = new Date(timestamp);
        return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }
    
    /**
     * Handle keydown event in the textarea.
     * @param {KeyboardEvent} event Keyboard event
     */
    function handleKeyDown(event) {
        // Submit on Enter (without Shift)
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            handleSend();
        }
        
        // Auto-resize textarea
        setTimeout(() => {
            textarea.style.height = 'auto';
            textarea.style.height = `${Math.min(textarea.scrollHeight, 150)}px`;
        }, 0);
    }
    
    /**
     * Handle send button click.
     */
    function handleSend() {
        const message = textarea.value.trim();
        
        if (!message || isGenerating) {
            return;
        }
        
        // Add user message
        addMessage('user', message);
        
        // Clear textarea
        textarea.value = '';
        textarea.style.height = 'auto';
        
        // Call onSend if provided
        if (onSend) {
            onSend(message);
        }
        
        // Generate response
        generateResponse(message);
    }
    
    /**
     * Add a message to the chat.
     * @param {string} role Message role ('user', 'assistant', or 'system')
     * @param {string} content Message content
     * @param {Object} [options] Additional options
     * @param {boolean} [options.render=true] Whether to render messages after adding
     * @returns {Object} The added message
     */
    function addMessage(role, content, options = {}) {
        const { render = true } = options;
        
        const message = {
            role,
            content,
            timestamp: Date.now()
        };
        
        messages.push(message);
        
        if (render) {
            renderMessages();
        }
        
        return message;
    }
    
    /**
     * Generate a response using the LLM adapter.
     * @param {string} message User message
     */
    function generateResponse(message) {
        isGenerating = true;
        fullResponse = '';
        
        // Show typing indicator
        if (showTypingIndicator) {
            const typingIndicator = document.createElement('div');
            typingIndicator.className = 'message assistant typing';
            typingIndicator.innerHTML = '<div class="avatar"><svg width="24" height="24" viewBox="0 0 24 24"><path fill="currentColor" d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-5.44 3.53c.24-.24.58-.35.92-.35.34 0 .68.11.92.35.24.24.35.58.35.92 0 .34-.11.68-.35.92-.24.24-.58.35-.92.35-.34 0-.68-.11-.92-.35-.24-.24-.35-.58-.35-.92 0-.34.11-.68.35-.92zM7.5 7.5h2v2h-2V7.5zm9 9H7.5v-2h9V16.5z"></path></svg></div><div class="content"><span class="dot"></span><span class="dot"></span><span class="dot"></span></div>';
            messagesContainer.appendChild(typingIndicator);
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }
        
        // Create chat history for context
        const chatHistory = messages
            .filter(msg => msg.role !== 'system')
            .map(msg => ({
                role: msg.role,
                content: msg.content
            }));
            
        // Prefer WebSocket for streaming if available
        if (wsClient) {
            try {
                currentRequestId = wsClient.generate({
                    prompt: message,
                    systemPrompt,
                    model: defaultModel,
                    chatHistory: chatHistory.slice(0, -1), // Exclude the last message (the one we're sending)
                    onChunk: handleResponseChunk,
                    onComplete: handleResponseComplete,
                    onError: handleResponseError
                });
            } catch (error) {
                handleResponseError(error);
            }
        } else if (httpClient) {
            httpClient.generateStream({
                prompt: message,
                systemPrompt,
                model: defaultModel,
                chatHistory: chatHistory.slice(0, -1), // Exclude the last message (the one we're sending)
                onChunk: handleResponseChunk,
                onComplete: handleResponseComplete,
                onError: handleResponseError
            });
        } else {
            handleResponseError(new Error('No client available for generating responses'));
        }
    }
    
    /**
     * Handle a chunk of the response.
     * @param {Object} chunk Response chunk
     */
    function handleResponseChunk(chunk) {
        // Remove typing indicator if present
        const typingIndicator = messagesContainer.querySelector('.message.typing');
        if (typingIndicator) {
            messagesContainer.removeChild(typingIndicator);
        }
        
        // Append to full response
        if (chunk.content) {
            fullResponse += chunk.content;
        }
        
        // Find or create assistant message
        let assistantMessage = messagesContainer.querySelector('.message.assistant:not(.typing)');
        
        if (!assistantMessage) {
            // Create new message if it doesn't exist
            assistantMessage = createMessageElement({
                role: 'assistant',
                content: fullResponse,
                timestamp: Date.now()
            });
            messagesContainer.appendChild(assistantMessage);
        } else {
            // Update existing message
            const contentElement = assistantMessage.querySelector('.content');
            if (contentElement) {
                contentElement.innerHTML = fullResponse;
            }
        }
        
        // Scroll to bottom
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
        
        // Call onMessageReceived if provided
        if (onMessageReceived) {
            onMessageReceived(chunk);
        }
    }
    
    /**
     * Handle response completion.
     * @param {Object} response Complete response
     */
    function handleResponseComplete(response) {
        // Update state
        isGenerating = false;
        currentRequestId = null;
        
        // Add to messages array if not already there
        const lastMessage = messages[messages.length - 1];
        if (lastMessage.role !== 'assistant') {
            addMessage('assistant', fullResponse, { render: false });
        } else {
            // Update the content of the last message
            lastMessage.content = fullResponse;
        }
        
        // Re-render messages (ensures proper formatting)
        renderMessages();
    }
    
    /**
     * Handle response error.
     * @param {Error} error Error object
     */
    function handleResponseError(error) {
        console.error('Error generating response:', error);
        
        // Remove typing indicator if present
        const typingIndicator = messagesContainer.querySelector('.message.typing');
        if (typingIndicator) {
            messagesContainer.removeChild(typingIndicator);
        }
        
        // Add error message
        addMessage('assistant', `Sorry, I encountered an error: ${error.message}`);
        
        // Update state
        isGenerating = false;
        currentRequestId = null;
        
        // Call onError if provided
        if (onError) {
            onError(error);
        }
    }
    
    /**
     * Cancel the current generation if in progress.
     */
    function cancelGeneration() {
        if (!isGenerating || !currentRequestId) {
            return false;
        }
        
        if (wsClient) {
            wsClient.cancel(currentRequestId);
        } else if (httpClient) {
            httpClient.cancelRequest(currentRequestId);
        }
        
        // Remove typing indicator if present
        const typingIndicator = messagesContainer.querySelector('.message.typing');
        if (typingIndicator) {
            messagesContainer.removeChild(typingIndicator);
        }
        
        // Update state
        isGenerating = false;
        currentRequestId = null;
        
        return true;
    }
    
    /**
     * Get all messages.
     * @returns {Array<Object>} All messages
     */
    function getMessages() {
        return [...messages];
    }
    
    /**
     * Clear all messages.
     */
    function clearMessages() {
        // Cancel any ongoing generation
        cancelGeneration();
        
        // Clear messages
        messages = [];
        renderMessages();
    }
    
    /**
     * Set the system prompt.
     * @param {string} prompt System prompt
     */
    function setSystemPrompt(prompt) {
        systemPrompt = prompt;
    }
    
    /**
     * Set the LLM model.
     * @param {string} model Model name
     */
    function setModel(model) {
        defaultModel = model;
    }
    
    // Return public API
    return {
        addMessage,
        getMessages,
        clearMessages,
        cancelGeneration,
        setSystemPrompt,
        setModel,
        isGenerating: () => isGenerating
    };
}
```

## Best Practices

### 1. Error Handling

Always implement proper error handling:

```javascript
try {
    const response = await llmClient.generateText(prompt);
    // Process response
} catch (error) {
    console.error('Error generating text:', error);
    
    // Display user-friendly error message
    displayError('Sorry, I encountered an error while processing your request.');
    
    // Log detailed error information
    logError({
        component: 'MyComponent',
        operation: 'generateText',
        error: error.message,
        stack: error.stack,
        prompt
    });
}
```

### 2. Rate Limiting

Implement rate limiting to prevent abuse:

```javascript
class RateLimiter {
    constructor(maxRequests = 10, interval = 60000) {
        this.maxRequests = maxRequests;
        this.interval = interval;
        this.requests = [];
    }
    
    canMakeRequest() {
        const now = Date.now();
        
        // Remove expired timestamps
        this.requests = this.requests.filter(timestamp => now - timestamp < this.interval);
        
        // Check if we're under the limit
        return this.requests.length < this.maxRequests;
    }
    
    recordRequest() {
        this.requests.push(Date.now());
    }
}

// Usage
const rateLimiter = new RateLimiter(5, 60000); // 5 requests per minute

async function makeLLMRequest(prompt) {
    if (!rateLimiter.canMakeRequest()) {
        throw new Error('Rate limit exceeded. Please try again later.');
    }
    
    rateLimiter.recordRequest();
    return await llmClient.generateText(prompt);
}
```

### 3. Caching

Implement caching for frequent identical requests:

```javascript
class LLMCache {
    constructor(ttl = 3600000) { // 1 hour TTL by default
        this.cache = new Map();
        this.ttl = ttl;
    }
    
    generateCacheKey(params) {
        // Create a deterministic cache key from the request parameters
        return JSON.stringify({
            prompt: params.prompt,
            systemPrompt: params.systemPrompt,
            model: params.model,
            temperature: params.temperature,
            maxTokens: params.maxTokens
        });
    }
    
    get(params) {
        const key = this.generateCacheKey(params);
        const cachedItem = this.cache.get(key);
        
        if (!cachedItem) {
            return null;
        }
        
        const { timestamp, data } = cachedItem;
        
        // Check if the item has expired
        if (Date.now() - timestamp > this.ttl) {
            this.cache.delete(key);
            return null;
        }
        
        return data;
    }
    
    set(params, data) {
        const key = this.generateCacheKey(params);
        this.cache.set(key, {
            timestamp: Date.now(),
            data
        });
    }
    
    clear() {
        this.cache.clear();
    }
}

// Usage
const llmCache = new LLMCache();

async function generateCachedText(params) {
    // Check cache first
    const cachedResult = llmCache.get(params);
    if (cachedResult) {
        console.log('Cache hit!');
        return cachedResult;
    }
    
    // Generate new response
    const response = await llmClient.generateText(params);
    
    // Cache the result
    llmCache.set(params, response);
    
    return response;
}
```

### 4. Context Management

Effectively manage context to optimize token usage:

```javascript
function optimizeContext(messages, maxTokens = 4000) {
    // If we're within the limit, return all messages
    if (estimateTokenCount(messages) <= maxTokens) {
        return messages;
    }
    
    // Always keep the system message if present
    const systemMessages = messages.filter(msg => msg.role === 'system');
    let remainingMessages = messages.filter(msg => msg.role !== 'system');
    
    // Keep the most recent messages up to the token limit
    let optimizedMessages = [...systemMessages];
    let currentTokenCount = estimateTokenCount(optimizedMessages);
    
    // Process messages from newest to oldest
    remainingMessages.reverse();
    
    for (const message of remainingMessages) {
        const messageTokens = estimateTokenCount([message]);
        
        if (currentTokenCount + messageTokens <= maxTokens) {
            optimizedMessages.push(message);
            currentTokenCount += messageTokens;
        } else {
            break;
        }
    }
    
    // Ensure the correct order (oldest to newest)
    return optimizedMessages.sort((a, b) => {
        // System messages should always come first
        if (a.role === 'system') return -1;
        if (b.role === 'system') return 1;
        
        // Then sort by timestamp if available
        if (a.timestamp && b.timestamp) {
            return a.timestamp - b.timestamp;
        }
        
        // Default case
        return 0;
    });
}

// Simple token estimator
function estimateTokenCount(messages) {
    // A very rough approximation: 1 token ≈ 4 characters
    return messages.reduce((count, message) => {
        return count + Math.ceil((message.content || '').length / 4);
    }, 0);
}
```

### 5. Graceful Degradation

Implement graceful degradation when the LLM service is unavailable:

```javascript
async function generateTextWithFallback(prompt, options = {}) {
    try {
        // Try primary model first
        return await llmClient.generateText(prompt, {
            model: 'gpt-4',
            ...options
        });
    } catch (error) {
        console.warn('Primary model unavailable, falling back to alternate model:', error);
        
        try {
            // Fall back to alternate model
            return await llmClient.generateText(prompt, {
                model: 'claude-instant-1.2',
                ...options
            });
        } catch (fallbackError) {
            console.error('All LLM models unavailable:', fallbackError);
            
            // Fall back to static response
            return {
                success: false,
                content: "I'm sorry, but I'm currently unable to process your request. Please try again later."
            };
        }
    }
}
```

## Component-Specific Integration

### 1. Hermes Integration

For Hermes, focus on service discovery and message routing:

```javascript
// LLM-powered service analyzer
class ServiceAnalyzer {
    constructor() {
        this.llmClient = new LLMAdapterClient();
    }
    
    async analyzeService(serviceInfo) {
        const systemPrompt = `
            You are a service analyzer for Tekton. Analyze the provided service information
            and extract key capabilities, dependencies, and potential issues.
            Format your response as JSON with the following fields:
            - capabilities: Array of string capabilities
            - dependencies: Array of services this service depends on
            - issues: Array of potential issues or warnings
            - recommendations: Array of recommendations for improvement
        `;
        
        const response = await this.llmClient.generateText(
            JSON.stringify(serviceInfo, null, 2),
            {
                systemPrompt,
                temperature: 0.2
            }
        );
        
        try {
            return JSON.parse(response.content);
        } catch (error) {
            console.error('Error parsing service analysis:', error);
            return {
                capabilities: [],
                dependencies: [],
                issues: [`Error parsing analysis: ${error.message}`],
                recommendations: []
            };
        }
    }
}
```

### 2. Engram Integration

For Engram, focus on memory augmentation:

```javascript
// Memory-augmented LLM client
class MemoryAugmentedLLM {
    constructor() {
        this.llmClient = new LLMAdapterClient();
        this.engramClient = new EngramClient();
    }
    
    async generateWithMemory(prompt, options = {}) {
        // Retrieve relevant memories
        const memories = await this.engramClient.search(prompt, {
            limit: options.memoryLimit || 5,
            minRelevance: options.minRelevance || 0.7
        });
        
        // Format memories as context
        let memoryContext = '';
        if (memories.length > 0) {
            memoryContext = 'Relevant information from my memory:\n\n' + 
                memories.map(mem => `- ${mem.content} (Relevance: ${mem.relevance.toFixed(2)})`).join('\n');
        }
        
        // Create system prompt with memory context
        const systemPrompt = `
            ${options.systemPrompt || ''}
            
            ${memoryContext}
            
            Based on the above context and your knowledge, respond to the user's query.
        `;
        
        // Generate response with memory-augmented context
        return await this.llmClient.generateText(prompt, {
            ...options,
            systemPrompt
        });
    }
    
    async storeResponseInMemory(prompt, response) {
        // Store the interaction in memory
        await this.engramClient.store({
            type: 'conversation',
            content: `User: ${prompt}\nAssistant: ${response}`,
            metadata: {
                timestamp: Date.now(),
                type: 'llm_interaction'
            }
        });
    }
}
```

### 3. Ergon Integration

For Ergon, focus on agent capabilities:

```javascript
// Agent-based LLM client
class AgentLLM {
    constructor() {
        this.llmClient = new LLMAdapterClient();
    }
    
    async executeAgentAction(agent, action, parameters) {
        // Generate agent instructions
        const systemPrompt = `
            You are ${agent.name}, an AI agent with the following capabilities:
            ${agent.capabilities.join('\n')}
            
            Your current task is to execute the action "${action}" with these parameters:
            ${JSON.stringify(parameters, null, 2)}
            
            Respond with a detailed analysis and result of performing this action.
            If the action requires multiple steps, explain each step clearly.
        `;
        
        // Execute the agent action
        return await this.llmClient.generateText(
            `Execute ${action} with the provided parameters.`,
            {
                systemPrompt,
                model: agent.preferredModel || 'gpt-4',
                temperature: agent.temperature || 0.7
            }
        );
    }
    
    async getAgentThinking(prompt, agent) {
        // Generate agent thinking process
        const systemPrompt = `
            You are ${agent.name}. Show your detailed thinking process as you analyze this request.
            Include multiple perspectives, potential approaches, and your reasoning for each step.
            This is your internal thought process, so be thorough and consider all relevant factors.
            
            Format your thinking in clear steps, and include any uncertainties or assumptions you're making.
        `;
        
        return await this.llmClient.generateText(prompt, {
            systemPrompt,
            model: agent.preferredModel || 'gpt-4',
            temperature: 0.8 // Higher temperature for more creative thinking
        });
    }
}
```

### 4. Telos Integration

For Telos, focus on requirements analysis:

```javascript
// Requirements analysis LLM client
class RequirementsLLM {
    constructor() {
        this.llmClient = new LLMAdapterClient();
    }
    
    async analyzeRequirement(requirement) {
        const systemPrompt = `
            You are a requirements analysis expert. Analyze the provided requirement
            and provide detailed feedback on its quality.
            
            Format your response as JSON with the following fields:
            - clarity: Score from 1-10
            - completeness: Score from 1-10
            - testability: Score from 1-10
            - ambiguities: Array of ambiguous phrases or terms
            - suggestions: Array of improvement suggestions
            - dependencies: Potential dependencies with other requirements
        `;
        
        const response = await this.llmClient.generateText(
            requirement.text,
            {
                systemPrompt,
                temperature: 0.2
            }
        );
        
        try {
            return JSON.parse(response.content);
        } catch (error) {
            console.error('Error parsing requirement analysis:', error);
            return {
                clarity: 5,
                completeness: 5,
                testability: 5,
                ambiguities: [`Error parsing analysis: ${error.message}`],
                suggestions: ['Retry analysis with more specific requirements'],
                dependencies: []
            };
        }
    }
    
    async generateRequirementSuggestions(projectContext, existingRequirements) {
        const systemPrompt = `
            You are a requirements engineering expert. Based on the project context
            and existing requirements, suggest additional requirements that might
            be missing or improvements to existing ones.
            
            Format your response as JSON with the following fields:
            - newRequirements: Array of suggested new requirements
            - improvements: Array of objects with 'id' and 'suggestion' fields for existing requirements
            - potentialRisks: Array of potential risks or issues in the current requirements set
        `;
        
        const prompt = `
            Project Context: ${projectContext}
            
            Existing Requirements:
            ${JSON.stringify(existingRequirements, null, 2)}
            
            What requirements might be missing or need improvement?
        `;
        
        const response = await this.llmClient.generateText(prompt, {
            systemPrompt,
            temperature: 0.4
        });
        
        try {
            return JSON.parse(response.content);
        } catch (error) {
            console.error('Error parsing requirement suggestions:', error);
            return {
                newRequirements: [],
                improvements: [],
                potentialRisks: [`Error parsing suggestions: ${error.message}`]
            };
        }
    }
}
```

## Conclusion

This guide provides a comprehensive approach to integrating the Rhetor LLM adapter into Tekton components. By following these patterns and best practices, components can leverage the power of large language models in a consistent, efficient, and reliable manner.

When implementing the unified LLM adapter integration for Phase 11.5, refer to this guide for standard patterns and examples that can be adapted to each component's specific needs.

## Additional Resources

- [Rhetor API Reference](../api/rhetor_api_reference.md)
- [LLM Model Capabilities Reference](../docs/llm_model_capabilities.md)
- [Chat Interface Design Guide](../docs/chat_interface_design.md)
- [State Management for Chat Applications](../docs/state_management_for_chat.md)
- [WebSocket Best Practices](../docs/websocket_best_practices.md)
/**
 * Configuration for connecting Hephaestus to the LLM Adapter
 * 
 * This file should be referenced in Hephaestus UI scripts to enable
 * communication with the LLM Adapter instead of using the mock responses.
 */

// LLM Adapter connection configuration
const LLM_ADAPTER_CONFIG = {
    // HTTP endpoints - Use environment variable with fallback
    httpUrl: `http://localhost:${window.RHETOR_PORT || 8003}`,
    
    // WebSocket endpoint - Use environment variable with fallback
    wsUrl: `ws://localhost:${window.RHETOR_PORT || 8003}/ws`,
    
    // Whether to use streaming responses (recommended)
    useStreaming: true,
    
    // Context ID mappings
    contextIds: {
        'ergon': 'ergon',
        'awt-team': 'awt-team',
        'agora': 'agora'
    },
    
    // LLM options
    options: {
        temperature: 0.7,
        max_tokens: 4000
    }
};

/**
 * Example usage in Hermes connector:
 * 
 * // Replace the sendLLMMessage method in hermes-connector.js
 * sendLLMMessage(contextId, message, streaming = true, options = {}) {
 *     // Add to UI via existing methods...
 *     
 *     // Connect to the LLM Adapter
 *     if (LLM_ADAPTER_CONFIG) {
 *         console.log(`Sending message to LLM Adapter: ${message}`);
 *         
 *         // Create message for adapter
 *         const llmRequest = {
 *             type: 'LLM_REQUEST',
 *             source: 'UI',
 *             target: 'LLM',
 *             timestamp: new Date().toISOString(),
 *             payload: {
 *                 message: message,
 *                 context: contextId,
 *                 streaming: LLM_ADAPTER_CONFIG.useStreaming && streaming,
 *                 options: {
 *                     ...LLM_ADAPTER_CONFIG.options,
 *                     ...options
 *                 }
 *             }
 *         };
 *         
 *         // Send via WebSocket
 *         if (this.socket && this.socket.readyState === WebSocket.OPEN) {
 *             this.socket.send(JSON.stringify(llmRequest));
 *         } else {
 *             this.connectToLLMAdapter(llmRequest);
 *         }
 *     }
 * }
 * 
 * // Connect to LLM Adapter WebSocket
 * connectToLLMAdapter(initialRequest = null) {
 *     // Close existing connection if any
 *     if (this.socket) {
 *         this.socket.close();
 *     }
 *     
 *     // Create new connection
 *     this.socket = new WebSocket(LLM_ADAPTER_CONFIG.wsUrl);
 *     
 *     // Set up event handlers
 *     this.socket.onopen = () => {
 *         console.log("Connected to LLM Adapter");
 *         
 *         // Send initial request if any
 *         if (initialRequest) {
 *             this.socket.send(JSON.stringify(initialRequest));
 *         }
 *     };
 *     
 *     this.socket.onmessage = (event) => {
 *         // Handle messages from LLM Adapter
 *         const data = JSON.parse(event.data);
 *         
 *         if (data.type === 'UPDATE' && data.payload.chunk) {
 *             // Handle streaming chunk
 *             this.dispatchEvent('streamChunk', {
 *                 contextId: data.payload.context,
 *                 chunk: data.payload.chunk
 *             });
 *         } else if (data.type === 'UPDATE' && data.payload.done) {
 *             // Handle stream completion
 *             this.dispatchEvent('streamComplete', {
 *                 contextId: data.payload.context
 *             });
 *         } else if (data.type === 'RESPONSE' && data.payload.message) {
 *             // Handle complete message
 *             this.dispatchEvent('messageReceived', {
 *                 sender: data.source,
 *                 recipients: [data.target],
 *                 message: {
 *                     text: data.payload.message,
 *                     content: data.payload.message,
 *                     context: data.payload.context
 *                 }
 *             });
 *         }
 *     };
 *     
 *     this.socket.onerror = (error) => {
 *         console.error("LLM Adapter connection error:", error);
 *     };
 *     
 *     this.socket.onclose = () => {
 *         console.log("LLM Adapter connection closed");
 *     };
 * }
 */
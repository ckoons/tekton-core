"""
WebSocket server for the LLM Adapter
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Set, Dict, Any

import websockets
from websockets.server import WebSocketServerProtocol

from .llm_client import LLMClient
from .config import WS_PORT

logger = logging.getLogger(__name__)

class WebSocketServer:
    """WebSocket server for real-time communication with the LLM Adapter"""
    
    def __init__(self, port=WS_PORT):
        """Initialize the WebSocket server"""
        self.port = port
        self.clients: Set[WebSocketServerProtocol] = set()
        self.llm_client = LLMClient()
    
    async def register_client(self, websocket: WebSocketServerProtocol):
        """Register a new client connection"""
        self.clients.add(websocket)
        logger.info(f"Client connected. Total clients: {len(self.clients)}")
        
        try:
            async for message in websocket:
                await self.handle_message(websocket, message)
        except websockets.exceptions.ConnectionClosed:
            logger.info("Client disconnected")
        finally:
            self.clients.remove(websocket)
    
    async def handle_message(self, websocket: WebSocketServerProtocol, message: str):
        """Handle incoming WebSocket messages"""
        try:
            # Parse the message
            data = json.loads(message)
            logger.debug(f"Received message: {data}")
            
            # Handle LLM requests
            if data.get('type') == 'LLM_REQUEST':
                await self.handle_llm_request(websocket, data)
            # Handle registration messages
            elif data.get('type') == 'REGISTER':
                await self.handle_registration(websocket, data)
            # Handle status requests
            elif data.get('type') == 'STATUS':
                await self.handle_status_request(websocket, data)
            # Handle unknown message types
            else:
                logger.warning(f"Unknown message type: {data.get('type')}")
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON message: {message}")
        except Exception as e:
            logger.error(f"Error handling message: {e}", exc_info=True)
    
    async def handle_llm_request(self, websocket: WebSocketServerProtocol, data: Dict[str, Any]):
        """Handle LLM request messages"""
        try:
            # Extract relevant information
            payload = data.get('payload', {})
            context_id = payload.get('context', 'ergon')
            message = payload.get('message', '')
            options = payload.get('options', {})
            
            if not message:
                logger.error("Empty message in LLM request")
                return
            
            # Set up typing indicator response
            typing_response = {
                'type': 'UPDATE',
                'source': 'SYSTEM',
                'target': data.get('source', 'UI'),
                'timestamp': self.get_timestamp(),
                'payload': {
                    'status': 'typing',
                    'isTyping': True,
                    'context': context_id
                }
            }
            await websocket.send(json.dumps(typing_response))
            
            # Check if streaming is requested
            streaming = payload.get('streaming', True)
            
            if streaming:
                # Handle streaming response
                async for chunk in self.llm_client.stream_completion(message, context_id, options):
                    # Check if this is the final chunk
                    if chunk.get('done', False):
                        # Send done message
                        done_response = {
                            'type': 'UPDATE',
                            'source': context_id,
                            'target': data.get('source', 'UI'),
                            'timestamp': self.get_timestamp(),
                            'payload': {
                                'done': True,
                                'context': context_id
                            }
                        }
                        await websocket.send(json.dumps(done_response))
                    elif chunk.get('error'):
                        # Send error message
                        error_response = {
                            'type': 'ERROR',
                            'source': 'SYSTEM',
                            'target': data.get('source', 'UI'),
                            'timestamp': self.get_timestamp(),
                            'payload': {
                                'error': chunk.get('error'),
                                'context': context_id
                            }
                        }
                        await websocket.send(json.dumps(error_response))
                    else:
                        # Send chunk
                        chunk_response = {
                            'type': 'UPDATE',
                            'source': context_id,
                            'target': data.get('source', 'UI'),
                            'timestamp': self.get_timestamp(),
                            'payload': {
                                'chunk': chunk.get('chunk', ''),
                                'context': context_id
                            }
                        }
                        await websocket.send(json.dumps(chunk_response))
            else:
                # Handle non-streaming response
                response = await self.llm_client.complete(message, context_id, False, options)
                
                if response.get('error'):
                    # Send error message
                    error_response = {
                        'type': 'ERROR',
                        'source': 'SYSTEM',
                        'target': data.get('source', 'UI'),
                        'timestamp': self.get_timestamp(),
                        'payload': {
                            'error': response.get('error'),
                            'context': context_id
                        }
                    }
                    await websocket.send(json.dumps(error_response))
                else:
                    # Send response
                    ai_response = {
                        'type': 'RESPONSE',
                        'source': context_id,
                        'target': data.get('source', 'UI'),
                        'timestamp': self.get_timestamp(),
                        'payload': {
                            'message': response.get('message', ''),
                            'context': context_id
                        }
                    }
                    await websocket.send(json.dumps(ai_response))
            
            # Send typing end indicator
            typing_end_response = {
                'type': 'UPDATE',
                'source': 'SYSTEM',
                'target': data.get('source', 'UI'),
                'timestamp': self.get_timestamp(),
                'payload': {
                    'status': 'typing',
                    'isTyping': False,
                    'context': context_id
                }
            }
            await websocket.send(json.dumps(typing_end_response))
                
        except Exception as e:
            logger.error(f"Error handling LLM request: {e}", exc_info=True)
            
            # Send error response
            error_response = {
                'type': 'ERROR',
                'source': 'SYSTEM',
                'target': data.get('source', 'UI'),
                'timestamp': self.get_timestamp(),
                'payload': {
                    'error': f"Error processing request: {str(e)}",
                    'context': context_id if 'context_id' in locals() else 'unknown'
                }
            }
            await websocket.send(json.dumps(error_response))
    
    async def handle_registration(self, websocket: WebSocketServerProtocol, data: Dict[str, Any]):
        """Handle client registration"""
        # Send acknowledgement
        response = {
            'type': 'RESPONSE',
            'source': 'SYSTEM',
            'target': data.get('source', 'UNKNOWN'),
            'timestamp': self.get_timestamp(),
            'payload': {
                'status': 'registered',
                'message': 'Client registered successfully with LLM Adapter'
            }
        }
        await websocket.send(json.dumps(response))
    
    async def handle_status_request(self, websocket: WebSocketServerProtocol, data: Dict[str, Any]):
        """Handle status request"""
        # Send status information
        response = {
            'type': 'RESPONSE',
            'source': 'SYSTEM',
            'target': data.get('source', 'UI'),
            'timestamp': self.get_timestamp(),
            'payload': {
                'status': 'ok',
                'service': 'llm_adapter',
                'version': '0.1.0',
                'claude_available': self.llm_client.has_claude,
                'message': 'LLM Adapter is running'
            }
        }
        await websocket.send(json.dumps(response))
    
    def get_timestamp(self):
        """Get current ISO timestamp"""
        return datetime.now().isoformat()
    
    async def start_server(self):
        """Start the WebSocket server"""
        logger.info(f"Starting WebSocket server on port {self.port}")
        async with websockets.serve(self.register_client, "0.0.0.0", self.port):
            await asyncio.Future()  # Run forever

def start_ws_server():
    """Start the WebSocket server"""
    ws_server = WebSocketServer()
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        loop.run_until_complete(ws_server.start_server())
    except KeyboardInterrupt:
        logger.info("WebSocket server stopped")
    finally:
        loop.close()

if __name__ == "__main__":
    start_ws_server()
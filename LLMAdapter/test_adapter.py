#!/usr/bin/env python3
"""
Test script for the LLM Adapter
"""

import argparse
import asyncio
import json
import logging
import os
import sys
import websockets

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

async def test_websocket(host="localhost", port=8301, message="Hello, how are you?", context_id="ergon"):
    """Test the WebSocket interface"""
    uri = f"ws://{host}:{port}"
    logger.info(f"Connecting to WebSocket at {uri}")
    
    try:
        async with websockets.connect(uri) as websocket:
            logger.info("Connected to WebSocket server")
            
            # Create LLM request
            llm_request = {
                "type": "LLM_REQUEST",
                "source": "TEST",
                "target": "LLM",
                "timestamp": "",
                "payload": {
                    "message": message,
                    "context": context_id,
                    "streaming": True,
                    "options": {
                        "temperature": 0.7
                    }
                }
            }
            
            # Send the request
            logger.info(f"Sending message: {message}")
            await websocket.send(json.dumps(llm_request))
            
            # Receive responses
            response_text = ""
            while True:
                response = await websocket.recv()
                data = json.loads(response)
                
                if data.get("type") == "UPDATE" and data.get("payload", {}).get("chunk"):
                    # Print chunk
                    chunk = data["payload"]["chunk"]
                    print(chunk, end="", flush=True)
                    response_text += chunk
                elif data.get("type") == "UPDATE" and data.get("payload", {}).get("done"):
                    # Stream complete
                    print("\n\n[Stream complete]")
                    break
                elif data.get("type") == "ERROR":
                    # Error response
                    print(f"\n\n[Error: {data.get('payload', {}).get('error')}]")
                    break
                elif data.get("type") == "RESPONSE":
                    # Complete message
                    message = data.get("payload", {}).get("message", "")
                    print(f"\n{message}")
                    response_text = message
                    break
            
            return response_text
    
    except Exception as e:
        logger.error(f"Error testing WebSocket: {e}")
        return None

async def test_http(host="localhost", port=8300, message="Hello, how are you?", context_id="ergon"):
    """Test the HTTP interface"""
    import aiohttp
    
    url = f"http://{host}:{port}/message"
    logger.info(f"Sending HTTP request to {url}")
    
    try:
        async with aiohttp.ClientSession() as session:
            # Create request data
            data = {
                "message": message,
                "context_id": context_id,
                "streaming": False,
                "options": {
                    "temperature": 0.7
                }
            }
            
            # Send the request
            async with session.post(url, json=data) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info("Received response")
                    message = result.get("message", "")
                    print(f"\n{message}")
                    return message
                else:
                    logger.error(f"Error: {response.status}")
                    return None
    
    except Exception as e:
        logger.error(f"Error testing HTTP: {e}")
        return None

async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Test the LLM Adapter')
    parser.add_argument('--host', type=str, default='localhost', help='Host to connect to')
    parser.add_argument('--http-port', type=int, default=8300, help='HTTP port')
    parser.add_argument('--ws-port', type=int, default=8301, help='WebSocket port')
    parser.add_argument('--message', type=str, default='Hello, tell me about the Tekton project', help='Message to send')
    parser.add_argument('--context', type=str, default='ergon', help='Context ID (ergon, awt-team, agora)')
    parser.add_argument('--http', action='store_true', help='Test HTTP interface (default is WebSocket)')
    args = parser.parse_args()
    
    if args.http:
        await test_http(args.host, args.http_port, args.message, args.context)
    else:
        await test_websocket(args.host, args.ws_port, args.message, args.context)

if __name__ == "__main__":
    asyncio.run(main())
#!/usr/bin/env python3
"""
Tekton MCP Proxy

A simple MCP proxy that forwards requests to the Hermes MCP server.
"""

import sys
import json
import requests
from datetime import datetime
import os

# Configuration
HERMES_URL = "http://localhost:8001/api/mcp/v2"
DEBUG_LOG = os.path.expanduser("~/tekton_mcp_proxy.log")

def log(message):
    """Log a message to the debug log file."""
    timestamp = datetime.now().isoformat()
    with open(DEBUG_LOG, "a") as f:
        f.write(f"{timestamp} - {message}\n")

def main():
    """Main entry point for the proxy."""
    log("Tekton MCP Proxy started")
    log(f"Forwarding to Hermes MCP at {HERMES_URL}")
    print(f"Tekton MCP Proxy running on stdio", file=sys.stderr)
    print(f"Forwarding to Hermes MCP at {HERMES_URL}", file=sys.stderr)

    # MCP uses line-delimited JSON for communication
    for line in sys.stdin:
        try:
            # Log the received request
            log(f"Received: {line.strip()}")
            print(f"Received: {line.strip()}", file=sys.stderr)
            
            # Parse the request
            request = json.loads(line)
            
            # Forward the request to Hermes
            response = requests.post(
                HERMES_URL,
                json=request,
                headers={"Content-Type": "application/json"}
            )
            
            # Get the response
            if response.status_code == 200:
                result = response.json()
                log(f"Response: {json.dumps(result)}")
                print(f"Sending response: {json.dumps(result)}", file=sys.stderr)
                
                # Send the response back to Claude
                print(json.dumps(result))
                sys.stdout.flush()
            else:
                log(f"Error: Hermes returned status {response.status_code}")
                print(f"Error: Hermes returned status {response.status_code}", file=sys.stderr)
                
                # Send an error response back to Claude
                error_response = {
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32603,
                        "message": f"Hermes MCP error: {response.status_code}"
                    },
                    "id": request.get("id")
                }
                print(json.dumps(error_response))
                sys.stdout.flush()
                
        except Exception as e:
            log(f"Error: {str(e)}")
            print(f"Error: {str(e)}", file=sys.stderr)
            
            # Send an error response back to Claude
            error_response = {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32603,
                    "message": f"Proxy error: {str(e)}"
                },
                "id": None  # We don't know the ID if parsing failed
            }
            print(json.dumps(error_response))
            sys.stdout.flush()

if __name__ == "__main__":
    main()
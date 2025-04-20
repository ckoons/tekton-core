"""
HTTP server for the LLM Adapter
"""

import logging
from typing import Dict, Any, Optional

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

from .llm_client import LLMClient
from .config import HTTP_PORT

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Tekton LLM Adapter", version="0.1.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development only - restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize LLM client
llm_client = LLMClient()

# Request and response models
class MessageRequest(BaseModel):
    message: str
    context_id: str = "ergon"
    streaming: bool = False
    options: Optional[Dict[str, Any]] = None

class StreamRequest(BaseModel):
    message: str
    context_id: str = "ergon"
    options: Optional[Dict[str, Any]] = None

@app.get("/")
async def root():
    """Root endpoint - provides basic information"""
    return {
        "name": "Tekton LLM Adapter",
        "version": "0.1.0",
        "status": "running",
        "endpoints": ["/message", "/stream"],
        "claude_available": llm_client.has_claude
    }

@app.post("/message")
async def message(request: MessageRequest):
    """Send a message to the LLM and get a response"""
    try:
        response = await llm_client.complete(
            message=request.message,
            context_id=request.context_id,
            streaming=request.streaming,
            options=request.options
        )
        return response
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/stream")
async def stream(request: StreamRequest):
    """Send a message to the LLM and get a streaming response"""
    try:
        # Use server-sent events for streaming
        return EventSourceResponse(
            llm_client.stream_completion(
                message=request.message,
                context_id=request.context_id,
                options=request.options
            ),
            media_type="text/event-stream"
        )
    except Exception as e:
        logger.error(f"Error processing streaming request: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def start_http_server():
    """Start the HTTP server"""
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=HTTP_PORT)

if __name__ == "__main__":
    start_http_server()
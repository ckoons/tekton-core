# Backend Implementation Guide

## Overview

This guide provides detailed instructions for implementing the backend of a Tekton component, including the API server, business logic, CLI, and integrations.

## Project Setup

### 1. Create Directory Structure

```bash
mkdir -p MyComponent/{mycomponent,tests,ui,examples}
cd MyComponent
```

### 2. Create setup.py

```python
from setuptools import setup, find_packages

setup(
    name="mycomponent",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "uvicorn",
        "httpx",
        "pydantic",
        "rich",
        "python-dotenv",
        "aiohttp",
    ],
    entry_points={
        "console_scripts": [
            "mycomponent=mycomponent.cli.main:main",
        ],
    },
)
```

### 3. Create requirements.txt

```text
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
httpx>=0.25.0
pydantic>=2.0.0
pydantic-settings>=2.0.0
rich>=13.0.0
python-dotenv>=1.0.0
aiohttp>=3.9.0
asyncio>=3.4.3
```

## API Implementation

### 1. Create app.py

```python
#!/usr/bin/env python3
"""
MyComponent API Server

This module implements the API server for the MyComponent,
following the Single Port Architecture pattern.
"""

import os
import sys
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Initialize Tekton environment
try:
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "shared", "utils"))
    from tekton_startup import tekton_component_startup
    tekton_component_startup("mycomponent")
except ImportError:
    print("[MYCOMPONENT] Could not load Tekton environment manager")
    print("[MYCOMPONENT] Continuing with system environment variables")

# Import Hermes registration
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "shared", "utils"))
from hermes_registration import HermesRegistration, heartbeat_loop

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("mycomponent.api")

# Create FastAPI application
app = FastAPI(
    title="MyComponent API",
    description="API for MyComponent - [component description]",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Component configuration
COMPONENT_NAME = "mycomponent"
COMPONENT_PORT = int(os.environ.get("MYCOMPONENT_PORT", 8015))

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "MyComponent",
        "version": "0.1.0",
        "status": "running",
        "documentation": f"http://localhost:{COMPONENT_PORT}/docs"
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint following Tekton standards."""
    return {
        "status": "healthy",
        "component": COMPONENT_NAME,
        "version": "0.1.0",
        "timestamp": datetime.utcnow().isoformat(),
        "port": COMPONENT_PORT,
        "uptime": get_uptime() if hasattr(app.state, "start_time") else 0,
        "checks": {
            "api": "healthy",
            "dependencies": check_dependencies()
        }
    }

def get_uptime() -> float:
    """Calculate uptime in seconds."""
    if hasattr(app.state, "start_time"):
        return (datetime.utcnow() - app.state.start_time).total_seconds()
    return 0

def check_dependencies() -> Dict[str, str]:
    """Check status of component dependencies."""
    # Add checks for your specific dependencies
    return {
        "hermes": "healthy" if hasattr(app.state, "hermes_registration") else "not_registered"
    }

@app.on_event("startup")
async def startup_event():
    """Initialize component on startup."""
    try:
        logger.info(f"Starting {COMPONENT_NAME} on port {COMPONENT_PORT}")
        app.state.start_time = datetime.utcnow()
        
        # Register with Hermes
        app.state.hermes_registration = HermesRegistration()
        success = await app.state.hermes_registration.register_component(
            component_name=COMPONENT_NAME,
            port=COMPONENT_PORT,
            version="0.1.0",
            capabilities=["capability1", "capability2"],  # Update with actual capabilities
            metadata={
                "description": "MyComponent description",
                "author": "Tekton Team"
            }
        )
        
        if success:
            # Start heartbeat loop
            import asyncio
            asyncio.create_task(heartbeat_loop(app.state.hermes_registration, COMPONENT_NAME))
            logger.info(f"Successfully registered {COMPONENT_NAME} with Hermes")
        else:
            logger.warning(f"Failed to register {COMPONENT_NAME} with Hermes")
            
        # Initialize your component's core functionality here
        # app.state.my_service = MyService()
        # await app.state.my_service.initialize()
        
        logger.info(f"{COMPONENT_NAME} initialized successfully")
        
    except Exception as e:
        logger.error(f"Error initializing {COMPONENT_NAME}: {e}")
        # Don't re-raise to allow API to start even if initialization partially fails

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    try:
        logger.info(f"Shutting down {COMPONENT_NAME}")
        
        # Deregister from Hermes
        if hasattr(app.state, "hermes_registration") and app.state.hermes_registration:
            await app.state.hermes_registration.deregister(COMPONENT_NAME)
            
        # Cleanup your component's resources here
        # if hasattr(app.state, "my_service"):
        #     await app.state.my_service.cleanup()
        
        logger.info(f"{COMPONENT_NAME} shutdown complete")
        
    except Exception as e:
        logger.error(f"Error shutting down {COMPONENT_NAME}: {e}")

# Import and include routers
from mycomponent.api.endpoints import mcp

app.include_router(mcp.router, prefix="/mcp", tags=["mcp"])

if __name__ == "__main__":
    import argparse
    import uvicorn
    
    parser = argparse.ArgumentParser(description=f"{COMPONENT_NAME} API Server")
    parser.add_argument("--port", type=int, default=COMPONENT_PORT, help="Port to run the server on")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind the server to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload for development")
    args = parser.parse_args()
    
    logger.info(f"Starting {COMPONENT_NAME} server on {args.host}:{args.port}")
    uvicorn.run(
        "mycomponent.api.app:app" if args.reload else app,
        host=args.host,
        port=args.port,
        reload=args.reload
    )
```

### 2. Create MCP Endpoints

```python
# mycomponent/api/endpoints/mcp.py
"""
MCP v2 Endpoints for MyComponent
"""

import logging
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter()

# MCP v2 Models
class Tool(BaseModel):
    """MCP Tool definition"""
    name: str
    description: str
    inputSchema: Dict[str, Any]

class ToolList(BaseModel):
    """Response for tool listing"""
    tools: List[Tool]

class ToolCall(BaseModel):
    """Request to call a tool"""
    name: str
    arguments: Dict[str, Any] = Field(default_factory=dict)

class ToolResponse(BaseModel):
    """Response from tool execution"""
    content: List[Dict[str, Any]]
    isError: bool = False

# Define available tools
AVAILABLE_TOOLS = [
    Tool(
        name="example_tool",
        description="An example tool that demonstrates MCP integration",
        inputSchema={
            "type": "object",
            "properties": {
                "input": {"type": "string", "description": "Input parameter"}
            },
            "required": ["input"]
        }
    )
]

@router.post("/v2/tools/list", response_model=ToolList)
async def list_tools() -> ToolList:
    """List available MCP tools."""
    return ToolList(tools=AVAILABLE_TOOLS)

@router.post("/v2/tools/call", response_model=ToolResponse)
async def call_tool(request: ToolCall) -> ToolResponse:
    """Execute an MCP tool."""
    try:
        if request.name == "example_tool":
            # Implement your tool logic here
            result = f"Processed: {request.arguments.get('input', '')}"
            return ToolResponse(
                content=[{"type": "text", "text": result}]
            )
        else:
            raise HTTPException(status_code=404, detail=f"Tool {request.name} not found")
            
    except Exception as e:
        logger.error(f"Error executing tool {request.name}: {e}")
        return ToolResponse(
            content=[{"type": "text", "text": str(e)}],
            isError=True
        )
```

## CLI Implementation

### 1. Create CLI Main

```python
# mycomponent/cli/main.py
#!/usr/bin/env python3
"""
MyComponent CLI

Command-line interface for interacting with MyComponent.
"""

import asyncio
import logging
from typing import Optional

import click
import httpx
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()
logger = logging.getLogger(__name__)

# Default API URL
DEFAULT_API_URL = f"http://localhost:{os.environ.get('MYCOMPONENT_PORT', 8015)}"

class MyComponentClient:
    """Client for interacting with MyComponent API."""
    
    def __init__(self, base_url: str = DEFAULT_API_URL):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=10.0)
    
    async def get_health(self) -> Dict[str, Any]:
        """Get health status."""
        response = await self.client.get(f"{self.base_url}/health")
        return response.json()
    
    async def close(self):
        """Close the client."""
        await self.client.aclose()

@click.group()
@click.option('--api-url', default=DEFAULT_API_URL, help='MyComponent API URL')
@click.pass_context
def cli(ctx, api_url):
    """MyComponent CLI - Command line interface for MyComponent."""
    ctx.ensure_object(dict)
    ctx.obj['client'] = MyComponentClient(api_url)

@cli.command()
@click.pass_context
async def status(ctx):
    """Check MyComponent status."""
    client = ctx.obj['client']
    try:
        health = await client.get_health()
        
        # Create status table
        table = Table(title="MyComponent Status")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Status", health['status'])
        table.add_row("Version", health['version'])
        table.add_row("Port", str(health['port']))
        table.add_row("Uptime", f"{health.get('uptime', 0):.2f}s")
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
    finally:
        await client.close()

@cli.command()
@click.argument('input_text')
@click.pass_context
async def process(ctx, input_text):
    """Process input through MyComponent."""
    client = ctx.obj['client']
    try:
        # Example command implementation
        console.print(Panel(f"Processing: {input_text}", title="MyComponent"))
        # Add actual processing logic here
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
    finally:
        await client.close()

def main():
    """Main entry point for CLI."""
    cli()

if __name__ == "__main__":
    main()
```

## Core Business Logic

### 1. Create Core Module

```python
# mycomponent/core/my_service.py
"""
Core business logic for MyComponent
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)

class MyService:
    """Main service class for MyComponent functionality."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.initialized = False
        
    async def initialize(self):
        """Initialize the service."""
        logger.info("Initializing MyService")
        # Add initialization logic here
        self.initialized = True
        
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input data."""
        if not self.initialized:
            raise RuntimeError("Service not initialized")
            
        # Implement your core business logic here
        result = {
            "processed_at": datetime.utcnow().isoformat(),
            "input": input_data,
            "output": "Processed successfully"
        }
        
        return result
    
    async def cleanup(self):
        """Cleanup resources."""
        logger.info("Cleaning up MyService")
        # Add cleanup logic here
        self.initialized = False
```

## Launch Scripts

### 1. Create setup.sh

```bash
#!/bin/bash
# Setup script for MyComponent

set -e  # Exit on error

# Ensure the script is run from the MyComponent directory
cd "$(dirname "$0")"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -U pip
pip install -r requirements.txt

# Install package in development mode
echo "Installing MyComponent in development mode..."
pip install -e .

# Make run script executable
chmod +x run_mycomponent.sh

echo "MyComponent setup complete!"
echo "Run './run_mycomponent.sh' to start the MyComponent server."
```

### 2. Create run_mycomponent.sh

```bash
#!/bin/bash
# This script starts the MyComponent server

# Ensure the script is run from the MyComponent directory
cd "$(dirname "$0")"

# Load environment variables if .env file exists
if [ -f .env ]; then
    set -a
    source .env
    set +a
fi

# Set MYCOMPONENT_PORT if not already set
if [ -z "$MYCOMPONENT_PORT" ]; then
    export MYCOMPONENT_PORT=8015
fi

# Start MyComponent API server
python -m mycomponent.api.app "$@"
```

## Common Patterns

### Error Handling

```python
from fastapi import HTTPException
from pydantic import BaseModel

class ErrorResponse(BaseModel):
    error: str
    component: str = "mycomponent"
    timestamp: str
    details: Optional[Dict[str, Any]] = None

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error=str(exc),
            timestamp=datetime.utcnow().isoformat()
        ).dict()
    )
```

### Dependency Injection

```python
# mycomponent/api/dependencies.py
from typing import Optional
from fastapi import Depends, HTTPException

async def get_my_service() -> MyService:
    """Dependency to get MyService instance."""
    if not hasattr(app.state, "my_service"):
        raise HTTPException(status_code=503, detail="Service not initialized")
    return app.state.my_service

# Usage in endpoints
@router.post("/process")
async def process_data(
    data: Dict[str, Any],
    service: MyService = Depends(get_my_service)
):
    result = await service.process(data)
    return result
```

## Best Practices

1. **Always use async/await** for I/O operations
2. **Log appropriately** - INFO for normal operations, ERROR for failures
3. **Handle errors gracefully** - Return proper HTTP status codes
4. **Use dependency injection** - Don't access app.state directly in endpoints
5. **Document everything** - Use docstrings and type hints
6. **Follow naming conventions** - Lowercase with underscores for modules
7. **Keep it simple** - No complex abstractions

---

*Next: [UI Implementation Guide](./UI_Implementation_Guide.md)*
# Shared Patterns Reference

This reference documents common patterns, utilities, and conventions used across all Tekton components. Always use these patterns instead of creating component-specific implementations.

## Environment Configuration

### Three-Tier Environment System

Tekton uses a three-tier environment variable system:

1. **System Environment** - OS-level variables
2. **User Environment** - `~/.env.tekton`
3. **Component Environment** - `ComponentName/.env`

```python
# Standard environment initialization
import sys
import os

# Initialize Tekton environment
try:
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "shared", "utils"))
    from tekton_startup import tekton_component_startup
    tekton_component_startup("mycomponent")
except ImportError:
    print("[MYCOMPONENT] Could not load Tekton environment manager")
    print("[MYCOMPONENT] Continuing with system environment variables")
```

### Standard Environment Variables

```bash
# Global Tekton variables
TEKTON_ROOT=/path/to/Tekton
TEKTON_LOG_LEVEL=INFO

# Component-specific (always uppercase)
MYCOMPONENT_PORT=8015
MYCOMPONENT_LOG_LEVEL=DEBUG
MYCOMPONENT_API_TIMEOUT=30
```

## Port Configuration

### Port Assignment Table

| Component | Port | Purpose |
|-----------|------|---------|
| Engram | 8000 | Memory management |
| Hermes | 8001 | Service registry & messaging |
| Ergon | 8002 | Agent coordination |
| Rhetor | 8003 | LLM management |
| Terma | 8004 | Terminal interface |
| Athena | 8005 | Knowledge graph |
| Prometheus | 8006 | Planning & tracking |
| Harmonia | 8007 | Workflow orchestration |
| Telos | 8008 | Requirements management |
| Synthesis | 8009 | Execution engine |
| Tekton Core | 8010 | Core services |
| Metis | 8011 | Task decomposition |
| Apollo | 8012 | Executive coordinator |
| Budget | 8013 | Token management |
| Sophia | 8014 | Reasoning engine |
| Hephaestus | 8080 | Web UI |

### Port Configuration Pattern

```python
# In your component
COMPONENT_PORT = int(os.environ.get("MYCOMPONENT_PORT", 8015))

# When referencing other components (after Shared_Utilities_Sprint)
from tekton.shared.config import PortConfig

hermes_url = PortConfig.get_component_url("hermes")
```

## Logging Configuration

### Standard Logging Setup

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("mycomponent.module")

# Usage
logger.info("Starting component")
logger.error(f"Error occurred: {e}")
logger.debug("Debug information")
```

### Logging Levels

- **DEBUG** - Detailed diagnostic information
- **INFO** - Normal operational messages
- **WARNING** - Warning messages for recoverable issues
- **ERROR** - Error messages for failures
- **CRITICAL** - Critical failures requiring immediate attention

## Health Check Pattern

### Standard Health Response

```python
from datetime import datetime
from typing import Dict, Any

@app.get("/health")
async def health_check():
    """Health check endpoint following Tekton standards."""
    return {
        "status": "healthy",  # healthy, degraded, unhealthy
        "component": "mycomponent",
        "version": "0.1.0",
        "timestamp": datetime.utcnow().isoformat(),
        "port": COMPONENT_PORT,
        "uptime": get_uptime(),
        "checks": {
            "api": "healthy",
            "database": check_database_health(),
            "dependencies": check_dependencies()
        }
    }
```

### Health Status Values

- **healthy** - All systems operational
- **degraded** - Partial functionality available
- **unhealthy** - Major issues, limited functionality

## Service Registration

### Hermes Registration Pattern

```python
from hermes_registration import HermesRegistration, heartbeat_loop

@app.on_event("startup")
async def startup_event():
    # Register with Hermes
    app.state.hermes_registration = HermesRegistration()
    success = await app.state.hermes_registration.register_component(
        component_name="mycomponent",
        port=COMPONENT_PORT,
        version="0.1.0",
        capabilities=["capability1", "capability2"],
        metadata={
            "description": "Component description",
            "author": "Tekton Team"
        }
    )
    
    if success:
        # Start heartbeat
        asyncio.create_task(heartbeat_loop(app.state.hermes_registration, "mycomponent"))
```

### Heartbeat Pattern

The heartbeat keeps your component registered with Hermes:

```python
async def heartbeat_loop(registration: HermesRegistration, component_name: str):
    """Send periodic heartbeats to Hermes."""
    while True:
        try:
            await asyncio.sleep(30)  # Every 30 seconds
            await registration.heartbeat(component_name)
        except Exception as e:
            logger.error(f"Heartbeat failed: {e}")
```

## MCP v2 Patterns

### Tool Definition

```python
from pydantic import BaseModel, Field
from typing import Dict, List, Any

class Tool(BaseModel):
    """MCP Tool definition"""
    name: str
    description: str
    inputSchema: Dict[str, Any]

# Example tool
Tool(
    name="process_data",
    description="Process input data according to component logic",
    inputSchema={
        "type": "object",
        "properties": {
            "data": {
                "type": "object",
                "description": "Input data to process"
            },
            "options": {
                "type": "object",
                "description": "Processing options",
                "properties": {
                    "mode": {
                        "type": "string",
                        "enum": ["fast", "accurate"],
                        "default": "fast"
                    }
                }
            }
        },
        "required": ["data"]
    }
)
```

### Standard MCP Endpoints

```python
@router.post("/v2/tools/list", response_model=ToolList)
async def list_tools() -> ToolList:
    """List available MCP tools."""
    return ToolList(tools=AVAILABLE_TOOLS)

@router.post("/v2/tools/call", response_model=ToolResponse)
async def call_tool(request: ToolCall) -> ToolResponse:
    """Execute an MCP tool."""
    try:
        # Tool execution logic
        if request.name == "tool_name":
            result = await execute_tool(request.arguments)
            return ToolResponse(
                content=[{"type": "text", "text": str(result)}]
            )
    except Exception as e:
        return ToolResponse(
            content=[{"type": "text", "text": str(e)}],
            isError=True
        )
```

## Error Handling

### Standard Error Response

```python
from pydantic import BaseModel
from datetime import datetime

class ErrorResponse(BaseModel):
    error: str
    component: str
    timestamp: str
    details: Optional[Dict[str, Any]] = None

# Usage in exception handler
@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error=str(exc),
            component="mycomponent",
            timestamp=datetime.utcnow().isoformat()
        ).dict()
    )
```

### HTTP Status Codes

- **200** - Success
- **201** - Created
- **400** - Bad Request (client error)
- **404** - Not Found
- **409** - Conflict
- **500** - Internal Server Error
- **503** - Service Unavailable

## Startup and Shutdown

### Graceful Startup

```python
@app.on_event("startup")
async def startup_event():
    """Initialize component on startup."""
    try:
        logger.info(f"Starting {COMPONENT_NAME}")
        app.state.start_time = datetime.utcnow()
        
        # Initialize services
        app.state.my_service = MyService()
        await app.state.my_service.initialize()
        
        # Register with Hermes
        # ... registration code ...
        
        logger.info(f"{COMPONENT_NAME} initialized successfully")
        
    except Exception as e:
        logger.error(f"Error initializing {COMPONENT_NAME}: {e}")
        # Don't re-raise - allow partial functionality
```

### Graceful Shutdown

```python
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    try:
        logger.info(f"Shutting down {COMPONENT_NAME}")
        
        # Stop background tasks
        for task in asyncio.all_tasks():
            if not task.done():
                task.cancel()
        
        # Deregister from Hermes
        if hasattr(app.state, "hermes_registration"):
            await app.state.hermes_registration.deregister(COMPONENT_NAME)
        
        # Cleanup resources
        if hasattr(app.state, "my_service"):
            await app.state.my_service.cleanup()
        
        logger.info(f"{COMPONENT_NAME} shutdown complete")
        
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")
```

## CLI Patterns

### Standard CLI Structure

```python
import click
from rich.console import Console
from rich.table import Table

console = Console()

@click.group()
@click.option('--api-url', default=DEFAULT_API_URL)
@click.pass_context
def cli(ctx, api_url):
    """Component CLI description."""
    ctx.ensure_object(dict)
    ctx.obj['client'] = ComponentClient(api_url)

@cli.command()
@click.pass_context
def status(ctx):
    """Check component status."""
    # Implementation

@cli.command()
@click.argument('input')
@click.option('--format', type=click.Choice(['json', 'table']), default='table')
@click.pass_context
def process(ctx, input, format):
    """Process input."""
    # Implementation
```

### Rich Output Formatting

```python
# Table output
table = Table(title="Component Status")
table.add_column("Property", style="cyan")
table.add_column("Value", style="green")
table.add_row("Status", "healthy")
console.print(table)

# Progress indicator
with console.status("Processing..."):
    result = await long_running_operation()

# Colored output
console.print("[green]Success![/green]")
console.print("[red]Error occurred[/red]")
```

## Testing Patterns

### Test Structure

```python
import pytest
import asyncio
from httpx import AsyncClient

@pytest.fixture
async def client():
    """Create test client."""
    from mycomponent.api.app import app
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.mark.asyncio
async def test_health_endpoint(client):
    """Test health check endpoint."""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["component"] == "mycomponent"
```

### Test Fixtures

```python
@pytest.fixture
async def mock_service():
    """Mock service for testing."""
    service = MockService()
    await service.initialize()
    yield service
    await service.cleanup()
```

## WebSocket Patterns

### WebSocket Connection

```python
from fastapi import WebSocket, WebSocketDisconnect

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            # Process data
            await websocket.send_json({"type": "response", "data": result})
    except WebSocketDisconnect:
        logger.info("Client disconnected")
```

### WebSocket Message Format

```javascript
// Standard message format
{
    "type": "message_type",  // e.g., "status_update", "command", "response"
    "payload": {
        // Message-specific data
    },
    "timestamp": "2025-01-01T00:00:00Z",
    "component": "mycomponent"
}
```

## UI Patterns

### BEM CSS Naming

```css
/* Block */
.mycomponent { }

/* Element */
.mycomponent__header { }
.mycomponent__content { }

/* Modifier */
.mycomponent__button--primary { }
.mycomponent__status--healthy { }
```

### Component Initialization

```javascript
// Standard component initialization
const MyComponentUI = {
    config: {
        apiUrl: window.MYCOMPONENT_API_URL || 'http://localhost:8015',
        wsUrl: window.MYCOMPONENT_WS_URL || 'ws://localhost:8015/ws'
    },
    
    init() {
        console.log('Initializing MyComponent UI');
        this.connectWebSocket();
        this.loadInitialData();
    }
};

// Initialize when loaded
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('mycomponent-component')) {
        MyComponentUI.init();
    }
});
```

## File Organization

### Python Import Order

```python
#!/usr/bin/env python3
"""Module docstring."""

# Standard library imports
import os
import sys
import asyncio
from datetime import datetime
from typing import Dict, List, Optional

# Third-party imports
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx

# Tekton/shared imports
from tekton_startup import tekton_component_startup
from hermes_registration import HermesRegistration

# Component imports
from mycomponent.core import MyService
from mycomponent.models import MyModel
```

### Module Structure

```
mycomponent/
├── api/          # API layer
├── cli/          # CLI interface
├── core/         # Business logic
├── models/       # Data models
└── utils/        # Component utilities
```

## Common Utilities (After Shared_Utilities_Sprint)

These utilities will be available after the Shared_Utilities_Sprint:

```python
# Port configuration
from tekton.shared.config import PortConfig
hermes_port = PortConfig.get_component_port("hermes")

# Logging setup
from tekton.shared.logging import setup_component_logger
logger = setup_component_logger("mycomponent")

# Health checks
from tekton.shared.health import create_health_response
response = create_health_response("mycomponent", port, "healthy")

# Error handling
from tekton.shared.errors import TektonError, StartupError

# Component startup
from tekton.shared.startup import component_startup
await component_startup("mycomponent", startup_func)
```

## Best Practices Summary

1. **Use Standard Patterns** - Don't reinvent the wheel
2. **Keep It Simple** - No clever abstractions
3. **Error Gracefully** - Always handle errors appropriately
4. **Log Appropriately** - Not too much, not too little
5. **Test Everything** - Write tests for critical paths
6. **Document Clearly** - Code should be self-documenting
7. **Follow Conventions** - Consistency across components

---

*Next: [Testing Guide](./Testing_Guide.md)*
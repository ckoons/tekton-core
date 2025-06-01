# Component Architecture Guide

## Overview

Tekton components follow a unified architecture pattern that ensures consistency, interoperability, and maintainability. This guide explains the architectural principles and patterns that all components must follow.

## Architectural Layers

### 1. API Layer (FastAPI)
- Single port for all services (HTTP, WebSocket, MCP)
- RESTful endpoints for standard operations
- WebSocket support for real-time communication
- MCP v2 endpoints for inter-component communication

### 2. Business Logic Layer
- Core functionality isolated from API concerns
- Domain models separate from API models
- Stateless operations where possible
- Clear separation of concerns

### 3. Integration Layer
- Hermes registration and heartbeat
- Inter-component communication via MCP
- Environment-based configuration
- Health monitoring and diagnostics

### 4. UI Layer
- Hephaestus-integrated components
- Simple visibility and control interface
- LLM chat integration for complex interactions
- Real-time updates via WebSocket

## Component Communication Flow

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Hephaestus    │────▶│   Component     │────▶│     Hermes      │
│      (UI)       │◀────│     (API)       │◀────│   (Registry)    │
└─────────────────┘     └─────────────────┘     └─────────────────┘
         │                       │                         │
         │                       │                         │
         ▼                       ▼                         ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   LLM Client    │     │  Other Tekton   │     │    Component    │
│  (Chat/Tools)   │     │   Components    │     │   Discovery     │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

## Single Port Architecture

Each component operates on a single port that handles:
- HTTP REST API endpoints
- WebSocket connections
- MCP protocol messages
- Health check endpoints

Example port configuration:
```python
# Port assignments (from config/port_assignments.md)
COMPONENT_PORTS = {
    'engram': 8000,
    'hermes': 8001,
    'ergon': 8002,
    'rhetor': 8003,
    # ... etc
}
```

## Service Registration Pattern

Components must register with Hermes on startup:

```python
# Standard registration pattern
async def startup_event():
    # Register with Hermes
    hermes_registration = HermesRegistration()
    await hermes_registration.register_component(
        component_name="mycomponent",
        port=8015,
        version="0.1.0",
        capabilities=["capability1", "capability2"],
        metadata={"description": "My component description"}
    )
    
    # Start heartbeat loop
    asyncio.create_task(heartbeat_loop(hermes_registration, "mycomponent"))
```

## MCP Integration

All components expose capabilities through MCP v2:

```python
# Standard MCP endpoint structure
@router.post("/mcp/v2/tools/list")
async def list_tools() -> MCPToolList:
    """List available MCP tools"""

@router.post("/mcp/v2/tools/call")
async def call_tool(request: MCPToolCall) -> MCPToolResponse:
    """Execute an MCP tool"""
```

## Environment Configuration

Components use Tekton's three-tier environment system:
1. System environment variables
2. User-level `.env.tekton`
3. Component-level `.env`

```python
# Standard environment loading
from tekton_startup import tekton_component_startup
tekton_component_startup("mycomponent")
```

## Health Check Pattern

All components implement standard health endpoints:

```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "component": "mycomponent",
        "version": "0.1.0",
        "uptime": get_uptime(),
        "dependencies": check_dependencies()
    }
```

## UI Integration Pattern

UI components follow these principles:
- Direct HTML injection (no Shadow DOM)
- BEM CSS naming convention
- Self-contained functionality
- LLM chat integration on every panel

```html
<!-- Standard UI structure -->
<div id="mycomponent-component">
    <div class="mycomponent">
        <div class="mycomponent__header">
            <!-- Header content -->
        </div>
        <div class="mycomponent__tabs">
            <!-- Tab navigation -->
        </div>
        <div class="mycomponent__content">
            <!-- Main content panels -->
        </div>
    </div>
</div>
```

## Error Handling

Consistent error handling across all layers:

```python
# Standard error response
class APIError(BaseModel):
    error: str
    component: str
    timestamp: datetime
    details: Optional[Dict[str, Any]] = None
```

## Startup and Shutdown

Components implement graceful startup and shutdown:

```python
@app.on_event("startup")
async def startup_event():
    # Initialize component
    # Register with Hermes
    # Start background tasks

@app.on_event("shutdown")
async def shutdown_event():
    # Stop background tasks
    # Deregister from Hermes
    # Clean up resources
```

## Component Categories

While all components follow the same architecture, they typically fall into these categories:

### Service Components
- Provide specific functionality (e.g., Engram for memory)
- Focus on a single domain
- Expose capabilities via MCP

### Orchestration Components  
- Coordinate other components (e.g., Apollo, Ergon)
- Manage workflows and processes
- Heavy MCP tool usage

### Interface Components
- Primary user interaction (e.g., Rhetor for LLM management)
- Rich UI requirements
- WebSocket for real-time updates

### Utility Components
- Support functionality (e.g., Budget for token management)
- Often called by other components
- Minimal UI requirements

## Best Practices

1. **Keep It Simple** - No clever abstractions that break
2. **Fail Fast** - Clear error messages, quick failure detection
3. **Document Everything** - Code is read more than written
4. **Test First** - Let tests drive the implementation
5. **Use Shared Utilities** - Don't reinvent the wheel
6. **Monitor Health** - Always know component status
7. **Log Appropriately** - Not too much, not too little

## Common Pitfalls to Avoid

1. Creating component-specific utilities instead of using shared ones
2. Complex UI logic instead of leveraging LLM capabilities
3. Tight coupling between components
4. Ignoring the three-tier environment system
5. Custom health check formats
6. Skipping Hermes registration
7. Not implementing proper shutdown handlers

---

*Next: [Backend Implementation Guide](./Backend_Implementation_Guide.md)*
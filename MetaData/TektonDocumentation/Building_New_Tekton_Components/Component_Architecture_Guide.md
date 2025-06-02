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

Components MUST use the lifespan pattern with shared utilities:

```python
# REQUIRED: Use lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup with shared utilities
    async def component_startup():
        # Get configuration - NEVER hardcode ports
        config = get_component_config()
        port = config.mycomponent.port if hasattr(config, 'mycomponent') else int(os.environ.get("MYCOMPONENT_PORT", 8015))
        
        # Register with Hermes
        hermes_registration = HermesRegistration()
        await hermes_registration.register_component(
            component_name="mycomponent",
            port=port,  # From config, never hardcoded
            version="0.1.0",
            capabilities=["capability1", "capability2"],
            metadata={"description": "My component description"}
        )
        
        # Start heartbeat with interval
        asyncio.create_task(heartbeat_loop(hermes_registration, "mycomponent", interval=30))
    
    # Execute startup with metrics
    metrics = await component_startup("mycomponent", component_startup, timeout=30)
    logger.info(f"Started in {metrics.total_time:.2f}s")
    
    yield
    
    # Shutdown with GracefulShutdown
    shutdown = GracefulShutdown("mycomponent")
    await shutdown.shutdown_sequence(timeout=10)
    await asyncio.sleep(0.5)  # CRITICAL: Socket release delay

app = FastAPI(lifespan=lifespan)  # REQUIRED
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

Components use Tekton's three-tier environment system through shared utilities:
1. System environment variables
2. User-level `.env.tekton`
3. Component-level `.env`

```python
# REQUIRED: Use shared utilities for all configuration
from shared.utils.env_config import get_component_config
from shared.utils.logging_setup import setup_component_logging

# Get configuration
config = get_component_config()
logger = setup_component_logging("mycomponent")

# NEVER hardcode values
port = config.mycomponent.port if hasattr(config, 'mycomponent') else int(os.environ.get("MYCOMPONENT_PORT", 8015))
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

**IMPORTANT**: The `@app.on_event` decorators are deprecated. Components MUST use the lifespan pattern with shared utilities:

```python
from shared.utils.startup import component_startup
from shared.utils.shutdown import GracefulShutdown

# See the Service Registration Pattern section above for the complete lifespan implementation
# Key requirements:
# 1. Use asynccontextmanager with lifespan
# 2. Use component_startup for startup metrics
# 3. Use GracefulShutdown for cleanup
# 4. Include socket release delay (0.5s) after shutdown
# 5. Pass lifespan to FastAPI constructor
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
5. **Use Shared Utilities** - MANDATORY, not optional
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
8. Using deprecated @app.on_event decorators
9. Hardcoding port numbers
10. Using logging.getLogger instead of setup_component_logging
11. Forgetting the socket release delay in shutdown
12. Not using the lifespan pattern

---

*Next: [Backend Implementation Guide](./Backend_Implementation_Guide.md)*
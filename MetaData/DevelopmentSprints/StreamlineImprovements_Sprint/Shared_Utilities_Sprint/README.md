# Shared Utilities Sprint

## Overview

This sprint creates a comprehensive shared utilities library to eliminate code duplication across Tekton components. Based on patterns observed during GoodLaunch Sprint, we'll extract common functionality into reusable modules.

## Current State

Significant code duplication across components:
- Logger initialization (14+ identical implementations)
- FastMCP server setup (10+ similar patterns)
- Health check endpoints (inconsistent implementations)
- Error handling (no standard patterns)
- Component registration (repeated boilerplate)

## Goals

1. **Create Shared Library**: Centralized utilities in `tekton-core`
2. **Eliminate Duplication**: 30-40% code reduction
3. **Standardize Patterns**: Consistent usage across components
4. **Improve Reliability**: Battle-tested shared implementations

## Implementation Plan

### Phase 1: Utility Creation (1 session)

Create core utility modules:

```
tekton-core/tekton/shared/
├── __init__.py
├── logging.py      # Standardized logger setup
├── mcp.py          # FastMCP registration helpers
├── health.py       # Health check utilities
├── errors.py       # Common error classes
├── startup.py      # Component startup helpers
└── config.py       # Configuration utilities
```

### Phase 2: Integration (2 sessions)

Update all components to use shared utilities:
- Replace local implementations
- Standardize usage patterns
- Update imports

### Phase 3: Documentation (0.5 sessions)

- Usage examples
- Migration guide
- Best practices

## Key Utilities

### 0. Version Management (Future - for broader release)
```python
# tekton/shared/version.py
# When releasing to broader audience, standardize version tracking
__tekton_version__ = "1.0.0"  # Global Tekton version

def get_component_version(component_name: str) -> str:
    """Get version for a component (for now, all in lockstep)."""
    return __tekton_version__
```

### 1. Logger Setup
```python
# tekton/shared/logging.py
def setup_component_logger(component_name: str, level: str = "INFO") -> logging.Logger:
    """Standard logger setup for all Tekton components."""
    logger = logging.getLogger(f"tekton.{component_name}")
    # Standard configuration
    return logger

# Usage in components
from tekton.shared.logging import setup_component_logger
logger = setup_component_logger("athena")
```

### 2. FastMCP Helpers
```python
# tekton/shared/mcp.py
def create_mcp_server(component_name: str, version: str = "0.1.0") -> FastMCPServer:
    """Create standardized FastMCP server."""
    server = FastMCPServer(
        name=component_name,
        version=version,
        description=f"FastMCP server for {component_name}"
    )
    return server

def register_mcp_tools(server: FastMCPServer, tools: List[Callable]):
    """Bulk register tools with error handling."""
    for tool in tools:
        try:
            server.register_tool(tool)
        except Exception as e:
            logger.error(f"Failed to register {tool.__name__}: {e}")
```

### 3. Health Check
```python
# tekton/shared/health.py
def create_health_endpoint(router: APIRouter, component_name: str):
    """Add standardized health check endpoint."""
    @router.get("/health")
    async def health_check():
        return {
            "status": "healthy",
            "component": component_name,
            "timestamp": datetime.utcnow().isoformat()
        }
```

### 4. Error Classes
```python
# tekton/shared/errors.py
class TektonError(Exception):
    """Base error for all Tekton components."""
    def __init__(self, message: str, component: str, error_code: str = None):
        self.component = component
        self.error_code = error_code
        super().__init__(f"[{component}] {message}")

class StartupError(TektonError):
    """Component startup failure."""
    pass

class RegistrationError(TektonError):
    """Service registration failure."""
    pass
```

### 5. Startup Helpers with Metrics
```python
# tekton/shared/startup.py
import time
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class StartupMetrics:
    """Metrics collected during component startup."""
    import_time: float = 0.0
    init_time: float = 0.0
    connection_time: float = 0.0
    registration_time: float = 0.0
    total_time: float = 0.0
    dependency_status: Dict[str, bool] = None
    resource_usage: Dict[str, Any] = None

async def component_startup(
    component_name: str,
    startup_func: Callable,
    timeout: int = 30,
    collect_metrics: bool = True
) -> StartupMetrics:
    """Standard component startup with timeout, error handling, and metrics."""
    metrics = StartupMetrics()
    start_time = time.time()
    
    try:
        logger.info(f"Starting {component_name}...")
        
        # Track initialization phases
        if collect_metrics:
            metrics.import_time = time.time() - start_time
            
        await asyncio.wait_for(startup_func(), timeout=timeout)
        
        metrics.total_time = time.time() - start_time
        logger.info(f"{component_name} started successfully in {metrics.total_time:.2f}s")
        return metrics
    except asyncio.TimeoutError:
        logger.error(f"{component_name} startup timeout after {timeout}s")
        raise StartupError(f"Startup timeout", component_name)
    except Exception as e:
        logger.error(f"{component_name} startup failed: {e}")
        raise StartupError(str(e), component_name)
```

### 6. Graceful Shutdown
```python
# tekton/shared/shutdown.py
import signal
import asyncio
from typing import List, Callable, Optional

class GracefulShutdown:
    """Coordinated graceful shutdown for Tekton components."""
    
    def __init__(self, component_name: str):
        self.component_name = component_name
        self.shutdown_event = asyncio.Event()
        self.cleanup_tasks: List[Callable] = []
        
        # Register signal handlers
        signal.signal(signal.SIGTERM, self._handle_signal)
        signal.signal(signal.SIGINT, self._handle_signal)
    
    def _handle_signal(self, signum, frame):
        """Handle shutdown signals."""
        logger.info(f"[{self.component_name}] Received signal {signum}, initiating graceful shutdown")
        self.shutdown_event.set()
    
    def register_cleanup(self, cleanup_func: Callable):
        """Register a cleanup function to run during shutdown."""
        self.cleanup_tasks.append(cleanup_func)
    
    async def shutdown_sequence(self, timeout: int = 30):
        """Execute graceful shutdown sequence."""
        logger.info(f"[{self.component_name}] Starting graceful shutdown...")
        
        try:
            # Run all cleanup tasks with timeout
            cleanup_coroutines = [task() for task in self.cleanup_tasks]
            await asyncio.wait_for(
                asyncio.gather(*cleanup_coroutines, return_exceptions=True),
                timeout=timeout
            )
        except asyncio.TimeoutError:
            logger.warning(f"[{self.component_name}] Shutdown timeout after {timeout}s")
        
        logger.info(f"[{self.component_name}] Graceful shutdown complete")

# FastAPI integration helper
from contextlib import asynccontextmanager

@asynccontextmanager
async def component_lifespan(
    component_name: str,
    startup_func: Callable,
    cleanup_funcs: Optional[List[Callable]] = None
):
    """Lifespan context manager for FastAPI apps with graceful shutdown."""
    # Startup
    metrics = await component_startup(component_name, startup_func)
    logger.info(f"Startup metrics: {metrics}")
    
    # Create shutdown handler
    shutdown = GracefulShutdown(component_name)
    if cleanup_funcs:
        for func in cleanup_funcs:
            shutdown.register_cleanup(func)
    
    yield
    
    # Shutdown
    await shutdown.shutdown_sequence()
```

## Benefits

1. **Code Reduction**: 30-40% less duplicated code
2. **Consistency**: Same patterns everywhere
3. **Reliability**: Well-tested shared code
4. **Maintainability**: Fix once, benefit everywhere
5. **Developer Speed**: Faster component creation

## Success Criteria

- [ ] Shared utilities module created and tested
- [ ] All components using shared utilities
- [ ] 30%+ reduction in code duplication
- [ ] Zero regression in functionality
- [ ] Comprehensive documentation

## Migration Strategy

1. Create utilities without breaking existing code
2. Migrate one component as proof of concept
3. Systematically update remaining components
4. Remove deprecated local implementations

## Timeline

Total effort: 3.5 sessions
- Utility Creation: 1 session
- Component Integration: 2 sessions
- Documentation: 0.5 sessions
# Step By Step Tutorial: Building a New Tekton Component

This tutorial walks through creating a new Tekton component from scratch. We'll build a hypothetical "Nexus" component that manages connections between other components.

## ⚠️ IMPORTANT: Updated for Shared Utilities Sprint

This tutorial has been updated to follow the mandatory standards from the Shared Utilities Sprint:
- ✅ Uses the lifespan pattern (no deprecated @app.on_event)
- ✅ Imports all shared utilities (now REQUIRED)
- ✅ Uses setup_component_logging() not logging.getLogger()
- ✅ Never hardcodes ports
- ✅ Includes all required endpoints (/health, /status, /shutdown)
- ✅ Follows standardized launch script patterns

**Start with [Shared_Patterns_Reference.md](./Shared_Patterns_Reference.md) to understand all requirements!**

## Phase 1: Project Setup

### Step 1: Create Directory Structure

```bash
# From Tekton root directory
cd /Users/cskoons/projects/github/Tekton

# Create component directory
mkdir -p Nexus/{nexus,tests,ui,examples}
cd Nexus

# Create Python package structure
mkdir -p nexus/{api,cli,core,models,utils}
mkdir -p nexus/api/endpoints
mkdir -p nexus/cli/commands
mkdir -p ui/{scripts,styles}
mkdir -p tests/{unit,integration}

# Create __init__.py files
touch nexus/__init__.py
touch nexus/{api,cli,core,models,utils}/__init__.py
touch nexus/api/endpoints/__init__.py
touch nexus/cli/commands/__init__.py
touch tests/__init__.py
```

### Step 2: Create Project Files

```bash
# Create setup.py
cat > setup.py << 'EOF'
from setuptools import setup, find_packages

setup(
    name="nexus",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.104.0",
        "uvicorn[standard]>=0.24.0",
        "httpx>=0.25.0",
        "pydantic>=2.0.0",
        "pydantic-settings>=2.0.0",
        "rich>=13.0.0",
        "python-dotenv>=1.0.0",
        "aiohttp>=3.9.0",
        "click>=8.0.0",
    ],
    entry_points={
        "console_scripts": [
            "nexus=nexus.cli.main:main",
        ],
    },
    python_requires=">=3.8",
    author="Tekton Team",
    description="Connection management component for Tekton",
)
EOF

# Create requirements.txt
cat > requirements.txt << 'EOF'
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
httpx>=0.25.0
pydantic>=2.0.0
pydantic-settings>=2.0.0
rich>=13.0.0
python-dotenv>=1.0.0
aiohttp>=3.9.0
click>=8.0.0
pytest>=7.0.0
pytest-asyncio>=0.21.0
EOF

# Create README.md
cat > README.md << 'EOF'
# Nexus

Connection management component for the Tekton ecosystem.

## Overview

Nexus manages and monitors connections between Tekton components, providing:
- Connection health monitoring
- Dependency tracking
- Communication routing
- Performance metrics

## Installation

```bash
./setup.sh
```

## Usage

### Starting the Server

```bash
./run_nexus.sh
```

### CLI Usage

```bash
nexus status
nexus list-connections
nexus test-connection <component>
```

## API Documentation

Once running, visit http://localhost:8016/docs for interactive API documentation.

## MCP Tools

Nexus provides the following MCP tools:
- `list_connections` - List all active connections
- `test_connection` - Test connectivity to a component
- `get_connection_metrics` - Get performance metrics

## Configuration

Configure Nexus through environment variables:
- `NEXUS_PORT` - API server port (default: 8016)
- `NEXUS_LOG_LEVEL` - Logging level (default: INFO)
EOF
```

### Step 3: Create Setup Scripts

```bash
# Create setup.sh
cat > setup.sh << 'EOF'
#!/bin/bash
# Setup script for Nexus

set -e  # Exit on error

# Ensure the script is run from the Nexus directory
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
echo "Installing Nexus in development mode..."
pip install -e .

# Make run script executable
chmod +x run_nexus.sh

echo "Nexus setup complete!"
echo "Run './run_nexus.sh' to start the Nexus server."
EOF

chmod +x setup.sh

# Create run_nexus.sh
cat > run_nexus.sh << 'EOF'
#!/bin/bash
# This script starts the Nexus server

# Ensure the script is run from the Nexus directory
cd "$(dirname "$0")"

# Load environment variables if .env file exists
if [ -f .env ]; then
    set -a
    source .env
    set +a
fi

# Set NEXUS_PORT if not already set
if [ -z "$NEXUS_PORT" ]; then
    export NEXUS_PORT=8016
fi

# Start Nexus API server
python -m nexus.api.app "$@"
EOF

chmod +x run_nexus.sh
```

## Phase 2: Backend Implementation

### Step 4: Create Core Models

```python
# nexus/models/connection.py
from datetime import datetime
from typing import Optional, List, Dict, Any
from tekton.models.base import TektonBaseModel
from pydantic import Field
from enum import Enum

class ConnectionStatus(str, Enum):
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    DEGRADED = "degraded"
    UNKNOWN = "unknown"

class ConnectionInfo(TektonBaseModel):
    """Information about a component connection"""
    component_id: str
    component_name: str
    endpoint: str
    port: int
    status: ConnectionStatus
    last_seen: datetime
    latency_ms: Optional[float] = None
    error_count: int = 0
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ConnectionMetrics(TektonBaseModel):
    """Performance metrics for a connection"""
    component_id: str
    avg_latency_ms: float
    min_latency_ms: float
    max_latency_ms: float
    success_rate: float
    total_requests: int
    failed_requests: int
    last_updated: datetime
```

### Step 5: Create Core Service

```python
# nexus/core/connection_manager.py
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import aiohttp

from nexus.models.connection import ConnectionInfo, ConnectionStatus, ConnectionMetrics

logger = logging.getLogger(__name__)

class ConnectionManager:
    """Manages connections to other Tekton components"""
    
    def __init__(self, check_interval: int = 30):
        self.connections: Dict[str, ConnectionInfo] = {}
        self.metrics: Dict[str, ConnectionMetrics] = {}
        self.check_interval = check_interval
        self._monitoring_task: Optional[asyncio.Task] = None
        self._session: Optional[aiohttp.ClientSession] = None
        
    async def initialize(self):
        """Initialize the connection manager"""
        logger.info("Initializing ConnectionManager")
        self._session = aiohttp.ClientSession()
        self._monitoring_task = asyncio.create_task(self._monitor_connections())
        
    async def cleanup(self):
        """Cleanup resources"""
        logger.info("Cleaning up ConnectionManager")
        if self._monitoring_task:
            self._monitoring_task.cancel()
        if self._session:
            await self._session.close()
            
    async def register_connection(self, component_id: str, name: str, 
                                endpoint: str, port: int) -> ConnectionInfo:
        """Register a new component connection"""
        connection = ConnectionInfo(
            component_id=component_id,
            component_name=name,
            endpoint=endpoint,
            port=port,
            status=ConnectionStatus.UNKNOWN,
            last_seen=datetime.utcnow()
        )
        
        self.connections[component_id] = connection
        logger.info(f"Registered connection to {name} ({component_id})")
        
        # Test the connection immediately
        await self._check_connection(component_id)
        
        return connection
        
    async def test_connection(self, component_id: str) -> ConnectionInfo:
        """Test a specific connection"""
        if component_id not in self.connections:
            raise ValueError(f"Unknown component: {component_id}")
            
        await self._check_connection(component_id)
        return self.connections[component_id]
        
    async def get_all_connections(self) -> List[ConnectionInfo]:
        """Get all registered connections"""
        return list(self.connections.values())
        
    async def get_connection_metrics(self, component_id: str) -> Optional[ConnectionMetrics]:
        """Get metrics for a specific connection"""
        return self.metrics.get(component_id)
        
    async def _monitor_connections(self):
        """Background task to monitor all connections"""
        while True:
            try:
                await asyncio.sleep(self.check_interval)
                
                # Check all connections
                tasks = [self._check_connection(cid) for cid in self.connections]
                await asyncio.gather(*tasks, return_exceptions=True)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in connection monitoring: {e}")
                
    async def _check_connection(self, component_id: str):
        """Check the health of a specific connection"""
        connection = self.connections.get(component_id)
        if not connection:
            return
            
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Try to reach the health endpoint
            url = f"http://{connection.endpoint}:{connection.port}/health"
            async with self._session.get(url, timeout=5) as response:
                latency_ms = (asyncio.get_event_loop().time() - start_time) * 1000
                
                if response.status == 200:
                    connection.status = ConnectionStatus.CONNECTED
                    connection.latency_ms = latency_ms
                    connection.last_seen = datetime.utcnow()
                else:
                    connection.status = ConnectionStatus.DEGRADED
                    connection.error_count += 1
                    
        except asyncio.TimeoutError:
            connection.status = ConnectionStatus.DISCONNECTED
            connection.error_count += 1
            logger.warning(f"Connection to {connection.component_name} timed out")
        except Exception as e:
            connection.status = ConnectionStatus.DISCONNECTED
            connection.error_count += 1
            logger.error(f"Error checking {connection.component_name}: {e}")
            
        # Update metrics
        self._update_metrics(component_id, connection)
        
    def _update_metrics(self, component_id: str, connection: ConnectionInfo):
        """Update connection metrics"""
        # Simple metrics tracking - in production, use a proper metrics system
        if component_id not in self.metrics:
            self.metrics[component_id] = ConnectionMetrics(
                component_id=component_id,
                avg_latency_ms=0,
                min_latency_ms=float('inf'),
                max_latency_ms=0,
                success_rate=0,
                total_requests=0,
                failed_requests=0,
                last_updated=datetime.utcnow()
            )
            
        metrics = self.metrics[component_id]
        metrics.total_requests += 1
        
        if connection.status == ConnectionStatus.CONNECTED:
            if connection.latency_ms:
                # Update latency metrics (simplified)
                metrics.min_latency_ms = min(metrics.min_latency_ms, connection.latency_ms)
                metrics.max_latency_ms = max(metrics.max_latency_ms, connection.latency_ms)
                metrics.avg_latency_ms = connection.latency_ms  # Simplified
        else:
            metrics.failed_requests += 1
            
        metrics.success_rate = (metrics.total_requests - metrics.failed_requests) / metrics.total_requests
        metrics.last_updated = datetime.utcnow()
```

### Step 6: Create API Application

```python
# nexus/__main__.py
"""Entry point for python -m nexus"""
import os
import sys

# Add Tekton root to path if not already present
tekton_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if tekton_root not in sys.path:
    sys.path.insert(0, tekton_root)

from shared.utils.socket_server import run_component_server

if __name__ == "__main__":
    # Get port from environment variable - NO HARDCODED DEFAULTS!
    default_port = int(os.environ.get("NEXUS_PORT"))
    
    run_component_server(
        component_name="nexus",
        app_module="nexus.api.app",
        default_port=default_port,
        reload=True
    )
```

Create the main API application:

```python
# nexus/api/app.py
#!/usr/bin/env python3
"""
Nexus API Server

Connection management component for Tekton
"""

import os
import sys
import asyncio
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Dict, Any, List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# REQUIRED: Add Tekton root to path
tekton_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
if tekton_root not in sys.path:
    sys.path.insert(0, tekton_root)

# Import shared utilities (NO LONGER OPTIONAL)
from shared.utils.hermes_registration import HermesRegistration, heartbeat_loop
from shared.utils.logging_setup import setup_component_logging
from shared.utils.env_config import get_component_config
from shared.utils.errors import StartupError
from shared.utils.startup import component_startup, StartupMetrics
from shared.utils.shutdown import GracefulShutdown
from shared.utils.health_check import create_health_response
from shared.utils.shutdown_endpoint import add_shutdown_endpoint_to_app

# Import shared API utilities (REQUIRED as of API Consistency Sprint)
from shared.api import (
    create_standard_routers,
    mount_standard_routers,
    create_ready_endpoint,
    create_discovery_endpoint,
    get_openapi_configuration,
    EndpointInfo
)

# Import core modules
from nexus.core.connection_manager import ConnectionManager
from nexus.models.connection import ConnectionInfo, ConnectionMetrics

# Component configuration (REQUIRED - API Consistency Standards)
COMPONENT_NAME = "Nexus"  # Use PascalCase for display
COMPONENT_VERSION = "0.1.0"  # All components must use 0.1.0
COMPONENT_DESCRIPTION = "Connection management component for Tekton"

# Use shared logger setup - DO NOT use logging.getLogger()
logger = setup_component_logging(COMPONENT_NAME.lower())

# Global state for registration and timing
hermes_registration = None
heartbeat_task = None
start_time = None  # Track startup time for ready endpoint
is_registered_with_hermes = False  # Track registration status

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for Nexus"""
    global hermes_registration, heartbeat_task, start_time, is_registered_with_hermes
    
    # Track startup time for ready endpoint
    import time
    start_time = time.time()
    
    # Startup
    logger.info("Starting Nexus API")
    
    async def nexus_startup():
        """Component-specific startup logic"""
        try:
            # Get configuration - NEVER hardcode ports
            config = get_component_config()
            port = config.nexus.port if hasattr(config, 'nexus') else int(os.environ.get("NEXUS_PORT", 8016))
            
            # Store in app state for access in endpoints
            app.state.port = port
            app.state.start_time = datetime.utcnow()
            
            # Register with Hermes
            global hermes_registration, heartbeat_task
            hermes_registration = HermesRegistration()
            
            logger.info(f"Attempting to register Nexus with Hermes on port {port}")
            is_registered_with_hermes = await hermes_registration.register_component(
                component_name=COMPONENT_NAME.lower(),
                port=port,  # NEVER hardcode this value
                version=COMPONENT_VERSION,  # Use the constant
                capabilities=["connection_monitoring", "dependency_tracking", "performance_metrics"],
                metadata={
                    "description": "Connection management for Tekton components",
                    "author": "Tekton Team"
                }
            )
            
            if is_registered_with_hermes:
                logger.info("Successfully registered with Hermes")
                heartbeat_task = asyncio.create_task(
                    heartbeat_loop(hermes_registration, COMPONENT_NAME, interval=30)
                )
            else:
                logger.warning("Failed to register with Hermes - continuing without registration")
                
            # Initialize connection manager
            app.state.connection_manager = ConnectionManager()
            await app.state.connection_manager.initialize()
            
        except Exception as e:
            logger.error(f"Error during Nexus startup: {e}", exc_info=True)
            raise StartupError(str(e), COMPONENT_NAME, "STARTUP_FAILED")
    
    # Execute startup with metrics
    try:
        metrics = await component_startup(COMPONENT_NAME, nexus_startup, timeout=30)
        logger.info(f"Nexus started successfully in {metrics.total_time:.2f}s")
    except Exception as e:
        logger.error(f"Failed to start Nexus: {e}")
        raise
    
    # Create shutdown handler
    shutdown = GracefulShutdown(COMPONENT_NAME)
    
    # Register cleanup tasks
    async def cleanup_hermes():
        """Cleanup Hermes registration"""
        if heartbeat_task:
            heartbeat_task.cancel()
            try:
                await heartbeat_task
            except asyncio.CancelledError:
                pass
        
        if hermes_registration and hermes_registration.is_registered:
            await hermes_registration.deregister(COMPONENT_NAME)
            logger.info("Deregistered from Hermes")
    
    shutdown.register_cleanup(cleanup_hermes)
    
    # Add connection manager cleanup
    async def cleanup_connection_manager():
        if hasattr(app.state, "connection_manager"):
            await app.state.connection_manager.cleanup()
    
    shutdown.register_cleanup(cleanup_connection_manager)
    
    yield
    
    # Shutdown
    logger.info("Shutting down Nexus API")
    await shutdown.shutdown_sequence(timeout=10)
    
    # CRITICAL: Socket release delay for macOS
    await asyncio.sleep(0.5)

# Create app with standard configuration (API Consistency Standards)
app = FastAPI(
    **get_openapi_configuration(
        component_name=COMPONENT_NAME,
        component_version=COMPONENT_VERSION,
        component_description=COMPONENT_DESCRIPTION
    ),
    lifespan=lifespan  # REQUIRED
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create standard routers (API Consistency Standards)
routers = create_standard_routers(COMPONENT_NAME)

# Root endpoint - use standard router
@routers.root.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": COMPONENT_NAME,
        "version": COMPONENT_VERSION,
        "description": COMPONENT_DESCRIPTION,
        "status": "running",
        "docs": "/api/v1/docs"  # Updated docs URL
    }

# Health check endpoint - use standard router
@routers.root.get("/health")
async def health_check():
    """Health check endpoint using shared utility."""
    port = getattr(app.state, 'port', int(os.environ.get("NEXUS_PORT")))
    uptime = None
    if hasattr(app.state, "start_time"):
        uptime = (datetime.utcnow() - app.state.start_time).total_seconds()
    
    return create_health_response(
        component_name=COMPONENT_NAME.lower(),
        port=port,
        version=COMPONENT_VERSION,
        status="healthy",
        registered=is_registered_with_hermes,
        details={
            "uptime": uptime,
            "connection_manager": "healthy" if hasattr(app.state, "connection_manager") else "not_initialized",
            "dependencies": {
                "hermes": "healthy" if is_registered_with_hermes else "not_registered"
            }
        }
    )

# Status endpoint for tekton-status
@app.get("/status")
async def get_status():
    """Status endpoint for tekton-status integration."""
    port = getattr(app.state, 'port', int(os.environ.get("NEXUS_PORT")))
    return {
        "component": COMPONENT_NAME,
        "status": "running",
        "version": "0.1.0",
        "port": port,
        "registered": hermes_registration.is_registered if hermes_registration else False,
        "uptime": (datetime.utcnow() - app.state.start_time).total_seconds() if hasattr(app.state, "start_time") else 0,
        "capabilities": ["connection_monitoring", "dependency_tracking", "performance_metrics"],
        "health": {
            "api": "healthy",
            "dependencies": {
                "hermes": "healthy" if hermes_registration and hermes_registration.is_registered else "disconnected"
            }
        }
    }

# Add ready endpoint (API Consistency Standards)
routers.root.add_api_route(
    "/ready",
    create_ready_endpoint(
        component_name=COMPONENT_NAME,
        component_version=COMPONENT_VERSION,
        start_time=start_time or 0,
        readiness_check=lambda: hasattr(app.state, "connection_manager")
    ),
    methods=["GET"]
)

# Add discovery endpoint (API Consistency Standards)
routers.v1.add_api_route(
    "/discovery",
    create_discovery_endpoint(
        component_name=COMPONENT_NAME,
        component_version=COMPONENT_VERSION,
        component_description=COMPONENT_DESCRIPTION,
        endpoints=[
            EndpointInfo(
                path="/api/v1/connections",
                method="GET",
                description="List all registered connections"
            ),
            EndpointInfo(
                path="/api/v1/connections/{component_id}/test",
                method="POST",
                description="Test a specific connection"
            ),
            EndpointInfo(
                path="/api/v1/connections/{component_id}/metrics",
                method="GET",
                description="Get metrics for a specific connection"
            )
        ],
        capabilities=["connection_monitoring", "dependency_tracking", "performance_metrics"],
        dependencies={
            "hermes": "http://localhost:8001"
        },
        metadata={
            "documentation": "/api/v1/docs"
        }
    ),
    methods=["GET"]
)

# Connection management endpoints - use v1 router
@routers.v1.get("/connections", response_model=List[ConnectionInfo])
async def list_connections():
    """List all registered connections."""
    if not hasattr(app.state, "connection_manager"):
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    return await app.state.connection_manager.get_all_connections()

@routers.v1.post("/connections/{component_id}/test", response_model=ConnectionInfo)
async def test_connection(component_id: str):
    """Test a specific connection."""
    if not hasattr(app.state, "connection_manager"):
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        return await app.state.connection_manager.test_connection(component_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@routers.v1.get("/connections/{component_id}/metrics", response_model=ConnectionMetrics)
async def get_connection_metrics(component_id: str):
    """Get metrics for a specific connection."""
    if not hasattr(app.state, "connection_manager"):
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    metrics = await app.state.connection_manager.get_connection_metrics(component_id)
    if not metrics:
        raise HTTPException(status_code=404, detail=f"No metrics for component: {component_id}")
    
    return metrics

# Mount standard routers (REQUIRED)
mount_standard_routers(app, routers)

# Import and include MCP router (remains at /api/mcp/v2)
try:
    from nexus.api.endpoints import mcp
    app.include_router(mcp.router, prefix="/api/mcp/v2", tags=["mcp"])
except ImportError:
    logger.warning("MCP endpoints not available")

# Add shutdown endpoint using shared utility
add_shutdown_endpoint_to_app(app, COMPONENT_NAME)

# Main module requirement
if __name__ == "__main__":
    from shared.utils.socket_server import run_with_socket_reuse
    
    # Get port from environment - NEVER hardcode
    port = int(os.environ.get("NEXUS_PORT"))
    
    # Use socket reuse for quick port release
    run_with_socket_reuse(
        "nexus.api.app:app",
        host="0.0.0.0",
        port=port,
        timeout_graceful_shutdown=3,
        server_header=False,
        access_log=False
    )
```

### Step 7: Create MCP Endpoints

```python
# nexus/api/endpoints/mcp.py
"""
MCP v2 Endpoints for Nexus
"""

import logging
from typing import Dict, List, Any
from fastapi import APIRouter, HTTPException, Depends
from tekton.models.base import TektonBaseModel
from pydantic import Field

from nexus.api.dependencies import get_connection_manager
from nexus.core.connection_manager import ConnectionManager

logger = logging.getLogger(__name__)

router = APIRouter()

# MCP v2 Models
class Tool(TektonBaseModel):
    """MCP Tool definition"""
    name: str
    description: str
    inputSchema: Dict[str, Any]

class ToolList(TektonBaseModel):
    """Response for tool listing"""
    tools: List[Tool]

class ToolCall(TektonBaseModel):
    """Request to call a tool"""
    name: str
    arguments: Dict[str, Any] = Field(default_factory=dict)

class ToolResponse(TektonBaseModel):
    """Response from tool execution"""
    content: List[Dict[str, Any]]
    isError: bool = False

# Define available tools
AVAILABLE_TOOLS = [
    Tool(
        name="list_connections",
        description="List all component connections and their status",
        inputSchema={
            "type": "object",
            "properties": {},
            "required": []
        }
    ),
    Tool(
        name="test_connection",
        description="Test connectivity to a specific component",
        inputSchema={
            "type": "object",
            "properties": {
                "component_id": {
                    "type": "string",
                    "description": "ID of the component to test"
                }
            },
            "required": ["component_id"]
        }
    ),
    Tool(
        name="get_connection_metrics",
        description="Get performance metrics for a component connection",
        inputSchema={
            "type": "object",
            "properties": {
                "component_id": {
                    "type": "string",
                    "description": "ID of the component"
                }
            },
            "required": ["component_id"]
        }
    )
]

@router.post("/v2/tools/list", response_model=ToolList)
async def list_tools() -> ToolList:
    """List available MCP tools."""
    return ToolList(tools=AVAILABLE_TOOLS)

@router.post("/v2/tools/call", response_model=ToolResponse)
async def call_tool(
    request: ToolCall,
    connection_manager: ConnectionManager = Depends(get_connection_manager)
) -> ToolResponse:
    """Execute an MCP tool."""
    try:
        if request.name == "list_connections":
            connections = await connection_manager.get_all_connections()
            content = [
                {
                    "type": "text",
                    "text": f"{conn.component_name}: {conn.status} (port {conn.port})"
                }
                for conn in connections
            ]
            return ToolResponse(content=content)
            
        elif request.name == "test_connection":
            component_id = request.arguments.get("component_id")
            if not component_id:
                raise ValueError("component_id is required")
                
            connection = await connection_manager.test_connection(component_id)
            return ToolResponse(
                content=[{
                    "type": "text",
                    "text": f"{connection.component_name}: {connection.status} (latency: {connection.latency_ms:.2f}ms)"
                }]
            )
            
        elif request.name == "get_connection_metrics":
            component_id = request.arguments.get("component_id")
            if not component_id:
                raise ValueError("component_id is required")
                
            metrics = await connection_manager.get_connection_metrics(component_id)
            if metrics:
                return ToolResponse(
                    content=[{
                        "type": "text",
                        "text": f"Metrics for {component_id}: Success rate: {metrics.success_rate:.2%}, Avg latency: {metrics.avg_latency_ms:.2f}ms"
                    }]
                )
            else:
                return ToolResponse(
                    content=[{"type": "text", "text": f"No metrics available for {component_id}"}]
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

Create dependencies:

```python
# nexus/api/dependencies.py
"""Dependency injection for Nexus API"""

from fastapi import HTTPException
from nexus.core.connection_manager import ConnectionManager

async def get_connection_manager() -> ConnectionManager:
    """Get the connection manager instance."""
    from nexus.api.app import app
    
    if not hasattr(app.state, "connection_manager"):
        raise HTTPException(status_code=503, detail="Connection manager not initialized")
    
    return app.state.connection_manager
```

## Phase 3: CLI Implementation

### Step 8: Create CLI

```python
# nexus/cli/main.py
#!/usr/bin/env python3
"""
Nexus CLI

Command-line interface for Nexus connection manager.
"""

import os
import asyncio
import click
import httpx
from rich.console import Console
from rich.table import Table
from rich.live import Live
from datetime import datetime

console = Console()

DEFAULT_API_URL = f"http://localhost:{os.environ.get('NEXUS_PORT', 8016)}"

class NexusClient:
    """Client for interacting with Nexus API."""
    
    def __init__(self, base_url: str = DEFAULT_API_URL):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=10.0)
    
    async def get_health(self):
        """Get health status."""
        response = await self.client.get(f"{self.base_url}/health")
        return response.json()
    
    async def list_connections(self):
        """List all connections."""
        response = await self.client.get(f"{self.base_url}/api/connections")
        return response.json()
    
    async def test_connection(self, component_id: str):
        """Test a specific connection."""
        response = await self.client.post(f"{self.base_url}/api/connections/{component_id}/test")
        return response.json()
    
    async def get_metrics(self, component_id: str):
        """Get connection metrics."""
        response = await self.client.get(f"{self.base_url}/api/connections/{component_id}/metrics")
        return response.json()
    
    async def close(self):
        """Close the client."""
        await self.client.aclose()

@click.group()
@click.option('--api-url', default=DEFAULT_API_URL, help='Nexus API URL')
@click.pass_context
def cli(ctx, api_url):
    """Nexus CLI - Connection management for Tekton."""
    ctx.ensure_object(dict)
    ctx.obj['client'] = NexusClient(api_url)

@cli.command()
@click.pass_context
def status(ctx):
    """Check Nexus status."""
    async def _status():
        client = ctx.obj['client']
        try:
            health = await client.get_health()
            
            table = Table(title="Nexus Status")
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
    
    asyncio.run(_status())

@cli.command()
@click.pass_context
def list_connections(ctx):
    """List all component connections."""
    async def _list():
        client = ctx.obj['client']
        try:
            connections = await client.list_connections()
            
            table = Table(title="Component Connections")
            table.add_column("Component", style="cyan")
            table.add_column("Status", style="green")
            table.add_column("Port")
            table.add_column("Last Seen")
            table.add_column("Latency")
            
            for conn in connections:
                status_style = {
                    "connected": "green",
                    "disconnected": "red",
                    "degraded": "yellow",
                    "unknown": "gray"
                }.get(conn['status'], "white")
                
                last_seen = datetime.fromisoformat(conn['last_seen'].replace('Z', '+00:00'))
                last_seen_str = last_seen.strftime("%Y-%m-%d %H:%M:%S")
                
                latency_str = f"{conn.get('latency_ms', 0):.2f}ms" if conn.get('latency_ms') else "N/A"
                
                table.add_row(
                    conn['component_name'],
                    f"[{status_style}]{conn['status']}[/{status_style}]",
                    str(conn['port']),
                    last_seen_str,
                    latency_str
                )
            
            console.print(table)
            
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
        finally:
            await client.close()
    
    asyncio.run(_list())

@cli.command()
@click.argument('component_id')
@click.pass_context
def test_connection(ctx, component_id):
    """Test connection to a specific component."""
    async def _test():
        client = ctx.obj['client']
        try:
            with console.status(f"Testing connection to {component_id}..."):
                result = await client.test_connection(component_id)
            
            status_style = {
                "connected": "green",
                "disconnected": "red",
                "degraded": "yellow"
            }.get(result['status'], "white")
            
            console.print(f"Component: {result['component_name']}")
            console.print(f"Status: [{status_style}]{result['status']}[/{status_style}]")
            if result.get('latency_ms'):
                console.print(f"Latency: {result['latency_ms']:.2f}ms")
            
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
        finally:
            await client.close()
    
    asyncio.run(_test())

@cli.command()
@click.option('--interval', default=5, help='Update interval in seconds')
@click.pass_context
def monitor(ctx, interval):
    """Monitor connections in real-time."""
    async def _monitor():
        client = ctx.obj['client']
        
        def generate_table():
            return Table(title=f"Connection Monitor (Updated every {interval}s)")
        
        try:
            with Live(generate_table(), refresh_per_second=1) as live:
                while True:
                    connections = await client.list_connections()
                    
                    table = generate_table()
                    table.add_column("Component", style="cyan")
                    table.add_column("Status")
                    table.add_column("Latency")
                    table.add_column("Errors")
                    
                    for conn in connections:
                        status_style = {
                            "connected": "green",
                            "disconnected": "red",
                            "degraded": "yellow",
                            "unknown": "gray"
                        }.get(conn['status'], "white")
                        
                        latency_str = f"{conn.get('latency_ms', 0):.2f}ms" if conn.get('latency_ms') else "N/A"
                        
                        table.add_row(
                            conn['component_name'],
                            f"[{status_style}]● {conn['status']}[/{status_style}]",
                            latency_str,
                            str(conn.get('error_count', 0))
                        )
                    
                    live.update(table)
                    await asyncio.sleep(interval)
                    
        except KeyboardInterrupt:
            console.print("\n[yellow]Monitoring stopped[/yellow]")
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
        finally:
            await client.close()
    
    asyncio.run(_monitor())

def main():
    """Main entry point."""
    cli()

if __name__ == "__main__":
    main()
```

## Phase 4: UI Implementation

### Step 9: Create UI Component

Follow the [UI Implementation Guide](./UI_Implementation_Guide.md) to create:
- `ui/nexus-component.html`
- `ui/scripts/nexus.js`
- `ui/styles/nexus.css`

## Phase 5: Testing

### Step 10: Create Tests

```python
# tests/test_connection_manager.py
import pytest
import asyncio
from datetime import datetime

from nexus.core.connection_manager import ConnectionManager
from nexus.models.connection import ConnectionStatus

@pytest.fixture
async def connection_manager():
    """Create a connection manager for testing."""
    manager = ConnectionManager(check_interval=1)
    await manager.initialize()
    yield manager
    await manager.cleanup()

@pytest.mark.asyncio
async def test_register_connection(connection_manager):
    """Test registering a new connection."""
    connection = await connection_manager.register_connection(
        component_id="test-component",
        name="Test Component",
        endpoint="localhost",
        port=8000
    )
    
    assert connection.component_id == "test-component"
    assert connection.component_name == "Test Component"
    assert connection.port == 8000
    assert connection.status == ConnectionStatus.DISCONNECTED  # No real server

@pytest.mark.asyncio
async def test_get_all_connections(connection_manager):
    """Test getting all connections."""
    # Register multiple connections
    await connection_manager.register_connection("comp1", "Component 1", "localhost", 8001)
    await connection_manager.register_connection("comp2", "Component 2", "localhost", 8002)
    
    connections = await connection_manager.get_all_connections()
    assert len(connections) == 2
    assert any(c.component_id == "comp1" for c in connections)
    assert any(c.component_id == "comp2" for c in connections)

# Create test runner
# tests/conftest.py
import pytest
import asyncio

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
```

### Step 11: Create Integration Test

```python
# examples/test_fastmcp.py
#!/usr/bin/env python3
"""Test FastMCP integration for Nexus"""

import asyncio
import httpx
import json

async def test_mcp_tools():
    """Test MCP tool listing and execution."""
    base_url = "http://localhost:8016"
    
    async with httpx.AsyncClient() as client:
        # List tools
        print("Listing MCP tools...")
        response = await client.post(f"{base_url}/mcp/v2/tools/list")
        tools = response.json()
        print(f"Available tools: {json.dumps(tools, indent=2)}")
        
        # Call list_connections tool
        print("\nCalling list_connections tool...")
        response = await client.post(
            f"{base_url}/mcp/v2/tools/call",
            json={"name": "list_connections", "arguments": {}}
        )
        result = response.json()
        print(f"Result: {json.dumps(result, indent=2)}")

if __name__ == "__main__":
    asyncio.run(test_mcp_tools())
```

## Phase 5: Launch Scripts

### Step 11: Create setup.sh

```bash
#!/bin/bash
# Setup script for Nexus

set -e  # Exit on error

# Ensure the script is run from the Nexus directory
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
echo "Installing Nexus in development mode..."
pip install -e .

# Make run script executable
chmod +x run_nexus.sh

echo "Nexus setup complete!"
echo "Run './run_nexus.sh' to start the Nexus server."
```

### Step 12: Create run_nexus.sh

```bash
#!/bin/bash
# Launch script for Nexus - follows Tekton standards

# ANSI color codes for visibility
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Component name and port configuration
COMPONENT_NAME="Nexus"
COMPONENT_MODULE="nexus"
PORT_VAR="NEXUS_PORT"

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Set up Python path to include component and Tekton root
export PYTHONPATH="$SCRIPT_DIR:$(dirname "$SCRIPT_DIR"):$PYTHONPATH"

# Get port from environment (NO hardcoded ports!)
PORT="${!PORT_VAR}"
if [ -z "$PORT" ]; then
    echo -e "${RED}Error: $PORT_VAR not set${NC}"
    echo "Please set the port in your environment or .env file"
    exit 1
fi

# Check if port is already in use
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null ; then
    echo -e "${RED}Error: Port $PORT is already in use${NC}"
    echo "Another service is using this port. Check with: lsof -i :$PORT"
    exit 1
fi

# Create log directory if it doesn't exist
LOG_DIR="$HOME/.tekton/logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/$COMPONENT_MODULE.log"

# Activate virtual environment if present
if [ -d "venv" ]; then
    echo -e "${GREEN}Activating virtual environment...${NC}"
    source venv/bin/activate
fi

# Start the component
echo -e "${GREEN}Starting $COMPONENT_NAME on port $PORT...${NC}"
echo "Logging to: $LOG_FILE"

# Run the component with proper module path
python -m $COMPONENT_MODULE "$@" 2>&1 | tee -a "$LOG_FILE" &
PID=$!

# Health check loop (30 second timeout)
echo -e "${YELLOW}Waiting for $COMPONENT_NAME to start...${NC}"
for i in {1..30}; do
    if curl -s "http://localhost:$PORT/health" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ $COMPONENT_NAME is running!${NC}"
        echo -e "${GREEN}API Documentation: http://localhost:$PORT/docs${NC}"
        echo -e "${GREEN}Health Check: http://localhost:$PORT/health${NC}"
        echo -e "${GREEN}Process ID: $PID${NC}"
        exit 0
    fi
    sleep 1
    echo -n "."
done

echo -e "\n${RED}✗ $COMPONENT_NAME failed to start within 30 seconds${NC}"
echo "Check the logs at: $LOG_FILE"
exit 1
```

## Phase 6: Documentation

### Step 13: Update Documentation

1. Add Nexus to `/config/port_assignments.md`
2. Create `/MetaData/ComponentDocumentation/Nexus/` directory
3. Add component-specific documentation
4. Update Hermes component registry

## Final Steps

### Step 14: Test Everything

```bash
# 1. Setup the component
./setup.sh

# 2. Set environment variable
export NEXUS_PORT=8016

# 3. Start the server
./run_nexus.sh

# 4. In another terminal, test the health endpoint
curl http://localhost:8016/health

# 5. Test the status endpoint
curl http://localhost:8016/status

# 6. Test the shutdown endpoint
curl -X POST http://localhost:8016/shutdown

# 7. Test with tekton-status
tekton-status

# 8. Test the CLI
nexus status
nexus list-connections

# 9. Test MCP integration
python examples/test_fastmcp.py

# 10. Access the UI
# Open Hephaestus and navigate to Nexus component
```

### Step 15: Integration Checklist

Based on the Shared Utilities Sprint standards:

- [ ] Uses lifespan pattern (no @app.on_event)
- [ ] Imports all shared utilities correctly
- [ ] Uses setup_component_logging() not logging.getLogger()
- [ ] Gets port from environment (never hardcoded)
- [ ] Includes socket release delay (0.5s) after shutdown
- [ ] Registers with Hermes successfully
- [ ] Implements /health endpoint with create_health_response
- [ ] Implements /status endpoint for tekton-status
- [ ] Has shutdown endpoint via add_shutdown_endpoint_to_app(app, "nexus")
- [ ] Launch script uses ANSI colors and lsof checking
- [ ] Logs to ~/.tekton/logs/
- [ ] Component appears in tekton-status as healthy
- [ ] MCP tools are accessible
- [ ] CLI commands work correctly
- [ ] UI component loads in Hephaestus
- [ ] WebSocket connections work
- [ ] Main module has if __name__ == "__main__": block

## Common Issues and Solutions

### Port Already in Use
```bash
# Find what's using the port
lsof -i :8016

# Kill the process if needed
kill -9 <PID>
```

### Import Errors
- Ensure you're in the virtual environment
- Check PYTHONPATH includes Tekton directories
- Verify shared utilities are available

### Hermes Registration Fails
- Check Hermes is running on port 8001
- Verify network connectivity
- Check registration payload format

### UI Not Loading
- Ensure component is registered with Hermes
- Check browser console for errors
- Verify WebSocket connection

## Next Steps

1. **Enhance Functionality** - Add more specific features
2. **Add More MCP Tools** - Expand capabilities
3. **Improve UI** - Add visualizations and controls
4. **Write More Tests** - Increase coverage
5. **Performance Optimization** - Profile and optimize

---

*Remember: Keep it simple, test everything, document clearly*

---

*Next: [Shared Patterns Reference](./Shared_Patterns_Reference.md)*
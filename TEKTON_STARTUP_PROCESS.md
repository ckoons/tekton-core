# Tekton Startup Process

## Overview

This document describes the startup process for the Tekton ecosystem components, including 
dependency management, registration with Hermes, and cross-component communication.

## Component Architecture

Tekton consists of several key components that work together:

1. **Engram** - Memory and persistence system
2. **Hermes** - Database services and message bus
3. **Athena** - Knowledge graph
4. **Sophia** - Machine learning engine
5. **Prometheus** - Planning engine
6. **Synthesis** - Execution engine
7. **Harmonia** - Workflow orchestration
8. **Rhetor** - Communication system
9. **Telos** - User interface

Components have dependencies on each other, which must be respected during startup to ensure 
proper initialization. The general dependency order is:

1. Core infrastructure (Engram, Hermes)
2. Knowledge services (Athena, Sophia)
3. Planning and execution (Prometheus, Synthesis)
4. Orchestration (Harmonia)
5. User-facing components (Rhetor, Telos)

## Startup Process Implementation

Tekton uses a structured startup process built around `StartUpInstructions` and `ComponentRegistration` 
classes defined in the `tekton-core` package.

### StartUpInstructions

The `StartUpInstructions` class provides a standardized way to specify component initialization parameters:

```python
class StartUpInstructions:
    """Container for instructions passed to components during startup."""
    
    def __init__(self, 
                component_id: str,
                component_type: str,
                data_directory: Optional[str] = None,
                config_file: Optional[str] = None,
                options: Optional[Dict[str, Any]] = None,
                dependencies: Optional[List[str]] = None,
                hermes_url: Optional[str] = None,
                register: bool = True,
                capabilities: Optional[List[Dict[str, Any]]] = None,
                metadata: Optional[Dict[str, Any]] = None):
        """Initialize startup instructions."""
        # ...
```

This class standardizes how components receive their configuration and dependency information, making it
easier to ensure consistent startup behavior across components.

### ComponentRegistration

The `ComponentRegistration` class handles the registration of components with the Hermes service registry:

```python
class ComponentRegistration:
    """Handles component registration with Hermes and startup coordination."""
    
    def __init__(self,
                component_id: str,
                component_name: str,
                version: str = "0.1.0",
                hermes_url: Optional[str] = None,
                capabilities: Optional[List[Dict[str, Any]]] = None,
                metadata: Optional[Dict[str, Any]] = None):
        """Initialize the component registration."""
        # ...
```

This class ensures that components can advertise their capabilities to other components in the ecosystem
and participate in service discovery.

### StartUpProcess

The `StartUpProcess` class coordinates the startup of a component, including dependency checks:

```python
class StartUpProcess:
    """Manages the startup process for a component."""
    
    def __init__(self, 
                component_id: str,
                component_name: str,
                version: str = "0.1.0",
                startup_handlers: Optional[Dict[str, Callable]] = None):
        """Initialize the startup process."""
        # ...
```

This class provides a structured way to initialize components, check dependencies, and handle 
startup failures.

## Hermes Restart Handling

Tekton includes automatic re-registration and reconnection when Hermes restarts. This is handled by the 
`HeartbeatMonitor` class which:

1. Maintains heartbeats to Hermes to indicate component health
2. Detects when Hermes becomes unavailable
3. Automatically attempts to re-register components when Hermes restarts
4. Restores service connections across components

```python
class HeartbeatMonitor:
    """
    Monitors the connection to Hermes and handles reconnection.
    
    This class maintains heartbeats to Hermes and automatically
    re-registers components if Hermes restarts or becomes unavailable.
    """
```

Components use a simplified interface `ComponentHeartbeat` to integrate with the monitoring system:

```python
class ComponentHeartbeat:
    """
    Simplified interface for component heartbeat management.
    
    This class provides a simplified interface for components to manage
    their connection to Hermes, including automatic reconnection.
    """
```

### Reconnection Sequence

When Hermes restarts, the following sequence occurs:

1. HeartbeatMonitor detects failed heartbeats from components to Hermes
2. After consecutive failures, it checks if Hermes is available
3. If Hermes has restarted, it re-registers all tracked components
4. Components resume heartbeats with the newly started Hermes instance
5. Service discovery is restored across the ecosystem

This ensures that even if Hermes restarts, the entire Tekton ecosystem can recover automatically.

## Launch Scripts

Tekton provides several ways to launch components:

### 1. Bash Script: tekton_launch

The `tekton_launch` script is a Bash script that launches Tekton components based on command-line options.
It detects available components, ensures dependencies are met, and launches them in the correct order.

Usage:
```bash
tekton_launch [OPTIONS] [COMPONENTS...]
```

### 2. Bash Script: tekton_launch_components

The `tekton_launch_components` script is a more targeted script for launching specific components.
It handles registration with Hermes and initializes components with appropriate virtual environments.

Usage:
```bash
tekton_launch_components [OPTIONS] [COMPONENTS...]
```

### 3. Python Script: tekton_launcher.py

The `tekton_launcher.py` script is a Python implementation of the launcher that uses the 
`StartUpInstructions` and `StartUpProcess` classes to coordinate component startup. It also supports
continuous monitoring and automatic restart of components.

Usage:
```bash
python tekton_launcher.py [OPTIONS] [COMPONENTS...]
```

Key options for `tekton_launcher.py`:
- `--restart`: Keep the launcher running to monitor components and handle Hermes restarts
- `--all`: Launch all available components
- `--direct`: Run components in-process (not as subprocesses)
- `--hermes-url`: Specify the URL of the Hermes API

## Component Registration with Hermes

Each component should provide a `register_with_hermes.py` script in its `scripts` directory
that handles registration with the Hermes service registry. This script should:

1. Accept `StartUpInstructions` from the launcher
2. Define the component's capabilities
3. Register with Hermes using the `ComponentRegistration` class
4. Set up heartbeat monitoring to maintain connection with Hermes
5. Handle graceful shutdown when instructed

Example:
```python
async def register_with_hermes(instructions_file: Optional[str] = None, hermes_url: Optional[str] = None):
    """Register component with Hermes."""
    # Load StartUpInstructions if available
    if instructions_file and os.path.isfile(instructions_file):
        instructions = StartUpInstructions.from_file(instructions_file)
        # ...
    
    # Set up heartbeat monitoring
    heartbeat = ComponentHeartbeat(
        component_id=component_id,
        component_name=component_name,
        hermes_url=hermes_url,
        capabilities=capabilities,
        metadata=metadata
    )
    
    # Start heartbeat (this also handles registration)
    await heartbeat.start()
    
    # Keep running to maintain heartbeat
    # ...
```

## Startup Order and Dependencies

The proper startup order for Tekton components is:

1. **Engram** - Memory services first (no dependencies)
2. **Hermes** - Message bus and database services (depends on: none)
3. **Athena** - Knowledge graph (depends on: Hermes)
4. **Sophia** - Machine learning (depends on: Hermes)
5. **Prometheus** - Planning (depends on: Athena)
6. **Synthesis** - Execution (depends on: Prometheus)
7. **Harmonia** - Workflow (depends on: Hermes)
8. **Rhetor** - Communication (depends on: Sophia)
9. **Telos** - User interface (depends on: Rhetor)

The launcher scripts ensure that components are started in an order that respects these dependencies.

## Capabilities Registration

Components should register their capabilities with Hermes to enable discovery by other components.
Capabilities are defined as a list of objects with the following structure:

```json
{
    "name": "capability_name",
    "description": "Description of the capability",
    "parameters": {
        "param1": "data_type",
        "param2": "data_type (optional)"
    }
}
```

This allows components to discover and use each other's functionality without hard-coded dependencies.

## Component Isolation with Virtual Environments

Each Tekton component is designed to run in its own virtual environment for isolation. The startup process:

1. Checks for an existing virtual environment at `component/venv/`
2. If not found, creates one using the component's `setup.sh` script
3. Uses the component's virtual environment Python when launching scripts

This isolation ensures that components can have different dependencies without conflicts, while
still enabling cross-component communication through standardized interfaces.

## Example: Manual Component Launch

To manually launch a component with the proper startup process:

```bash
# 1. Create StartUpInstructions
cat > /tmp/component_instructions.json << EOL
{
    "component_id": "component.core",
    "component_type": "component",
    "data_directory": "/path/to/data",
    "dependencies": ["dependency1.core", "dependency2.core"],
    "register": true,
    "capabilities": [
        {
            "name": "capability1",
            "description": "Description of capability 1",
            "parameters": {
                "param1": "string"
            }
        }
    ],
    "metadata": {
        "description": "Component description",
        "version": "0.1.0"
    }
}
EOL

# 2. Set environment variables
export STARTUP_INSTRUCTIONS_FILE=/tmp/component_instructions.json
export HERMES_URL=http://localhost:5000/api

# 3. Run the registration script
python -m component.scripts.register_with_hermes
```

## Hermes Integration

Components integrate with Hermes in several ways:

1. **Service Registration**: Components register their services and capabilities
2. **Service Discovery**: Components discover other components' capabilities
3. **Message Bus**: Components communicate via Hermes message bus
4. **Database Services**: Components use Hermes database adapters
5. **Heartbeat Monitoring**: Components maintain heartbeats for health tracking

The `ComponentRegistration` class handles service registration and discovery, while the
`HeartbeatMonitor` ensures robust connection management across service restarts.

## Running a Complete Launch Sequence

To launch the complete Tekton ecosystem:

```bash
# 1. Start core services (Engram and Hermes)
./scripts/tekton_launcher.py --restart Engram Hermes

# 2. Once core services are running, start knowledge components
./scripts/tekton_launcher.py --restart Athena Sophia

# 3. Start planning and execution components
./scripts/tekton_launcher.py --restart Prometheus Synthesis

# 4. Start workflow and user-facing components
./scripts/tekton_launcher.py --restart Harmonia Rhetor Telos
```

Alternatively, launch everything at once (the launcher will handle dependencies):

```bash
./scripts/tekton_launcher.py --restart --all
```

## Conclusion

The Tekton startup process provides a structured way to initialize, register, and coordinate 
components in the ecosystem. By using `StartUpInstructions`, `ComponentRegistration`, and
`StartUpProcess`, components can be started in the correct order with proper dependency management.

The system is resilient to restarts, with heartbeat monitoring and automatic re-registration
ensuring continuous operation even when core services like Hermes restart.

Future enhancements may include:

- Full distributed deployment support
- Dynamic scaling of components
- Enhanced health monitoring and metrics
- Configuration validation and management
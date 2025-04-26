# Telos Integration Guide

This guide provides details on how to integrate with the Telos requirements management system from other components within the Tekton ecosystem as well as from external systems.

## Overview

Telos provides multiple integration points for other components within Tekton and for external systems:

1. **REST API**: HTTP-based API for requirements management
2. **WebSocket API**: Real-time updates and notifications
3. **Events API**: Server-sent events for asynchronous communication
4. **Component Clients**: Pre-built client libraries for Tekton components
5. **UI Component**: Shadow DOM component for Hephaestus UI integration

All integration points follow the Single Port Architecture pattern, with communication consolidated through port 8008 by default.

## Single Port Architecture

Telos follows the Tekton Single Port Architecture pattern, using path-based routing for different types of communication:

- **HTTP API**: `/api/*` endpoints for RESTful interactions
- **WebSocket**: `/ws` endpoint for real-time bidirectional communication
- **Events**: `/events` endpoint for server-sent events

This architecture simplifies integration by providing all services through a single port (8008 by default), making it easier to configure firewalls, proxies, and service discovery.

## Hermes Integration

Telos registers itself with Hermes to make its capabilities available to other Tekton components.

### Registration Process

When started, Telos registers these capabilities with Hermes:

```json
{
  "service_id": "telos.requirements",
  "name": "Telos Requirements Manager",
  "capabilities": [
    "create_project",
    "create_requirement",
    "get_project",
    "get_requirements",
    "analyze_requirements",
    "refine_requirement"
  ],
  "metadata": {
    "description": "Requirements management and refinement for Tekton",
    "ui_available": true,
    "cli_available": true,
    "prometheus_integration": true,
    "single_port_architecture": true,
    "port": "8008"
  }
}
```

### Service Discovery

Other components can discover Telos through Hermes with this code:

```python
from tekton.utils.component_client import discover_component

# Discover Telos service
telos_service = await discover_component("telos.requirements")

# Get endpoint information
endpoint = telos_service.get("endpoint")
capabilities = telos_service.get("capabilities")
```

## Integrating with the REST API

Telos provides a comprehensive REST API for requirements management. See the [API Reference](telos_api_reference.md) for detailed documentation.

### Authentication

The API currently does not require authentication. Future versions will add authentication mechanisms.

### Basic Usage

#### Python Example

```python
import requests

# Base URL for Telos API
TELOS_API_URL = "http://localhost:8008/api"

# Create a project
def create_project(name, description=None, metadata=None):
    response = requests.post(f"{TELOS_API_URL}/projects", json={
        "name": name,
        "description": description or "",
        "metadata": metadata or {}
    })
    return response.json()

# Create a requirement
def create_requirement(project_id, title, description, **kwargs):
    response = requests.post(f"{TELOS_API_URL}/projects/{project_id}/requirements", json={
        "title": title,
        "description": description,
        **kwargs
    })
    return response.json()

# Get all requirements for a project
def get_requirements(project_id, **filters):
    response = requests.get(f"{TELOS_API_URL}/projects/{project_id}/requirements", params=filters)
    return response.json()

# Example usage
project = create_project("Integration Test Project", "Testing API integration")
print(f"Created project: {project['project_id']}")

requirement = create_requirement(
    project_id=project['project_id'],
    title="Test Requirement",
    description="This is a test requirement created via the API",
    requirement_type="functional",
    priority="medium"
)
print(f"Created requirement: {requirement['requirement_id']}")
```

#### JavaScript Example

```javascript
// Base URL for Telos API
const TELOS_API_URL = "http://localhost:8008/api";

// Create a project
async function createProject(name, description = "", metadata = {}) {
  const response = await fetch(`${TELOS_API_URL}/projects`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      name,
      description,
      metadata
    })
  });
  return response.json();
}

// Create a requirement
async function createRequirement(projectId, title, description, options = {}) {
  const response = await fetch(`${TELOS_API_URL}/projects/${projectId}/requirements`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      title,
      description,
      ...options
    })
  });
  return response.json();
}

// Example usage
async function testIntegration() {
  const project = await createProject("JS Integration Test", "Testing from JavaScript");
  console.log(`Created project: ${project.project_id}`);
  
  const requirement = await createRequirement(
    project.project_id,
    "Test Requirement",
    "This is a test requirement created from JavaScript",
    {
      requirement_type: "functional",
      priority: "medium",
      tags: ["test", "api", "integration"]
    }
  );
  console.log(`Created requirement: ${requirement.requirement_id}`);
}

testIntegration().catch(console.error);
```

### Error Handling

The API uses standard HTTP status codes to indicate success or failure:

- `200 OK`: Successful operation
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request parameters
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

```python
import requests

def get_project(project_id):
    response = requests.get(f"{TELOS_API_URL}/projects/{project_id}")
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 404:
        print(f"Project {project_id} not found")
        return None
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None
```

## Integrating with the WebSocket API

The WebSocket API provides real-time updates for requirements changes.

### Connecting to the WebSocket

```javascript
// Connect to WebSocket
const ws = new WebSocket("ws://localhost:8008/ws");

// Handle connection open
ws.onopen = () => {
  console.log("Connected to Telos WebSocket");
  
  // Register client
  ws.send(JSON.stringify({
    type: "REGISTER",
    source: "client-123",
    target: "server",
    timestamp: Date.now(),
    payload: {}
  }));
};

// Handle messages
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log("Received:", data);
  
  // Handle different message types
  if (data.type === "RESPONSE") {
    console.log("Response:", data.payload);
  } else if (data.type === "UPDATE") {
    console.log("Update:", data.payload);
    // Handle the update (e.g., refresh UI)
  } else if (data.type === "ERROR") {
    console.error("Error:", data.payload.error);
  }
};

// Handle errors
ws.onerror = (error) => {
  console.error("WebSocket error:", error);
};

// Handle disconnection
ws.onclose = (event) => {
  console.log("Disconnected from WebSocket:", event.code, event.reason);
  // Implement reconnection logic if needed
};
```

### Subscribing to Updates

```javascript
// Subscribe to project updates
function subscribeToProject(projectId) {
  ws.send(JSON.stringify({
    type: "PROJECT_SUBSCRIBE",
    source: "client-123",
    target: "server",
    timestamp: Date.now(),
    payload: {
      project_id: projectId
    }
  }));
}

// Subscribe to a specific project
subscribeToProject("project-456");
```

### Python WebSocket Client

```python
import asyncio
import json
import websockets

async def connect_to_telos_websocket():
    uri = "ws://localhost:8008/ws"
    
    async with websockets.connect(uri) as websocket:
        # Register client
        await websocket.send(json.dumps({
            "type": "REGISTER",
            "source": "python-client",
            "target": "server",
            "timestamp": int(time.time() * 1000),
            "payload": {}
        }))
        
        # Subscribe to a project
        await websocket.send(json.dumps({
            "type": "PROJECT_SUBSCRIBE",
            "source": "python-client",
            "target": "server",
            "timestamp": int(time.time() * 1000),
            "payload": {
                "project_id": "project-123"
            }
        }))
        
        # Listen for messages
        while True:
            message = await websocket.recv()
            data = json.loads(message)
            
            if data["type"] == "UPDATE":
                # Handle update
                resource_type = data["payload"]["resource_type"]
                resource_id = data["payload"]["resource_id"]
                action = data["payload"]["action"]
                
                print(f"Update: {action} {resource_type} {resource_id}")
                # Process the update

# Run the client
asyncio.run(connect_to_telos_websocket())
```

## Using the Component Client

Tekton provides a standardized component client for easy integration.

### Installing the Client

```bash
# Install Tekton core utilities
pip install tekton-core
```

### Using the Client

```python
from tekton.utils.component_client import ComponentClient

async def use_telos_client():
    # Create the client
    telos_client = ComponentClient(
        component_id="telos.requirements",
        hermes_url="http://localhost:8001/api"  # Hermes API URL
    )
    
    # Invoke capabilities
    project = await telos_client.invoke_capability(
        "create_project",
        {
            "name": "Test Project",
            "description": "Created via component client"
        }
    )
    
    print(f"Created project: {project['project_id']}")
    
    # Create a requirement
    requirement = await telos_client.invoke_capability(
        "create_requirement",
        {
            "project_id": project["project_id"],
            "title": "Test Requirement",
            "description": "Created via component client",
            "requirement_type": "functional"
        }
    )
    
    print(f"Created requirement: {requirement['requirement_id']}")

# Run the client
import asyncio
asyncio.run(use_telos_client())
```

### Error Handling with Component Client

```python
from tekton.utils.component_client import (
    ComponentClient,
    ComponentNotFoundError,
    CapabilityNotFoundError,
    CapabilityInvocationError
)

async def safe_invoke_telos():
    try:
        # Create the client
        telos_client = ComponentClient(component_id="telos.requirements")
        
        # Invoke capability
        result = await telos_client.invoke_capability("get_project", {"project_id": "project-123"})
        return result
        
    except ComponentNotFoundError:
        print("Telos component not found. Is it registered with Hermes?")
    except CapabilityNotFoundError:
        print("The requested capability is not supported by Telos")
    except CapabilityInvocationError as e:
        print(f"Error invoking capability: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    
    return None
```

## UI Component Integration

Telos provides a shadow DOM component for integration with Hephaestus.

### Component Registration

Telos automatically registers its UI component with Hephaestus through this entry in the component registry:

```json
{
  "id": "telos",
  "name": "Telos",
  "description": "Requirements management, tracing and validation",
  "icon": "🎯",
  "defaultMode": "html",
  "capabilities": [
    "requirements_management", 
    "requirement_tracing", 
    "requirement_validation", 
    "hierarchical_visualization", 
    "prometheus_integration", 
    "shadow_dom", 
    "component_isolation",
    "state_management"
  ],
  "componentPath": "components/telos/telos-component.html",
  "scripts": [
    "scripts/telos/telos-service.js",
    "scripts/telos/telos-component.js",
    "scripts/telos/telos-integration.js"
  ],
  "styles": [
    "styles/telos/telos.css"
  ],
  "usesShadowDom": true
}
```

### Manual Component Loading

You can manually load the Telos component in any web page with this code:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Telos Integration</title>
    <script src="component-loader.js"></script>
    <script src="scripts/telos/telos-service.js"></script>
    <script src="scripts/telos/telos-component.js"></script>
</head>
<body>
    <h1>Telos Integration Demo</h1>
    
    <div id="telos-container"></div>
    
    <script>
        // Load the Telos component
        const componentLoader = new ComponentLoader();
        componentLoader.loadComponent({
            id: "telos",
            name: "Telos",
            containerElement: document.getElementById("telos-container"),
            componentPath: "components/telos/telos-component.html",
            scripts: [
                "scripts/telos/telos-service.js",
                "scripts/telos/telos-component.js"
            ],
            styles: [
                "styles/telos/telos.css"
            ],
            usesShadowDom: true
        });
    </script>
</body>
</html>
```

### Accessing Component API

You can access the Telos component API from other components:

```javascript
// Get a reference to the Telos component
const telosComponent = document.querySelector('telos-component');

// Access component methods
const projectId = "project-123";
telosComponent.loadProject(projectId).then(() => {
    console.log("Project loaded");
});

// Listen for component events
telosComponent.addEventListener('requirement-created', (event) => {
    console.log("Requirement created:", event.detail);
});

// Set component properties
telosComponent.showValidation = true;
telosComponent.viewMode = 'board';
```

## LLM Integration

Telos integrates with Rhetor for LLM-powered requirement analysis.

### Direct Integration

You can use the LLM integration directly:

```python
from telos.ui.analyzers import RequirementAnalyzer
from telos.core.requirement import Requirement

async def analyze_requirement():
    # Create a requirement
    requirement = Requirement(
        requirement_id="req-test",
        title="User Authentication",
        description="The system should authenticate users",
        requirement_type="functional"
    )
    
    # Create an analyzer with LLM integration
    analyzer = RequirementAnalyzer(use_llm=True)
    
    # Analyze the requirement
    analysis = await analyzer.analyze_requirement(requirement)
    
    print(f"Quality score: {analysis['score']}")
    print("Suggestions:")
    for suggestion in analysis['suggestions']:
        print(f"- {suggestion}")

# Run the analysis
import asyncio
asyncio.run(analyze_requirement())
```

### Integration with Rhetor API

You can integrate with the Rhetor API for advanced prompt capabilities:

```python
from rhetor.client import get_rhetor_prompt_client

async def generate_requirement_template():
    # Get Rhetor client
    rhetor_client = await get_rhetor_prompt_client()
    
    # Create a prompt template for requirements
    template_result = await rhetor_client.create_prompt_template(
        name="Functional Requirement Template",
        template="As a requirements engineer, write a clear, specific, and testable functional requirement for {feature} in a {system_type} system. The requirement should follow this format: 'The system shall [action] [object] [qualifier].' Include acceptance criteria and make sure the requirement is measurable.",
        variables=["feature", "system_type"],
        description="Template for generating functional requirements"
    )
    
    template_id = template_result["template_id"]
    
    # Use the template to generate a requirement
    prompt = await rhetor_client.render_prompt(
        template_id=template_id,
        variables={
            "feature": "user authentication",
            "system_type": "web application"
        }
    )
    
    print("Generated prompt:", prompt)
    
    # Use the prompt to get a requirement from the LLM
    # This would typically be sent to an LLM via Rhetor's LLM client

# Run the template generation
import asyncio
asyncio.run(generate_requirement_template())
```

## Prometheus Integration

Telos integrates with Prometheus for planning capabilities.

### Using the Prometheus Connector

```python
from telos.prometheus_connector import TelosPrometheusConnector
from telos.core.requirements_manager import RequirementsManager

async def create_plan_from_requirements():
    # Initialize requirements manager
    requirements_manager = RequirementsManager()
    
    # Initialize Prometheus connector
    prometheus_connector = TelosPrometheusConnector(requirements_manager)
    await prometheus_connector.initialize()
    
    # Create a plan from requirements
    project_id = "project-123"
    plan_result = await prometheus_connector.create_plan(project_id)
    
    print("Plan created:")
    print(f"Plan ID: {plan_result['plan_id']}")
    print(f"Number of tasks: {len(plan_result['tasks'])}")
    print(f"Estimated duration: {plan_result['estimated_duration']}")

# Run the planning
import asyncio
asyncio.run(create_plan_from_requirements())
```

### Analyzing Requirements for Planning

```python
from telos.prometheus_connector import TelosPrometheusConnector
from telos.core.requirements_manager import RequirementsManager

async def analyze_requirements_for_planning():
    # Initialize requirements manager
    requirements_manager = RequirementsManager()
    
    # Initialize Prometheus connector
    prometheus_connector = TelosPrometheusConnector(requirements_manager)
    await prometheus_connector.initialize()
    
    # Analyze requirements for planning readiness
    project_id = "project-123"
    analysis = await prometheus_connector.prepare_requirements_for_planning(project_id)
    
    print("Analysis results:")
    print(f"Status: {analysis['status']}")
    print(f"Ready requirements: {analysis['requirements_ready']}/{analysis['requirements_total']}")
    print("Suggestions:")
    for suggestion in analysis.get('suggestions', []):
        print(f"- {suggestion}")

# Run the analysis
import asyncio
asyncio.run(analyze_requirements_for_planning())
```

## CLI Integration

Telos provides a command-line interface that can be integrated with other systems.

### Scripting with the CLI

```bash
#!/bin/bash

# Create a project
PROJECT_ID=$(telos project create --name "Integration Test" --description "Testing CLI integration" --json | jq -r .project_id)

echo "Created project: $PROJECT_ID"

# Add a requirement
REQ_ID=$(telos requirement add --project-id $PROJECT_ID --title "Test Requirement" --description "This is a test requirement" --type functional --priority high --json | jq -r .requirement_id)

echo "Created requirement: $REQ_ID"

# Analyze requirements
telos refine analyze --project-id $PROJECT_ID --json | jq .
```

### Python Integration with CLI

```python
import subprocess
import json

def run_telos_command(cmd_args):
    """Run a Telos CLI command and return the JSON result."""
    # Add --json to get JSON output
    cmd = ["telos"] + cmd_args + ["--json"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return None
    
    return json.loads(result.stdout)

# Create a project
project = run_telos_command(["project", "create", "--name", "Python Integration", "--description", "Testing Python integration with CLI"])
project_id = project["project_id"]
print(f"Created project: {project_id}")

# Add a requirement
requirement = run_telos_command([
    "requirement", "add",
    "--project-id", project_id,
    "--title", "Test Requirement",
    "--description", "This is a test requirement created via Python CLI integration",
    "--type", "functional",
    "--priority", "medium"
])
print(f"Created requirement: {requirement['requirement_id']}")
```

## Data Import/Export Integration

Telos provides data import and export capabilities for integration with external systems.

### Exporting Data

```python
import requests
import json

def export_project(project_id, format="json"):
    """Export a project to the specified format."""
    response = requests.post(f"http://localhost:8008/api/projects/{project_id}/export", json={
        "format": format,
        "sections": ["metadata", "requirements", "traces"]
    })
    
    if response.status_code != 200:
        print(f"Error: {response.status_code} - {response.text}")
        return None
    
    return response.json()

# Export a project to JSON
project_data = export_project("project-123")

# Save to a file
with open("project_export.json", "w") as f:
    json.dump(project_data, f, indent=2)

print(f"Project exported to project_export.json")
```

### Importing Data

```python
import requests
import json

def import_project(data, format="json", merge_strategy="replace"):
    """Import a project from data."""
    response = requests.post("http://localhost:8008/api/projects/import", json={
        "data": data,
        "format": format,
        "merge_strategy": merge_strategy
    })
    
    if response.status_code != 201:
        print(f"Error: {response.status_code} - {response.text}")
        return None
    
    return response.json()

# Load data from a file
with open("project_export.json", "r") as f:
    import_data = json.load(f)

# Import the project
result = import_project(import_data)
print(f"Imported project: {result['project_id']}")
print(f"Imported {result['imported_requirements']} requirements")
```

## Advanced Integration Patterns

### Event-Driven Integration

```javascript
// Connect to WebSocket
const ws = new WebSocket("ws://localhost:8008/ws");

// Define event handlers
const eventHandlers = {
    "requirement.created": (data) => {
        console.log("Requirement created:", data);
        // Update UI or trigger other actions
    },
    "requirement.updated": (data) => {
        console.log("Requirement updated:", data);
        // Update UI or trigger other actions
    },
    "requirement.deleted": (data) => {
        console.log("Requirement deleted:", data);
        // Update UI or trigger other actions
    },
    "trace.created": (data) => {
        console.log("Trace created:", data);
        // Update UI or trigger other actions
    }
};

// Register for all events
ws.onopen = () => {
    // Register client
    ws.send(JSON.stringify({
        type: "REGISTER",
        source: "event-processor",
        target: "server",
        timestamp: Date.now(),
        payload: {}
    }));
    
    // Subscribe to project events
    ws.send(JSON.stringify({
        type: "PROJECT_SUBSCRIBE",
        source: "event-processor",
        target: "server",
        timestamp: Date.now(),
        payload: {
            project_id: "project-123"
        }
    }));
};

// Process events
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    
    // Handle update events
    if (data.type === "UPDATE") {
        const payload = data.payload;
        const eventType = `${payload.resource_type}.${payload.action}`;
        
        // Call the appropriate handler
        if (eventHandlers[eventType]) {
            eventHandlers[eventType](payload.data);
        }
    }
};
```

### Bulk Operations

```python
import requests
import json

def bulk_create_requirements(project_id, requirements):
    """Create multiple requirements at once."""
    results = []
    
    for req_data in requirements:
        response = requests.post(f"http://localhost:8008/api/projects/{project_id}/requirements", json=req_data)
        results.append(response.json())
    
    return results

# Example usage
requirements_data = [
    {
        "title": "User Registration",
        "description": "Users shall be able to register with email and password",
        "requirement_type": "functional",
        "priority": "high",
        "tags": ["user", "security"]
    },
    {
        "title": "Password Reset",
        "description": "Users shall be able to reset their password via email",
        "requirement_type": "functional",
        "priority": "medium",
        "tags": ["user", "security"]
    },
    {
        "title": "User Profile",
        "description": "Users shall be able to view and edit their profile information",
        "requirement_type": "functional",
        "priority": "medium",
        "tags": ["user", "profile"]
    }
]

created_requirements = bulk_create_requirements("project-123", requirements_data)
print(f"Created {len(created_requirements)} requirements")
```

### Chained Operations

```python
import requests

async def create_project_with_requirements(project_data, requirements_data):
    """Create a project with requirements and traces in a single operation."""
    # Create the project
    response = requests.post("http://localhost:8008/api/projects", json=project_data)
    project = response.json()
    project_id = project["project_id"]
    
    # Create requirements
    requirement_ids = []
    for req_data in requirements_data:
        response = requests.post(f"http://localhost:8008/api/projects/{project_id}/requirements", json=req_data)
        req = response.json()
        requirement_ids.append(req["requirement_id"])
    
    # Create traces between requirements
    for i in range(len(requirement_ids) - 1):
        # Create a trace from each requirement to the next one
        requests.post(f"http://localhost:8008/api/projects/{project_id}/traces", json={
            "source_id": requirement_ids[i],
            "target_id": requirement_ids[i + 1],
            "trace_type": "depends-on",
            "description": "Sequential dependency"
        })
    
    return {
        "project_id": project_id,
        "requirement_ids": requirement_ids
    }
```

## Security Considerations

### API Security

1. **Network Security**: Limit access to the Telos API (port 8008) to trusted networks
2. **HTTPS**: Configure a reverse proxy to provide HTTPS encryption for the API
3. **Authentication**: Future versions will include authentication
4. **Access Control**: Future versions will include role-based access control

### Data Security

1. **Input Validation**: All API endpoints validate input to prevent injection attacks
2. **Output Encoding**: API responses are properly encoded to prevent XSS
3. **File Security**: Project data is stored with proper permissions
4. **Data Privacy**: Be careful when exporting sensitive requirements data

## Common Integration Issues

### Troubleshooting

1. **Connection Issues**:
   - Ensure Telos is running and port 8008 is accessible
   - Check for firewall rules blocking access
   - Verify networking configuration

2. **API Errors**:
   - Check HTTP status codes and error messages
   - Validate request parameters against API documentation
   - Check for required fields in requests

3. **WebSocket Issues**:
   - Ensure proper connection initialization (REGISTER message)
   - Implement reconnection logic for dropped connections
   - Verify message format follows the expected structure

### Best Practices

1. **Use Component Clients**: When available, use the standard component client
2. **Implement Retry Logic**: Handle temporary failures with appropriate retries
3. **Validate Input**: Validate data before sending to the API
4. **Error Handling**: Implement proper error handling for all requests
5. **Logging**: Log API interactions for troubleshooting
6. **Rate Limiting**: Implement client-side rate limiting to avoid overloading the API
7. **Caching**: Cache frequently used data to reduce API calls
8. **Bulk Operations**: Use bulk operations when possible to reduce API calls

## Resources

- [API Reference](telos_api_reference.md) - Detailed API documentation
- [User Guide](Telos_User_Guide.md) - User guide for Telos
- [Data Model](Telos_Data_Model.md) - Detailed data model documentation
- [SINGLE_PORT_ARCHITECTURE.md](../docs/SINGLE_PORT_ARCHITECTURE.md) - Architecture details
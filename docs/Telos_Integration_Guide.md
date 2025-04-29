# Telos Integration Guide

This document provides comprehensive guidance for integrating Telos with other components in the Tekton ecosystem and with external systems.

## Table of Contents

1. [Introduction](#introduction)
2. [Integration Architecture](#integration-architecture)
3. [Hermes Integration](#hermes-integration)
4. [Prometheus Integration](#prometheus-integration)
5. [Rhetor Integration](#rhetor-integration)
6. [Hephaestus UI Integration](#hephaestus-ui-integration)
7. [Client Library](#client-library)
8. [WebSocket Integration](#websocket-integration)
9. [External System Integration](#external-system-integration)
10. [Single Port Architecture](#single-port-architecture)
11. [Data Models](#data-models)
12. [Security Considerations](#security-considerations)

## Introduction

Telos is designed to integrate seamlessly with other Tekton components and external systems. This guide covers key integration patterns, APIs, and examples for connecting Telos with:

- **Hermes**: For service registration and discovery
- **Prometheus**: For planning and task breakdown
- **Rhetor**: For LLM-powered requirement analysis
- **Hephaestus**: For UI components and interfaces
- **External systems**: Through API and WebSocket interfaces

## Integration Architecture

Telos follows a modular architecture that supports multiple integration patterns:

1. **Component Integration**: Direct integration with other Tekton components
2. **Client Library Integration**: Using the Telos client library for programmatic access
3. **HTTP API Integration**: RESTful API for external system integration
4. **WebSocket Integration**: For real-time updates and collaborative features
5. **UI Component Integration**: Shadow DOM component for web UI integration

## Hermes Integration

Telos integrates with Hermes for service registration and discovery.

### Registration Process

Telos automatically registers with Hermes during startup:

```python
async def register_with_hermes(self, service_registry=None) -> bool:
    """Register the requirements manager with the Hermes service registry."""
    try:
        # Try to import the service registry if not provided
        if service_registry is None:
            try:
                from hermes.core.service_discovery import ServiceRegistry
                service_registry = ServiceRegistry()
                await service_registry.start()
            except ImportError:
                logger.error("Could not import Hermes ServiceRegistry")
                return False
        
        # Register the requirements service
        success = await service_registry.register(
            service_id="telos-requirements",
            name="Telos Requirements Manager",
            version="0.1.0",
            capabilities=["requirements_management", "project_management"],
            metadata={
                "projects": len(self.projects),
                "requirements": sum(len(p.requirements) for p in self.projects.values())
            }
        )
        
        if success:
            logger.info("Registered requirements manager with Hermes")
        else:
            logger.warning("Failed to register requirements manager")
        
        return success
    
    except Exception as e:
        logger.error(f"Error registering with Hermes: {e}")
        return False
```

### Using the Registration Script

To manually register Telos with Hermes:

```bash
python -m Telos/register_with_hermes.py
```

### Registered Capabilities

Telos registers the following capabilities with Hermes:

| Capability | Description |
| ---------- | ----------- |
| `requirements_management` | Managing requirements (create, read, update, delete) |
| `project_management` | Managing projects (create, read, update, delete) |
| `requirement_validation` | Validating requirements for quality |
| `requirement_refinement` | Refining requirements with LLM assistance |
| `requirement_tracing` | Tracking relationships between requirements |
| `planning_preparation` | Preparing requirements for planning |

## Prometheus Integration

Telos integrates with Prometheus for advanced planning capabilities.

### Integration Components

The `TelosPrometheusConnector` class serves as the bridge between Telos and Prometheus:

```python
class TelosPrometheusConnector:
    """Bridge between Telos requirements and Prometheus planning."""
    
    def __init__(self, requirements_manager: RequirementsManager):
        """Initialize the connector."""
        self.requirements_manager = requirements_manager
        self.queries = []  # Store queries from Prometheus to Telos/user
        self.prometheus_available = False
        
        # Try to import Prometheus planning engine (optional dependency)
        try:
            from prometheus.core.planning_engine import PlanningEngine
            self.planning_engine = PlanningEngine()
            self.prometheus_available = True
        except ImportError:
            logger.warning("Prometheus planning engine not available. Planning features will be limited.")
            self.planning_engine = None
```

### Key Integration Methods

The connector provides these key methods:

1. **Prepare Requirements for Planning**:
   ```python
   async def prepare_requirements_for_planning(self, project_id: str) -> Dict[str, Any]:
       """Process requirements to determine planning readiness."""
   ```

2. **Create Plan**:
   ```python
   async def create_plan(self, project_id: str) -> Dict[str, Any]:
       """Create a plan for a project using Prometheus."""
   ```

3. **Request Clarification**:
   ```python
   async def request_clarification(self, project_id: str, requirement_id: str, question: str) -> Dict[str, Any]:
       """Request clarification from the user about a requirement."""
   ```

### Integration Example

```python
# Create the connector
connector = TelosPrometheusConnector(requirements_manager)

# Initialize the connector
await connector.initialize()

# Prepare requirements for planning
readiness = await connector.prepare_requirements_for_planning(project_id)

# If requirements are ready, create a plan
if readiness["status"] == "ready":
    plan_result = await connector.create_plan(project_id)
    # Use the plan result
```

## Rhetor Integration

Telos integrates with Rhetor for LLM-powered requirement analysis and refinement.

### Integration Components

Telos uses Rhetor for:
1. Requirement validation
2. Requirement refinement
3. Quality analysis

The integration is implemented in the `interactive_refine.py` module:

```python
async def refine_requirement_with_feedback(
    requirements_manager,
    project_id,
    requirement_id,
    feedback,
    auto_update=False
):
    """Refine a requirement with LLM-powered feedback."""
    try:
        # Try to import the Rhetor client
        from rhetor.client import RhetorClient
        
        # Initialize the client
        rhetor_client = await RhetorClient.create()
        
        # Get the requirement
        requirement = requirements_manager.get_requirement(project_id, requirement_id)
        if not requirement:
            return {
                "status": "error",
                "message": f"Requirement {requirement_id} not found"
            }
        
        # Prepare the prompt
        prompt = f"""
        I have the following requirement:
        
        Title: {requirement.title}
        Description: {requirement.description}
        Type: {requirement.requirement_type}
        Priority: {requirement.priority}
        
        I received this feedback about the requirement:
        {feedback}
        
        Please improve this requirement based on the feedback. Provide:
        1. An improved title if needed
        2. An improved description
        3. Any other suggested changes
        """
        
        # Get the response from Rhetor
        response = await rhetor_client.generate_text(
            prompt=prompt,
            context_id=f"requirement-{requirement_id}",
            max_tokens=1024
        )
        
        # Process the response
        # Implementation details for parsing the response
        
        # Update the requirement if auto_update is True
        if auto_update:
            # Update implementation
            pass
        
        return {
            "status": "success",
            "original": requirement.to_dict(),
            "refined": refined_requirement,
            "changes": changes
        }
        
    except ImportError:
        # Fall back to rule-based refinement if Rhetor is not available
        return {
            "status": "error",
            "message": "Rhetor is not available for LLM-powered refinement"
        }
```

### Integration Example

```python
# Refine a requirement with feedback
result = await refine_requirement_with_feedback(
    requirements_manager=requirements_manager,
    project_id="project-1",
    requirement_id="req-1",
    feedback="This requirement needs to be more specific about authentication methods",
    auto_update=False
)

# Display the refinement result
print(f"Original: {result['original']['description']}")
print(f"Refined: {result['refined']['description']}")
print("Changes:")
for change in result['changes']:
    print(f"- {change}")
```

## Hephaestus UI Integration

Telos integrates with Hephaestus through a Shadow DOM component.

### Shadow DOM Component

The Telos component is implemented as a Shadow DOM web component:

```javascript
class TelosComponent extends HTMLElement {
  constructor() {
    super();
    
    // Initialize Shadow DOM
    this.attachShadow({ mode: 'open' });
    
    // Load the template
    const template = document.getElementById('telos-template');
    this.shadowRoot.appendChild(template.content.cloneNode(true));
    
    // Initialize state
    this.state = {
      // Component state
    };
  }
  
  // Component lifecycle methods
  connectedCallback() {
    this.initializeComponent();
  }
  
  disconnectedCallback() {
    this.removeEventListeners();
  }
}

// Define the custom element
customElements.define('telos-component', TelosComponent);
```

### Integration with Hephaestus

To integrate the Telos component into Hephaestus:

1. Include the component scripts:
   ```html
   <script src="telos-component.js"></script>
   <script src="telos-service.js"></script>
   ```

2. Use the component in the Hephaestus UI:
   ```html
   <telos-component></telos-component>
   ```

3. Connect to the Tekton state management:
   ```javascript
   // Initialize Telos service
   const telosService = new TelosService();
   telosService.initialize(tektonStateManager);
   
   // Connect the component to the service
   document.querySelector('telos-component').service = telosService;
   ```

## Client Library

Telos provides a client library for programmatic integration.

### Client Initialization

```python
from telos.client import TelosClient, get_telos_client

# Create a client
client = await get_telos_client()

# Or with specific parameters
client = TelosClient(
    component_id="telos.requirements",
    hermes_url="http://localhost:8009/api"
)
```

### Client Capabilities

The client provides methods for all Telos operations:

```python
# Project operations
project = await client.create_project(name="Project Name", description="Description")
project_data = await client.get_project(project_id)

# Requirement operations
requirement = await client.create_requirement(
    project_id=project_id,
    title="Requirement Title",
    description="Requirement description",
    priority="high",
    requirement_type="functional"
)
requirements = await client.get_requirements(project_id)

# Analysis operations
analysis = await client.analyze_requirements(project_id)
refinement = await client.refine_requirement(requirement_id, feedback="Feedback")
```

### Integration Example

```python
import asyncio
from telos.client import get_telos_client

async def main():
    # Initialize the client
    client = await get_telos_client()
    
    try:
        # Create a project
        project = await client.create_project(
            name="Integration Project",
            description="Project for integration testing"
        )
        project_id = project["project_id"]
        
        # Create requirements
        req1 = await client.create_requirement(
            project_id=project_id,
            title="Authentication",
            description="User authentication system",
            priority="high"
        )
        
        req2 = await client.create_requirement(
            project_id=project_id,
            title="Authorization",
            description="User authorization system",
            priority="high"
        )
        
        # Analyze requirements
        analysis = await client.analyze_requirements(project_id)
        print(f"Analysis results: {analysis}")
    finally:
        # Close the client
        await client.close()

# Run the async function
asyncio.run(main())
```

## WebSocket Integration

Telos provides WebSocket integration for real-time updates.

### Connection Setup

```javascript
// Connect to WebSocket
const ws = new WebSocket("ws://localhost:8008/ws");

// Set up event handlers
ws.onopen = () => {
    console.log("WebSocket connection established");
    
    // Register with the server
    ws.send(JSON.stringify({
        type: "REGISTER",
        source: "client",
        target: "server",
        timestamp: Date.now(),
        payload: {
            client_id: "my-client-id"
        }
    }));
};

ws.onmessage = (event) => {
    const message = JSON.parse(event.data);
    console.log("Received message:", message);
    
    // Handle different message types
    switch (message.type) {
        case "WELCOME":
            // Handle welcome message
            break;
        case "RESPONSE":
            // Handle response to a request
            break;
        case "UPDATE":
            // Handle update notification
            break;
    }
};

ws.onerror = (error) => {
    console.error("WebSocket error:", error);
};

ws.onclose = () => {
    console.log("WebSocket connection closed");
};
```

### Subscription to Updates

```javascript
// Subscribe to project updates
function subscribeToProject(projectId) {
    ws.send(JSON.stringify({
        type: "PROJECT_SUBSCRIBE",
        source: "client",
        target: "server",
        timestamp: Date.now(),
        payload: {
            project_id: projectId
        }
    }));
}

// Request status
function requestStatus() {
    ws.send(JSON.stringify({
        type: "STATUS",
        source: "client",
        target: "server",
        timestamp: Date.now(),
        payload: {}
    }));
}
```

### Handling Updates

```javascript
function handleUpdate(update) {
    const payload = update.payload;
    
    if (payload.type === "project_update") {
        // Handle project update
        refreshProjectData(payload.project_id);
    } else if (payload.type === "requirement_update") {
        // Handle requirement update
        refreshRequirementData(payload.project_id, payload.requirement_id);
    } else if (payload.type === "trace_update") {
        // Handle trace update
        refreshTraceData(payload.project_id, payload.trace_id);
    }
}
```

## External System Integration

Telos can integrate with external systems through its API.

### API Authentication

For external system integration, API authentication should be implemented for production use.

### API Versioning

The API supports versioning for backward compatibility:

```
GET /api/v1/projects
```

### Data Export/Import

External systems can exchange data with Telos through export/import endpoints:

```python
import requests
import json

# Export data from Telos
response = requests.post(
    "http://localhost:8008/api/projects/project-id/export",
    json={"format": "json"}
)
export_data = response.json()

# Save to file
with open("telos_export.json", "w") as f:
    json.dump(export_data, f, indent=2)

# Import data to Telos
with open("external_requirements.json", "r") as f:
    import_data = json.load(f)

response = requests.post(
    "http://localhost:8008/api/projects/import",
    json={
        "data": import_data,
        "format": "json",
        "merge_strategy": "replace"
    }
)
```

### Integration with Issue Trackers

Example integration with an issue tracker:

```python
import requests

# Function to sync requirements with issues
def sync_requirements_with_issues(project_id, issue_tracker_url, api_key):
    # Get requirements from Telos
    telos_response = requests.get(
        f"http://localhost:8008/api/projects/{project_id}/requirements"
    )
    requirements = telos_response.json()["requirements"]
    
    # For each requirement, create or update an issue
    for req in requirements:
        # Check if issue exists for this requirement
        issue_id = req.get("metadata", {}).get("issue_id")
        
        if issue_id:
            # Update existing issue
            update_issue(issue_tracker_url, api_key, issue_id, req)
        else:
            # Create new issue
            new_issue_id = create_issue(issue_tracker_url, api_key, req)
            
            # Update requirement with issue ID
            requests.put(
                f"http://localhost:8008/api/projects/{project_id}/requirements/{req['requirement_id']}",
                json={
                    "metadata": {
                        "issue_id": new_issue_id
                    }
                }
            )
```

## Single Port Architecture

Telos follows the Tekton Single Port Architecture pattern for simplified integration.

### Port Configuration

Telos uses a single port (8008) for all communications:

```
TELOS_PORT=8008
```

### URL Structure

All Telos endpoints follow a consistent structure:

- **HTTP API**: `http://localhost:8008/api/*`
- **WebSocket**: `ws://localhost:8008/ws`
- **Events**: `http://localhost:8008/events`

### Containerization

For containerized deployments, expose only the single port:

```dockerfile
EXPOSE 8008
```

```yaml
# docker-compose.yml
services:
  telos:
    build: ./Telos
    ports:
      - "8008:8008"
    environment:
      - TELOS_PORT=8008
      - TELOS_STORAGE_DIR=/data/requirements
    volumes:
      - telos_data:/data/requirements
```

## Data Models

Understanding Telos data models is essential for integration.

### Project Model

```python
# Project structure
project = {
    "project_id": "project-id",
    "name": "Project Name",
    "description": "Project description",
    "created_at": timestamp,
    "updated_at": timestamp,
    "metadata": {
        "key1": "value1",
        "key2": "value2"
    },
    "requirements": {
        "req-id-1": {
            "requirement_id": "req-id-1",
            "title": "Requirement 1",
            # Other requirement attributes
        },
        "req-id-2": {
            "requirement_id": "req-id-2",
            "title": "Requirement 2",
            # Other requirement attributes
        }
    }
}
```

### Requirement Model

```python
# Requirement structure
requirement = {
    "requirement_id": "req-id",
    "title": "Requirement Title",
    "description": "Requirement description",
    "requirement_type": "functional",
    "priority": "high",
    "status": "new",
    "created_by": "user-id",
    "created_at": timestamp,
    "updated_at": timestamp,
    "tags": ["tag1", "tag2"],
    "parent_id": "parent-req-id",
    "dependencies": ["dep-req-id-1", "dep-req-id-2"],
    "metadata": {
        "key1": "value1",
        "key2": "value2"
    },
    "history": [
        {
            "timestamp": timestamp,
            "action": "created",
            "description": "Requirement created"
        },
        {
            "timestamp": timestamp,
            "action": "updated",
            "description": "Updated attributes: title, priority"
        }
    ]
}
```

### Trace Model

```python
# Trace structure
trace = {
    "trace_id": "trace-id",
    "source_id": "source-req-id",
    "target_id": "target-req-id",
    "trace_type": "depends_on",
    "description": "Description of the trace",
    "created_at": timestamp,
    "updated_at": timestamp,
    "metadata": {
        "key1": "value1",
        "key2": "value2"
    }
}
```

## Security Considerations

Consider these security aspects when integrating with Telos:

1. **Authentication and Authorization**:
   - Implement API authentication for external integrations
   - Use proper authorization checks for sensitive operations

2. **Data Validation**:
   - Validate all data sent to Telos APIs
   - Use proper content sanitization for user-generated content

3. **Network Security**:
   - Use HTTPS for all API communications in production
   - Secure WebSocket connections with proper authentication

4. **Error Handling**:
   - Implement proper error handling in integrations
   - Avoid exposing sensitive information in error messages

5. **Resource Protection**:
   - Implement rate limiting for API calls
   - Use timeouts for long-running operations

6. **Audit Logging**:
   - Log all integration activities for auditing
   - Monitor for suspicious patterns in API usage
# Telos API Reference

This document provides a comprehensive reference for the Telos API endpoints following the Single Port Architecture pattern.

## Base URL

All API endpoints are accessible through port 8008:

```
http://localhost:8008
```

## Path Structure

The API follows the Single Port Architecture pattern with these path prefixes:

- `/api/*` - RESTful API endpoints
- `/ws` - WebSocket endpoint for real-time updates
- `/events` - Server-sent events (future implementation)

## Authentication

Authentication is not currently implemented. All endpoints are accessible without authentication.

## API Endpoints

### Root Endpoints

#### GET /

Get basic information about the Telos API.

**Response**:
```json
{
  "name": "Telos Requirements Manager",
  "version": "0.1.0",
  "status": "running",
  "endpoints": [
    "/api/projects", "/api/requirements", "/api/traces", 
    "/api/validation", "/api/export", "/api/import", "/ws", "/events"
  ],
  "prometheus_available": true,
  "project_count": 3
}
```

#### GET /health

Check the health status of the Telos API.

**Response**:
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "project_count": 3,
  "storage_dir": "/path/to/storage",
  "prometheus_available": true
}
```

### Project Management

#### GET /api/projects

List all projects.

**Response**:
```json
{
  "projects": [
    {
      "project_id": "project-123",
      "name": "My Project",
      "description": "Project description",
      "created_at": 1650000000,
      "updated_at": 1650001000,
      "requirement_count": 5
    },
    // More projects...
  ],
  "count": 2
}
```

#### POST /api/projects

Create a new project.

**Request**:
```json
{
  "name": "New Project",
  "description": "Project description",
  "metadata": {
    "category": "Development",
    "priority": "High"
  }
}
```

**Response**:
```json
{
  "project_id": "project-456",
  "name": "New Project",
  "description": "Project description",
  "created_at": 1650002000
}
```

#### GET /api/projects/{project_id}

Get a specific project with its requirements.

**Response**:
```json
{
  "project_id": "project-123",
  "name": "My Project",
  "description": "Project description",
  "created_at": 1650000000,
  "updated_at": 1650001000,
  "requirements": {
    "req-1": {
      "requirement_id": "req-1",
      "title": "User Authentication",
      "description": "The system shall authenticate users",
      // More requirement attributes...
    },
    // More requirements...
  },
  "hierarchy": {
    // Hierarchical structure of requirements
  }
}
```

#### PUT /api/projects/{project_id}

Update a project.

**Request**:
```json
{
  "name": "Updated Project Name",
  "description": "Updated description",
  "metadata": {
    "status": "Active"
  }
}
```

**Response**:
```json
{
  "project_id": "project-123",
  "updated": {
    "name": "Updated Project Name",
    "description": "Updated description",
    "metadata": {
      "category": "Development",
      "priority": "High",
      "status": "Active"
    }
  },
  "updated_at": 1650003000
}
```

#### DELETE /api/projects/{project_id}

Delete a project.

**Response**:
```json
{
  "success": true,
  "project_id": "project-123"
}
```

### Requirement Management

#### POST /api/projects/{project_id}/requirements

Create a new requirement in a project.

**Request**:
```json
{
  "title": "User Authentication",
  "description": "The system shall authenticate users with username and password",
  "requirement_type": "functional",
  "priority": "high",
  "status": "new",
  "tags": ["security", "user"],
  "parent_id": null,
  "dependencies": []
}
```

**Response**:
```json
{
  "project_id": "project-123",
  "requirement_id": "req-1",
  "title": "User Authentication",
  "created_at": 1650004000
}
```

#### GET /api/projects/{project_id}/requirements

List requirements for a project with optional filtering.

**Query Parameters**:
- `status`: Filter by status
- `requirement_type`: Filter by type
- `priority`: Filter by priority
- `tag`: Filter by tag

**Response**:
```json
{
  "requirements": [
    {
      "requirement_id": "req-1",
      "title": "User Authentication",
      "description": "The system shall authenticate users",
      "requirement_type": "functional",
      "priority": "high",
      "status": "new",
      "tags": ["security", "user"],
      "created_at": 1650004000,
      "updated_at": 1650004000
    },
    // More requirements...
  ],
  "count": 5
}
```

#### GET /api/projects/{project_id}/requirements/{requirement_id}

Get a specific requirement.

**Response**:
```json
{
  "requirement_id": "req-1",
  "title": "User Authentication",
  "description": "The system shall authenticate users",
  "requirement_type": "functional",
  "priority": "high",
  "status": "new",
  "tags": ["security", "user"],
  "parent_id": null,
  "dependencies": [],
  "created_at": 1650004000,
  "updated_at": 1650004000,
  "metadata": {}
}
```

#### PUT /api/projects/{project_id}/requirements/{requirement_id}

Update a requirement.

**Request**:
```json
{
  "title": "Updated Title",
  "description": "Updated description",
  "priority": "medium",
  "status": "in_progress"
}
```

**Response**:
```json
{
  "requirement_id": "req-1",
  "updated": ["title", "description", "priority", "status"],
  "updated_at": 1650005000
}
```

#### DELETE /api/projects/{project_id}/requirements/{requirement_id}

Delete a requirement.

**Response**:
```json
{
  "success": true,
  "project_id": "project-123",
  "requirement_id": "req-1"
}
```

### Requirement Refinement

#### POST /api/projects/{project_id}/requirements/{requirement_id}/refine

Refine a requirement with feedback.

**Request**:
```json
{
  "feedback": "Add more detail about authentication methods",
  "auto_update": true
}
```

**Response**:
```json
{
  "requirement_id": "req-1",
  "title": "User Authentication",
  "description": "The system shall authenticate users with username/password and optional two-factor authentication",
  "suggestions": [
    "Consider adding details about password requirements",
    "Add information about account lockout policies"
  ],
  "score": 0.85
}
```

### Requirement Validation

#### POST /api/projects/{project_id}/validate

Validate a project's requirements against provided criteria.

**Request**:
```json
{
  "criteria": {
    "check_completeness": true,
    "check_clarity": true,
    "check_verifiability": true
  }
}
```

**Response**:
```json
{
  "project_id": "project-123",
  "validation_date": "2025-04-26T14:30:00.000Z",
  "results": [
    {
      "requirement_id": "req-1",
      "title": "User Authentication",
      "issues": [
        {
          "type": "verifiability",
          "message": "Requirement may not be easily verifiable"
        }
      ],
      "passed": false
    },
    // More requirement validation results...
  ],
  "summary": {
    "total_requirements": 5,
    "passed": 3,
    "failed": 2,
    "pass_percentage": 60
  },
  "criteria": {
    "check_completeness": true,
    "check_clarity": true,
    "check_verifiability": true
  }
}
```

### Requirement Tracing

#### GET /api/projects/{project_id}/traces

List all requirement traces for a project.

**Response**:
```json
{
  "traces": [
    {
      "trace_id": "trace_1650006000",
      "source_id": "req-1",
      "target_id": "req-2",
      "trace_type": "depends-on",
      "description": "Authentication is required before authorization",
      "created_at": 1650006000
    },
    // More traces...
  ],
  "count": 3
}
```

#### POST /api/projects/{project_id}/traces

Create a new trace between requirements.

**Request**:
```json
{
  "source_id": "req-1",
  "target_id": "req-3",
  "trace_type": "implements",
  "description": "Authentication implements security requirements"
}
```

**Response**:
```json
{
  "trace_id": "trace_1650007000",
  "source_id": "req-1",
  "target_id": "req-3"
}
```

#### GET /api/projects/{project_id}/traces/{trace_id}

Get a specific trace.

**Response**:
```json
{
  "trace_id": "trace_1650006000",
  "source_id": "req-1",
  "target_id": "req-2",
  "trace_type": "depends-on",
  "description": "Authentication is required before authorization",
  "created_at": 1650006000,
  "metadata": {}
}
```

#### PUT /api/projects/{project_id}/traces/{trace_id}

Update a trace.

**Request**:
```json
{
  "trace_type": "precedes",
  "description": "Updated description"
}
```

**Response**:
```json
{
  "trace_id": "trace_1650006000",
  "updated": {
    "trace_type": "precedes",
    "description": "Updated description"
  },
  "updated_at": 1650008000
}
```

#### DELETE /api/projects/{project_id}/traces/{trace_id}

Delete a trace.

**Response**:
```json
{
  "success": true,
  "trace_id": "trace_1650006000"
}
```

### Project Export/Import

#### POST /api/projects/{project_id}/export

Export a project in the specified format.

**Request**:
```json
{
  "format": "json",
  "sections": ["metadata", "requirements", "traces"]
}
```

**Response**:
```json
{
  // Full project data
}
```

#### POST /api/projects/import

Import a project from external data.

**Request**:
```json
{
  "data": {
    // Project data to import
  },
  "format": "json",
  "merge_strategy": "replace"
}
```

**Response**:
```json
{
  "project_id": "project-789",
  "name": "Imported Project",
  "imported_requirements": 10
}
```

### Planning Integration

#### POST /api/projects/{project_id}/analyze

Analyze requirements for planning readiness.

**Response**:
```json
{
  "project_id": "project-123",
  "analysis": {
    "status": "ready",
    "total_requirements": 10,
    "requirements_ready": 8,
    "missing_details": [
      {
        "requirement_id": "req-5",
        "missing": ["acceptance_criteria", "priority"]
      },
      {
        "requirement_id": "req-7",
        "missing": ["description_details"]
      }
    ],
    "suggestions": [
      "Add acceptance criteria to requirement 'User Logout'",
      "Provide more detailed description for 'Data Export'"
    ]
  }
}
```

#### POST /api/projects/{project_id}/plan

Create a plan for the project using Prometheus.

**Response**:
```json
{
  "project_id": "project-123",
  "plan": {
    "plan_id": "plan-456",
    "name": "Implementation Plan for Project 123",
    "phases": [
      {
        "name": "Phase 1: Authentication and User Management",
        "tasks": [
          {
            "task_id": "task-1",
            "name": "Implement User Authentication",
            "requirement_ids": ["req-1"],
            "estimated_effort": "3d",
            "dependencies": []
          },
          // More tasks...
        ]
      },
      // More phases...
    ],
    "timeline": {
      "start_date": "2025-05-01",
      "end_date": "2025-06-15",
      "milestones": [
        {
          "name": "Authentication Complete",
          "date": "2025-05-15",
          "tasks": ["task-1", "task-2"]
        },
        // More milestones...
      ]
    },
    "resource_allocation": {
      // Resource allocation details
    }
  }
}
```

## WebSocket API

### Endpoint

```
ws://localhost:8008/ws
```

### Message Format

All messages follow this general format:

```json
{
  "type": "MESSAGE_TYPE",
  "source": "client",
  "target": "server",
  "timestamp": 1650009000,
  "payload": {
    // Message-specific payload
  }
}
```

### Message Types

#### REGISTER

Register a client for WebSocket communication.

**Client Message**:
```json
{
  "type": "REGISTER",
  "source": "client",
  "target": "server",
  "timestamp": 1650009000,
  "payload": {}
}
```

**Server Response**:
```json
{
  "type": "RESPONSE",
  "source": "SERVER",
  "target": "client",
  "timestamp": 1650009001,
  "payload": {
    "status": "registered",
    "client_id": "client_1650009000",
    "message": "Client registered successfully"
  }
}
```

#### STATUS

Get the current status of the Telos service.

**Client Message**:
```json
{
  "type": "STATUS",
  "source": "client",
  "target": "server",
  "timestamp": 1650009100,
  "payload": {}
}
```

**Server Response**:
```json
{
  "type": "RESPONSE",
  "source": "SERVER",
  "target": "client",
  "timestamp": 1650009101,
  "payload": {
    "status": "ok",
    "service": "telos",
    "version": "0.1.0",
    "project_count": 5,
    "prometheus_available": true
  }
}
```

#### PROJECT_SUBSCRIBE

Subscribe to real-time updates for a project.

**Client Message**:
```json
{
  "type": "PROJECT_SUBSCRIBE",
  "source": "client",
  "target": "server",
  "timestamp": 1650009200,
  "payload": {
    "project_id": "project-123"
  }
}
```

**Server Response**:
```json
{
  "type": "RESPONSE",
  "source": "SERVER",
  "target": "client",
  "timestamp": 1650009201,
  "payload": {
    "status": "subscribed",
    "project_id": "project-123",
    "message": "Subscribed to updates for project project-123"
  }
}
```

### Real-time Update Messages

When changes occur to subscribed resources, the server sends update messages:

```json
{
  "type": "UPDATE",
  "source": "SERVER",
  "target": "client",
  "timestamp": 1650009300,
  "payload": {
    "project_id": "project-123",
    "resource_type": "requirement",
    "resource_id": "req-1",
    "action": "updated",
    "data": {
      // Updated resource data
    }
  }
}
```

## Error Handling

All API endpoints return appropriate HTTP status codes:

- `200 OK`: Successful operation
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request parameters
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

Error responses include a detail message:

```json
{
  "detail": "Project project-123 not found"
}
```

## Integration Examples

### JavaScript API Client

```javascript
// Example of using the Telos API with fetch
const BASE_URL = 'http://localhost:8008';

// Get all projects
async function getProjects() {
  const response = await fetch(`${BASE_URL}/api/projects`);
  return response.json();
}

// Create a new requirement
async function createRequirement(projectId, requirementData) {
  const response = await fetch(`${BASE_URL}/api/projects/${projectId}/requirements`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(requirementData)
  });
  return response.json();
}

// Connect to WebSocket for real-time updates
function connectWebSocket(onMessage) {
  const ws = new WebSocket(`ws://localhost:8008/ws`);
  
  ws.onopen = () => {
    console.log('Connected to Telos WebSocket');
    // Register client
    ws.send(JSON.stringify({
      type: 'REGISTER',
      source: 'client',
      target: 'server',
      timestamp: Date.now(),
      payload: {}
    }));
  };
  
  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    onMessage(data);
  };
  
  ws.onerror = (error) => {
    console.error('WebSocket error:', error);
  };
  
  ws.onclose = () => {
    console.log('Disconnected from WebSocket');
  };
  
  return ws;
}
```

### Python API Client

```python
import requests
import json
import websocket
import threading
import time

class TelosClient:
    """Client for interacting with the Telos API."""
    
    def __init__(self, base_url="http://localhost:8008"):
        """Initialize the client with the base URL."""
        self.base_url = base_url
        self.ws = None
        self.ws_thread = None
        
    def get_projects(self):
        """Get all projects."""
        response = requests.get(f"{self.base_url}/api/projects")
        return response.json()
    
    def create_project(self, project_data):
        """Create a new project."""
        response = requests.post(
            f"{self.base_url}/api/projects",
            json=project_data
        )
        return response.json()
    
    def get_project(self, project_id):
        """Get a specific project with requirements."""
        response = requests.get(f"{self.base_url}/api/projects/{project_id}")
        return response.json()
    
    def create_requirement(self, project_id, requirement_data):
        """Create a new requirement."""
        response = requests.post(
            f"{self.base_url}/api/projects/{project_id}/requirements",
            json=requirement_data
        )
        return response.json()
    
    def connect_websocket(self, on_message=None):
        """Connect to the WebSocket for real-time updates."""
        ws_url = f"ws://localhost:8008/ws"
        
        def on_open(ws):
            print("Connected to WebSocket")
            # Register client
            ws.send(json.dumps({
                "type": "REGISTER",
                "source": "client",
                "target": "server",
                "timestamp": int(time.time() * 1000),
                "payload": {}
            }))
        
        def on_message_internal(ws, message):
            data = json.loads(message)
            if on_message:
                on_message(data)
            else:
                print(f"Received: {data}")
        
        def on_error(ws, error):
            print(f"WebSocket error: {error}")
        
        def on_close(ws, close_status_code, close_msg):
            print("Disconnected from WebSocket")
        
        def run_websocket():
            self.ws = websocket.WebSocketApp(
                ws_url,
                on_open=on_open,
                on_message=on_message_internal,
                on_error=on_error,
                on_close=on_close
            )
            self.ws.run_forever()
        
        self.ws_thread = threading.Thread(target=run_websocket)
        self.ws_thread.daemon = True
        self.ws_thread.start()
    
    def subscribe_to_project(self, project_id):
        """Subscribe to real-time updates for a project."""
        if not self.ws:
            raise RuntimeError("WebSocket not connected")
            
        self.ws.send(json.dumps({
            "type": "PROJECT_SUBSCRIBE",
            "source": "client",
            "target": "server",
            "timestamp": int(time.time() * 1000),
            "payload": {
                "project_id": project_id
            }
        }))
    
    def close(self):
        """Close the WebSocket connection."""
        if self.ws:
            self.ws.close()
```

## Prometheus Integration

Telos integrates with Prometheus for planning capabilities through these endpoints:

- `POST /api/projects/{project_id}/analyze`: Analyze requirements for planning readiness
- `POST /api/projects/{project_id}/plan`: Create a plan based on requirements

This integration enables:

1. Analysis of requirements quality before planning
2. Generation of implementation plans from requirements
3. Task breakdown with effort estimation
4. Timeline and milestone creation
5. Resource allocation suggestions

## LLM Integration

Telos integrates with Rhetor for LLM-powered requirement analysis:

1. Quality assessment of requirements
2. Improvement suggestions
3. Clarity and completeness evaluation
4. Interactive requirement refinement

This integration is implemented through the RequirementAnalyzer class, which uses Rhetor's LLM client.

## Websocket Real-time Updates

The WebSocket endpoint (`/ws`) provides real-time updates for:

1. Requirement changes
2. Trace updates
3. Project modifications
4. Validation results

Clients can subscribe to specific projects to receive real-time updates.

## Rate Limiting

There are currently no rate limits on the API endpoints. However, excessive usage may impact performance.
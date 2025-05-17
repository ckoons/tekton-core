# Metis Integration Guide

This document provides guidance on integrating Metis with other Tekton components and external systems.

## Integration with Tekton Components

Metis is designed to work seamlessly with other Tekton components, especially Telos (requirements management) and Prometheus (planning system). This section outlines how to integrate Metis with these components.

## Integration Patterns

### Hermes Integration

Metis integrates with Hermes for service registration and discovery. This allows other Tekton components to discover and communicate with Metis.

#### Service Registration

At startup, Metis registers itself with Hermes:

```python
# Register with Hermes
success = await hermes_client.register()
if success:
    # Start heartbeat task
    asyncio.create_task(hermes_client.heartbeat_task())
```

#### Service Discovery

Metis discovers other components through Hermes:

```python
# Discover Telos service
telos_service = await hermes_client.get_service("Telos")
if telos_service:
    telos_url = f"{telos_service['protocol']}://{telos_service['host']}:{telos_service['port']}"
```

#### Capability Announcement

Metis announces its capabilities to Hermes:

```python
# Announce capabilities
capabilities = [
    "task_management",
    "dependency_management",
    "task_tracking",
    "websocket_updates"
]
```

#### Configuration

- `HERMES_PORT`: Port for the Hermes service (default: 8001)
- Service name: "Metis"
- Capabilities: ["task_management", "dependency_management", "task_tracking", "websocket_updates"]

### Telos Integration

Metis integrates with Telos to import requirements as tasks and to maintain links between tasks and requirements.

#### Requirement Import

Metis can import requirements from Telos as tasks:

```python
# Import requirement as task
requirement = await telos_client.get_requirement(requirement_id)
if requirement:
    task_data = {
        "title": requirement.get("title", "Untitled Requirement"),
        "description": requirement.get("description", ""),
        "status": TaskStatus.PENDING.value,
        "priority": Priority.MEDIUM.value,
        "tags": ["telos", "requirement", requirement.get("type", "unknown")]
    }
    task = await task_manager.create_task(task_data)
```

#### Requirement References

Metis maintains references to requirements in Telos:

```python
# Add requirement reference to task
req_ref = await telos_client.create_requirement_reference(requirement_id)
if req_ref:
    await task_manager.add_requirement_ref(task_id, req_ref.dict())
```

#### API Endpoints

- `GET /api/v1/telos/requirements`: Search for requirements in Telos
- `POST /api/v1/telos/requirements/{requirement_id}/import`: Import a requirement as a task
- `POST /api/v1/tasks/{task_id}/telos/requirements/{requirement_id}`: Add a reference to a requirement

#### Configuration

- `TELOS_PORT`: Port for the Telos service (default: 8008)

### Prometheus Integration

Metis provides task information to Prometheus for planning and scheduling.

#### Task Information

Prometheus can query Metis for tasks and their dependencies:

```python
# Get tasks for planning
tasks = await metis_client.get_tasks(status="pending")
```

#### Task Updates

Prometheus can update task status based on planning decisions:

```python
# Update task status
await metis_client.update_task(task_id, {"status": "in_progress"})
```

#### Dependency Management

Prometheus can add dependencies between tasks:

```python
# Add dependency between tasks
await metis_client.create_dependency({
    "source_task_id": task1_id,
    "target_task_id": task2_id,
    "dependency_type": "blocks"
})
```

#### Configuration

- `PROMETHEUS_PORT`: Port for the Prometheus service (default: 8006)

## Client Integration

### Python Client

Here's an example of how to integrate with Metis from a Python client:

```python
import aiohttp
import asyncio
import json

class MetisClient:
    def __init__(self, base_url="http://localhost:8011"):
        self.base_url = base_url
        self._session = None
    
    async def _get_session(self):
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session
    
    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()
    
    async def list_tasks(self, **filters):
        session = await self._get_session()
        async with session.get(f"{self.base_url}/api/v1/tasks", params=filters) as response:
            return await response.json()
    
    async def get_task(self, task_id):
        session = await self._get_session()
        async with session.get(f"{self.base_url}/api/v1/tasks/{task_id}") as response:
            return await response.json()
    
    async def create_task(self, task_data):
        session = await self._get_session()
        async with session.post(f"{self.base_url}/api/v1/tasks", json=task_data) as response:
            return await response.json()
    
    async def update_task(self, task_id, task_updates):
        session = await self._get_session()
        async with session.put(f"{self.base_url}/api/v1/tasks/{task_id}", json=task_updates) as response:
            return await response.json()
    
    async def delete_task(self, task_id):
        session = await self._get_session()
        async with session.delete(f"{self.base_url}/api/v1/tasks/{task_id}") as response:
            return await response.json()
    
    # WebSocket connection for real-time updates
    async def connect_websocket(self, event_handler, subscribe_to=None):
        if subscribe_to is None:
            subscribe_to = ["task_created", "task_updated", "task_deleted"]
        
        session = await self._get_session()
        async with session.ws_connect(f"{self.base_url}/ws") as ws:
            # Register with the server
            await ws.send_json({
                "client_id": f"client-{id(self)}",
                "subscribe_to": subscribe_to
            })
            
            # Wait for registration confirmation
            registration = await ws.receive_json()
            if registration["type"] != "registration_success":
                raise ValueError(f"Failed to register with WebSocket: {registration}")
            
            # Handle messages
            try:
                async for msg in ws:
                    if msg.type == aiohttp.WSMsgType.TEXT:
                        data = json.loads(msg.data)
                        await event_handler(data["type"], data["data"])
                    elif msg.type == aiohttp.WSMsgType.ERROR:
                        break
            finally:
                if not ws.closed:
                    await ws.close()

# Example usage
async def example():
    client = MetisClient()
    try:
        # List tasks
        tasks = await client.list_tasks(status="pending")
        print(f"Found {tasks['total']} pending tasks")
        
        # Create a task
        new_task = await client.create_task({
            "title": "Example Task",
            "description": "This is an example task",
            "status": "pending",
            "priority": "medium"
        })
        print(f"Created task: {new_task['id']}")
        
        # Update a task
        updated_task = await client.update_task(new_task["id"], {
            "status": "in_progress",
            "priority": "high"
        })
        print(f"Updated task: {updated_task['id']}")
        
        # Example WebSocket event handler
        async def handle_event(event_type, data):
            print(f"Received event: {event_type}")
            print(f"Data: {data}")
        
        # Connect to WebSocket for real-time updates
        # Uncomment to run WebSocket connection
        # await client.connect_websocket(handle_event)
    finally:
        await client.close()

# Run the example
# asyncio.run(example())
```

### JavaScript Client

Here's an example of how to integrate with Metis from a JavaScript client:

```javascript
class MetisClient {
  constructor(baseUrl = 'http://localhost:8011') {
    this.baseUrl = baseUrl;
  }
  
  async listTasks(filters = {}) {
    const queryParams = new URLSearchParams(filters);
    const response = await fetch(`${this.baseUrl}/api/v1/tasks?${queryParams}`);
    return response.json();
  }
  
  async getTask(taskId) {
    const response = await fetch(`${this.baseUrl}/api/v1/tasks/${taskId}`);
    return response.json();
  }
  
  async createTask(taskData) {
    const response = await fetch(`${this.baseUrl}/api/v1/tasks`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(taskData)
    });
    return response.json();
  }
  
  async updateTask(taskId, taskUpdates) {
    const response = await fetch(`${this.baseUrl}/api/v1/tasks/${taskId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(taskUpdates)
    });
    return response.json();
  }
  
  async deleteTask(taskId) {
    const response = await fetch(`${this.baseUrl}/api/v1/tasks/${taskId}`, {
      method: 'DELETE'
    });
    return response.json();
  }
  
  // WebSocket connection for real-time updates
  connectWebSocket(eventHandler, subscribeTo = ['task_created', 'task_updated', 'task_deleted']) {
    const ws = new WebSocket(`ws://${this.baseUrl.replace('http://', '')}/ws`);
    
    ws.onopen = () => {
      // Register with the server
      ws.send(JSON.stringify({
        client_id: `client-${Date.now()}`,
        subscribe_to: subscribeTo
      }));
    };
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      eventHandler(data.type, data.data);
    };
    
    // Handle ping/pong for keep-alive
    setInterval(() => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ type: 'ping', data: {} }));
      }
    }, 30000);
    
    return ws;
  }
}

// Example usage
async function example() {
  const client = new MetisClient();
  
  // List tasks
  const tasks = await client.listTasks({ status: 'pending' });
  console.log(`Found ${tasks.total} pending tasks`);
  
  // Create a task
  const newTask = await client.createTask({
    title: 'Example Task',
    description: 'This is an example task',
    status: 'pending',
    priority: 'medium'
  });
  console.log(`Created task: ${newTask.id}`);
  
  // Update a task
  const updatedTask = await client.updateTask(newTask.id, {
    status: 'in_progress',
    priority: 'high'
  });
  console.log(`Updated task: ${updatedTask.id}`);
  
  // Example WebSocket event handler
  function handleEvent(eventType, data) {
    console.log(`Received event: ${eventType}`);
    console.log(`Data:`, data);
  }
  
  // Connect to WebSocket for real-time updates
  // Uncomment to run WebSocket connection
  // const ws = client.connectWebSocket(handleEvent);
}

// Run the example
// example();
```

## Data Model Integration

When integrating with Metis, it's important to understand the core data models:

### Task

The central entity in Metis is the Task. A Task represents a discrete unit of work and has the following key attributes:

- `id`: Unique identifier
- `title`: Short title of the task
- `description`: Detailed description
- `status`: Current status (pending, in_progress, review, done, blocked, cancelled)
- `priority`: Priority level (high, medium, low)
- `dependencies`: List of tasks this task depends on
- `subtasks`: List of smaller sub-units of work
- `requirement_refs`: References to requirements in Telos

### Dependencies

Dependencies represent relationships between tasks. A Dependency has:

- `source_task_id`: ID of the source task
- `target_task_id`: ID of the target task
- `dependency_type`: Type of dependency (blocks, depends_on, related_to)

### Complexity

Complexity represents the difficulty level of a task. A ComplexityScore has:

- `factors`: List of factors contributing to complexity
- `overall_score`: Calculated complexity score
- `level`: Complexity level (trivial, simple, moderate, complex, very_complex)

## Domain Workflow Integration

### Task Lifecycle

Tasks in Metis follow a specific lifecycle:

1. **Creation**: Task is created with initial attributes
2. **Planning**: Dependencies and complexity are defined
3. **Assignment**: Task is assigned to a user
4. **Execution**: Status transitions from "pending" to "in_progress"
5. **Review**: Status transitions to "review" when ready for validation
6. **Completion**: Status transitions to "done" when completed

Components integrating with Metis should respect this lifecycle and use the appropriate status transitions.

### Dependency Resolution

When planning work, it's important to consider task dependencies:

1. **Identify Dependencies**: Determine what tasks depend on others
2. **Resolve Cycles**: Ensure there are no circular dependencies
3. **Critical Path**: Calculate the critical path through dependencies
4. **Parallel Work**: Identify tasks that can be worked on in parallel

The DependencyResolver in Metis provides utilities for these operations.

## Integration Best Practices

1. **Use WebSockets for Real-time Updates**
   - Connect to the WebSocket endpoint to receive real-time updates
   - Subscribe to relevant event types
   - Handle reconnections and maintain heartbeats

2. **Manage Dependencies Carefully**
   - Avoid creating circular dependencies
   - Use appropriate dependency types
   - Remove dependencies when they're no longer relevant

3. **Link Tasks to Requirements**
   - When a task implements a requirement, create a requirement reference
   - Use appropriate relationship types
   - Keep requirement references up to date

4. **Update Task Status Accurately**
   - Follow the allowed status transitions
   - Update status when work begins or completes
   - Set blocked status when dependencies are blocking progress

5. **Use Subtasks for Complex Work**
   - Break down complex tasks into subtasks
   - Update subtask status independently
   - Track progress at the task level based on subtask completion

6. **Handle Service Unavailability**
   - Implement retry logic for API calls
   - Cache task information for offline usage
   - Reprocess failed operations when services recover

7. **Bulk Operations for Performance**
   - Use bulk create/update operations for multiple tasks
   - Batch dependency updates
   - Rate-limit WebSocket subscriptions

## Tekton Component Integration Examples

### Integrating with Telos

```python
# Import requirements from Telos as tasks
from metis.core.telos_integration import telos_client

async def import_requirements_as_tasks():
    # Search for requirements in Telos
    requirements, total = await telos_client.search_requirements(
        status="approved",
        category="core"
    )
    
    # Import each requirement as a task
    imported_tasks = []
    for req in requirements:
        task = await task_manager.import_requirement_as_task(req["id"])
        if task:
            imported_tasks.append(task)
    
    return imported_tasks
```

### Integrating with Prometheus

```python
# Provide task information to Prometheus for planning
from metis.core.task_manager import task_manager

async def provide_tasks_for_planning():
    # Get pending tasks
    tasks, total = await task_manager.list_tasks(status="pending")
    
    # Get dependencies for these tasks
    dependencies = []
    for task in tasks:
        task_dependencies = await task_manager.list_dependencies(task_id=task.id)
        dependencies.extend(task_dependencies)
    
    # Calculate critical path
    from metis.core.dependency import DependencyResolver
    critical_path = DependencyResolver.get_critical_path(tasks)
    
    return {
        "tasks": tasks,
        "dependencies": dependencies,
        "critical_path": critical_path
    }
```

### Integrating with Hermes

```python
# Register with Hermes and discover other services
from metis.utils.hermes_helper import hermes_client

async def setup_hermes_integration():
    # Register with Hermes
    success = await hermes_client.register()
    if not success:
        raise RuntimeError("Failed to register with Hermes")
    
    # Discover other services
    telos_service = await hermes_client.get_service("Telos")
    prometheus_service = await hermes_client.get_service("Prometheus")
    
    # Update service URLs
    if telos_service:
        telos_url = f"{telos_service['protocol']}://{telos_service['host']}:{telos_service['port']}"
        # Update Telos client configuration
    
    if prometheus_service:
        prometheus_url = f"{prometheus_service['protocol']}://{prometheus_service['host']}:{prometheus_service['port']}"
        # Update Prometheus client configuration
    
    # Start heartbeat task
    import asyncio
    asyncio.create_task(hermes_client.heartbeat_task())
```

## Troubleshooting

### Common Issues

1. **Connection Refused**
   - Ensure Metis is running
   - Check that the port is correct
   - Verify network connectivity

2. **Authentication Errors**
   - Ensure authentication tokens are valid
   - Check permissions for the requested operation

3. **Invalid Task Status Transitions**
   - Refer to the allowed transitions in the data model
   - Ensure the current status allows the requested transition

4. **Circular Dependencies**
   - Check for cycles in dependency relationships
   - Resolve by removing or rearranging dependencies

5. **Service Discovery Failures**
   - Ensure Hermes is running
   - Check that Metis is properly registered with Hermes
   - Verify service names and capabilities

### Debugging

1. **Enable Detailed Logging**
   - Set the log level to DEBUG for more detailed logs
   - Check logs for error messages

2. **Use Health Endpoint**
   - Check the health endpoint to verify service status
   - Verify connectivity with dependent services

3. **Test API Endpoints Directly**
   - Use tools like curl or Postman to test API endpoints
   - Verify request and response formats

4. **Monitor WebSocket Connection**
   - Use browser developer tools to monitor WebSocket traffic
   - Check for connection drops or errors

5. **Check Hermes Registration**
   - Verify that Metis is registered with Hermes
   - Check that Metis is announcing the correct capabilities

## Additional Integration Patterns

### Event-Driven Integration

Metis supports event-driven integration through its WebSocket interface. Components can subscribe to events and react to changes in real-time.

```javascript
// Example: React to task status changes
const ws = new WebSocket("ws://localhost:8011/ws");

ws.onopen = () => {
  ws.send(JSON.stringify({
    client_id: "component_x",
    subscribe_to: ["task_updated"]
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.type === "task_updated") {
    const task = data.data;
    if (task.status === "done") {
      // Trigger follow-up action
      notifyTaskCompletion(task);
    }
  }
};
```

### Microservice Communication

Metis follows the Tekton microservice communication patterns, including:

1. **Direct API Communication**: Synchronous RESTful API calls
2. **Event-Based Communication**: Asynchronous events via WebSockets
3. **Service Discovery**: Hermes-based service registration and discovery

```python
# Example: Discover and communicate with Metis
async def communicate_with_metis():
    # Discover Metis through Hermes
    metis_service = await hermes_client.get_service("Metis")
    if metis_service:
        metis_url = f"{metis_service['protocol']}://{metis_service['host']}:{metis_service['port']}"
        
        # Create a client
        metis_client = MetisClient(base_url=metis_url)
        
        # Communicate with Metis
        tasks = await metis_client.list_tasks(status="pending")
        return tasks
    else:
        raise ServiceNotFoundError("Metis service not found")
```

### Integration with External Systems

Metis can be integrated with external systems using its REST API:

1. **Issue Tracking Systems**: Map tasks to issues in systems like Jira or GitHub Issues
2. **CI/CD Pipelines**: Update task status based on build/deployment results
3. **Project Management Tools**: Sync tasks with external project management tools

```python
# Example: Sync with external issue tracker
async def sync_with_issue_tracker():
    # Get tasks from Metis
    metis_tasks = await metis_client.list_tasks(updated_since=last_sync_time)
    
    # For each task, update the corresponding issue
    for task in metis_tasks:
        # Find or create the issue in the external system
        issue_id = task.metadata.get("external_issue_id")
        if issue_id:
            # Update existing issue
            await issue_tracker.update_issue(issue_id, {
                "status": map_status(task.status),
                "priority": map_priority(task.priority),
                "description": task.description
            })
        else:
            # Create new issue
            issue = await issue_tracker.create_issue({
                "title": task.title,
                "description": task.description,
                "status": map_status(task.status),
                "priority": map_priority(task.priority)
            })
            
            # Store the reference to the external issue
            await metis_client.update_task(task.id, {
                "metadata": {
                    "external_issue_id": issue.id,
                    "external_issue_url": issue.url
                }
            })
```

### Integration Testing

When integrating with Metis, it's important to test the integration thoroughly:

1. **API Contract Testing**: Ensure your client handles API responses correctly
2. **Event Handling Testing**: Verify proper handling of WebSocket events
3. **Error Handling Testing**: Test behavior when Metis is unavailable
4. **Authentication Testing**: Verify proper handling of authentication errors
5. **Performance Testing**: Test behavior under load

```python
# Example: Integration test for task creation
async def test_task_creation():
    # Setup test environment
    metis_client = MetisClient(base_url="http://localhost:8011")
    
    # Create a test task
    task_data = {
        "title": "Test Task",
        "description": "This is a test task",
        "status": "pending",
        "priority": "medium"
    }
    response = await metis_client.create_task(task_data)
    
    # Verify the response
    assert response["success"] == True
    assert "task" in response
    assert response["task"]["title"] == "Test Task"
    
    # Cleanup
    await metis_client.delete_task(response["task"]["id"])
```
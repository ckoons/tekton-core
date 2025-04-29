# Hermes Integration Guide

## Introduction

This guide provides instructions for integrating Tekton components with Hermes, the central message bus and component registration system. Hermes serves as the backbone for component interoperability, enabling seamless communication, discovery, and data sharing.

## Integration Overview

Integrating with Hermes involves:

1. **Registration**: Register your component with Hermes
2. **Discovery**: Discover other components and their capabilities
3. **Messaging**: Use the message bus for inter-component communication
4. **Database Access**: Access centralized database services
5. **Lifecycle Management**: Manage component lifecycle and health

## Single Port Architecture

Hermes follows Tekton's Single Port Architecture, using a single port (8001) for all operations. Following the same pattern in your component simplifies integration.

### URL Construction Pattern

All Hermes endpoints follow this pattern:
- HTTP API: `http://localhost:{HERMES_PORT}/api/{service}/{operation}`
- WebSocket: `ws://localhost:{HERMES_PORT}/ws/{service}`
- Events: `http://localhost:{HERMES_PORT}/events/{topic}`

Always use environment variables for port references:
```python
import os
hermes_url = f"http://localhost:{os.environ.get('HERMES_PORT', 8001)}/api"
```

## Component Registration

### Registration Process

1. Create a unique component ID (typically your component name in lowercase)
2. Define your component's capabilities (what services it provides)
3. Register with Hermes during startup
4. Store the returned authentication token
5. Use this token for all subsequent API calls

### Python Implementation

```python
from hermes.core.registration import RegistrationClient
import os

# Initialize client
hermes_url = f"http://localhost:{os.environ.get('HERMES_PORT', 8001)}/api"
registration_client = RegistrationClient(hermes_url)

# Define component details
component_id = "my-component"
component_port = int(os.environ.get("MY_COMPONENT_PORT", 8xxx))
component_endpoint = f"http://localhost:{component_port}/api"

# Register component
success, token = registration_client.register_component(
    component_id=component_id,
    name="My Component",
    version="1.0.0",
    component_type="custom",
    endpoint=component_endpoint,
    capabilities=["capability1", "capability2"],
    metadata={
        "description": "My custom Tekton component",
        "supports_streaming": True
    }
)

# Store token for future use
if success:
    # Store token securely (environment variable, secure storage, etc.)
    os.environ["MY_COMPONENT_TOKEN"] = token
else:
    # Handle registration failure
    print("Failed to register component with Hermes")
```

### JavaScript Implementation

```javascript
const axios = require('axios');

// Initialize client
const hermesPort = process.env.HERMES_PORT || 8001;
const hermesUrl = `http://localhost:${hermesPort}/api`;

// Define component details
const componentId = 'my-component';
const componentPort = process.env.MY_COMPONENT_PORT || 8xxx;
const componentEndpoint = `http://localhost:${componentPort}/api`;

// Register component
async function registerComponent() {
  try {
    const response = await axios.post(`${hermesUrl}/registration/register`, {
      component_id: componentId,
      name: 'My Component',
      version: '1.0.0',
      component_type: 'custom',
      endpoint: componentEndpoint,
      capabilities: ['capability1', 'capability2'],
      metadata: {
        description: 'My custom Tekton component',
        supports_streaming: true
      }
    });

    if (response.data.success) {
      // Store token for future use
      process.env.MY_COMPONENT_TOKEN = response.data.token;
      return response.data.token;
    } else {
      console.error('Failed to register component with Hermes');
      return null;
    }
  } catch (error) {
    console.error('Error registering component:', error);
    return null;
  }
}
```

### Required Registration Fields

| Field | Description | Example |
|-------|-------------|---------|
| `component_id` | Unique identifier | "my-component" |
| `name` | Human-readable name | "My Component" |
| `version` | Component version | "1.0.0" |
| `component_type` | Type category | "custom" |
| `endpoint` | Base API URL | "http://localhost:8xxx/api" |
| `capabilities` | Provided services | ["capability1", "capability2"] |
| `metadata` | Additional info | {"description": "..."} |

## Service Discovery

### Discovery Patterns

1. **Direct Lookup**: Get a specific component by ID
2. **Capability-based**: Find components with specific capabilities
3. **Full Registry**: Get all registered components

### Python Implementation

```python
from hermes.api.client import HermesClient
import os

# Initialize client
hermes_url = f"http://localhost:{os.environ.get('HERMES_PORT', 8001)}/api"
hermes_client = HermesClient(hermes_url)

# Get component by ID
engram_service = hermes_client.get_service("engram")
if engram_service:
    engram_endpoint = engram_service["endpoint"]
    engram_version = engram_service["version"]

# Find components by capability
memory_services = hermes_client.find_by_capability("memory")
for service in memory_services:
    if service["healthy"]:
        # Use the first healthy service
        memory_endpoint = service["endpoint"]
        break

# Get all services
all_services = hermes_client.get_all_services()
```

### JavaScript Implementation

```javascript
const axios = require('axios');

// Initialize client
const hermesPort = process.env.HERMES_PORT || 8001;
const hermesUrl = `http://localhost:${hermesPort}/api`;

// Get component by ID
async function getService(serviceId) {
  try {
    const response = await axios.get(`${hermesUrl}/discovery/service/${serviceId}`, {
      headers: {
        'Authorization': `Bearer ${process.env.MY_COMPONENT_TOKEN}`
      }
    });
    return response.data;
  } catch (error) {
    console.error(`Error getting service ${serviceId}:`, error);
    return null;
  }
}

// Find components by capability
async function findByCapability(capability) {
  try {
    const response = await axios.get(`${hermesUrl}/discovery/capability/${capability}`, {
      headers: {
        'Authorization': `Bearer ${process.env.MY_COMPONENT_TOKEN}`
      }
    });
    return response.data;
  } catch (error) {
    console.error(`Error finding services with capability ${capability}:`, error);
    return [];
  }
}
```

## Message Bus Integration

### Messaging Patterns

1. **Publish/Subscribe**: Asynchronous event broadcasting
2. **Request/Response**: Direct communication between components
3. **Broadcast**: Notify all components about system events

### Python Implementation

```python
from hermes.core.message_bus import MessageBus
import json

# Initialize message bus
message_bus = MessageBus()

# Define message handler
def handle_data_update(message):
    payload = message["payload"]
    headers = message["headers"]
    source_component = headers.get("component_id")
    
    # Process message...
    print(f"Received data update from {source_component}: {json.dumps(payload)}")

# Subscribe to topic
message_bus.subscribe("tekton.data.updated", handle_data_update)

# Publish message
message_bus.publish(
    topic="tekton.tasks.completed",
    message={
        "task_id": "123",
        "result": "success",
        "data": {"key": "value"}
    },
    headers={
        "component_id": "my-component",
        "priority": "high"
    }
)
```

### JavaScript Implementation (WebSocket)

```javascript
const WebSocket = require('ws');

// Initialize WebSocket connection
const hermesPort = process.env.HERMES_PORT || 8001;
const ws = new WebSocket(`ws://localhost:${hermesPort}/ws/message`);

// Subscribe to topics on connection
ws.on('open', () => {
  // Subscribe to topics
  ws.send(JSON.stringify({
    action: 'subscribe',
    topics: ['tekton.data.updated', 'tekton.system.events'],
    token: process.env.MY_COMPONENT_TOKEN
  }));
  
  // Publish message
  ws.send(JSON.stringify({
    action: 'publish',
    topic: 'tekton.tasks.completed',
    message: {
      task_id: '123',
      result: 'success',
      data: {key: 'value'}
    },
    headers: {
      component_id: 'my-component',
      priority: 'high'
    },
    token: process.env.MY_COMPONENT_TOKEN
  }));
});

// Handle incoming messages
ws.on('message', (data) => {
  const message = JSON.parse(data);
  if (message.type === 'message') {
    const payload = message.data.payload;
    const headers = message.data.headers;
    const topic = headers.topic;
    
    console.log(`Received message on topic ${topic}:`, payload);
    
    // Process message based on topic
    if (topic === 'tekton.data.updated') {
      // Handle data update
    } else if (topic === 'tekton.system.events') {
      // Handle system event
    }
  }
});
```

### Common Message Topics

| Topic Pattern | Description | Example |
|---------------|-------------|---------|
| `tekton.registration.*` | Registration events | `tekton.registration.completed` |
| `tekton.health.*` | Health status updates | `tekton.health.degraded` |
| `tekton.data.*` | Data changes | `tekton.data.updated` |
| `tekton.tasks.*` | Task lifecycle events | `tekton.tasks.completed` |
| `tekton.system.*` | System-wide events | `tekton.system.shutdown` |
| `component-specific` | Component-specific topics | `ergon.agent.created` |

## Database Integration

### Database Types

Hermes provides access to multiple database types:

1. **Vector Databases**: For semantic search and embeddings
2. **Graph Databases**: For knowledge graphs and relationships
3. **Key-Value Databases**: For simple structured storage
4. **Document Databases**: For unstructured document storage
5. **Cache Databases**: For high-performance caching
6. **Relational Databases**: For structured data with relationships

### Python Implementation

```python
from hermes.api.database_client import DatabaseClient
import os
import asyncio

# Initialize client
hermes_url = f"http://localhost:{os.environ.get('HERMES_PORT', 8001)}/api"
db_client = DatabaseClient(hermes_url)

# Define namespace (use component name for isolation)
namespace = "my-component"

# Vector database example
async def use_vector_db():
    # Get vector database connection
    vector_db = await db_client.get_vector_db(namespace=namespace)
    
    # Store vectors
    await vector_db.store(
        ids=["doc1", "doc2"],
        vectors=[[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]],
        metadata=[
            {"source": "document1", "type": "text"},
            {"source": "document2", "type": "code"}
        ]
    )
    
    # Query vectors
    results = await vector_db.query(
        vector=[0.1, 0.2, 0.3],
        top_k=5,
        filter={"type": "text"}
    )
    
    return results

# Key-value database example
async def use_kv_db():
    # Get key-value database connection
    kv_db = await db_client.get_key_value_db(namespace=namespace)
    
    # Store values
    await kv_db.set("user:123", {"name": "John", "role": "admin"})
    await kv_db.set("settings:theme", "dark")
    
    # Retrieve values
    user = await kv_db.get("user:123")
    theme = await kv_db.get("settings:theme")
    
    return user, theme

# Run async functions
async def main():
    vector_results = await use_vector_db()
    user, theme = await use_kv_db()
    print(f"Vector results: {vector_results}")
    print(f"User: {user}, Theme: {theme}")

asyncio.run(main())
```

### JavaScript Implementation

```javascript
const axios = require('axios');

// Initialize client
const hermesPort = process.env.HERMES_PORT || 8001;
const dbApiUrl = `http://localhost:${hermesPort}/api/database`;

// Define namespace (use component name for isolation)
const namespace = 'my-component';

// Vector database example
async function useVectorDb() {
  try {
    // Store vectors
    await axios.post(`${dbApiUrl}/vector/${namespace}/store`, {
      ids: ['doc1', 'doc2'],
      vectors: [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]],
      metadata: [
        {source: 'document1', type: 'text'},
        {source: 'document2', type: 'code'}
      ]
    }, {
      headers: {
        'Authorization': `Bearer ${process.env.MY_COMPONENT_TOKEN}`
      }
    });
    
    // Query vectors
    const response = await axios.post(`${dbApiUrl}/vector/${namespace}/query`, {
      vector: [0.1, 0.2, 0.3],
      top_k: 5,
      filter: {type: 'text'}
    }, {
      headers: {
        'Authorization': `Bearer ${process.env.MY_COMPONENT_TOKEN}`
      }
    });
    
    return response.data.results;
  } catch (error) {
    console.error('Error using vector database:', error);
    return [];
  }
}

// Key-value database example
async function useKvDb() {
  try {
    // Store values
    await axios.post(`${dbApiUrl}/key_value/${namespace}/set`, {
      key: 'user:123',
      value: {name: 'John', role: 'admin'}
    }, {
      headers: {
        'Authorization': `Bearer ${process.env.MY_COMPONENT_TOKEN}`
      }
    });
    
    // Retrieve values
    const response = await axios.post(`${dbApiUrl}/key_value/${namespace}/get`, {
      key: 'user:123'
    }, {
      headers: {
        'Authorization': `Bearer ${process.env.MY_COMPONENT_TOKEN}`
      }
    });
    
    return response.data.value;
  } catch (error) {
    console.error('Error using key-value database:', error);
    return null;
  }
}
```

## Lifecycle Management

### Component Lifecycle

1. **Initialization**: Register with Hermes and obtain token
2. **Operation**: Send heartbeats to indicate health
3. **Shutdown**: Unregister from Hermes before terminating

### Python Implementation

```python
from hermes.core.registration import RegistrationClient
import os
import signal
import threading
import time

# Initialize client
hermes_url = f"http://localhost:{os.environ.get('HERMES_PORT', 8001)}/api"
registration_client = RegistrationClient(hermes_url)

# Component details
component_id = "my-component"
component_port = int(os.environ.get("MY_COMPONENT_PORT", 8xxx))
component_endpoint = f"http://localhost:{component_port}/api"

# Store token globally
component_token = None

# Register component
def register_component():
    global component_token
    success, token = registration_client.register_component(
        component_id=component_id,
        name="My Component",
        version="1.0.0",
        component_type="custom",
        endpoint=component_endpoint,
        capabilities=["capability1", "capability2"]
    )
    
    if success:
        component_token = token
        print(f"Component registered successfully with token: {token}")
        return True
    else:
        print("Failed to register component")
        return False

# Heartbeat thread
def heartbeat_thread():
    global component_token
    
    while True:
        try:
            if component_token:
                # Send heartbeat with status
                success = registration_client.send_heartbeat(
                    component_id=component_id,
                    token=component_token,
                    status={
                        "uptime": time.time() - start_time,
                        "memory_usage": get_memory_usage(),
                        "active_tasks": get_active_tasks()
                    }
                )
                
                if not success:
                    print("Failed to send heartbeat, re-registering...")
                    register_component()
        except Exception as e:
            print(f"Error in heartbeat: {e}")
        
        # Sleep for heartbeat interval
        time.sleep(30)

# Unregister component
def unregister_component():
    global component_token
    
    if component_token:
        success = registration_client.unregister_component(
            component_id=component_id,
            token=component_token
        )
        
        if success:
            print("Component unregistered successfully")
        else:
            print("Failed to unregister component")

# Helper functions
def get_memory_usage():
    # Implementation to get memory usage
    return 0

def get_active_tasks():
    # Implementation to get active tasks
    return []

# Handle signals
def signal_handler(sig, frame):
    print("Shutting down...")
    unregister_component()
    os._exit(0)

# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# Start component
start_time = time.time()
if register_component():
    # Start heartbeat thread
    heart_thread = threading.Thread(target=heartbeat_thread, daemon=True)
    heart_thread.start()
    
    # Main component logic...
    try:
        # Component main loop
        while True:
            # Do component work
            time.sleep(1)
    except Exception as e:
        print(f"Error in main loop: {e}")
    finally:
        # Ensure unregistration
        unregister_component()
```

### JavaScript Implementation

```javascript
const axios = require('axios');
const process = require('process');

// Initialize client
const hermesPort = process.env.HERMES_PORT || 8001;
const hermesUrl = `http://localhost:${hermesPort}/api`;

// Component details
const componentId = 'my-component';
const componentPort = process.env.MY_COMPONENT_PORT || 8xxx;
const componentEndpoint = `http://localhost:${componentPort}/api`;

// Store token globally
let componentToken = null;
const startTime = Date.now();

// Register component
async function registerComponent() {
  try {
    const response = await axios.post(`${hermesUrl}/registration/register`, {
      component_id: componentId,
      name: 'My Component',
      version: '1.0.0',
      component_type: 'custom',
      endpoint: componentEndpoint,
      capabilities: ['capability1', 'capability2']
    });

    if (response.data.success) {
      componentToken = response.data.token;
      console.log(`Component registered successfully with token: ${componentToken}`);
      return true;
    } else {
      console.error('Failed to register component');
      return false;
    }
  } catch (error) {
    console.error('Error registering component:', error);
    return false;
  }
}

// Send heartbeat
async function sendHeartbeat() {
  try {
    if (componentToken) {
      const response = await axios.post(`${hermesUrl}/registration/heartbeat`, {
        component_id: componentId,
        token: componentToken,
        status: {
          uptime: (Date.now() - startTime) / 1000,
          memory_usage: process.memoryUsage().heapUsed,
          active_tasks: getActiveTasks()
        }
      });

      if (!response.data.success) {
        console.warn('Failed to send heartbeat, re-registering...');
        await registerComponent();
      }
    }
  } catch (error) {
    console.error('Error sending heartbeat:', error);
  }
}

// Unregister component
async function unregisterComponent() {
  try {
    if (componentToken) {
      const response = await axios.post(`${hermesUrl}/registration/unregister`, {
        component_id: componentId,
        token: componentToken
      });

      if (response.data.success) {
        console.log('Component unregistered successfully');
        return true;
      } else {
        console.error('Failed to unregister component');
        return false;
      }
    }
    return true;
  } catch (error) {
    console.error('Error unregistering component:', error);
    return false;
  }
}

// Helper functions
function getActiveTasks() {
  // Implementation to get active tasks
  return [];
}

// Start heartbeat interval
let heartbeatInterval = null;

// Handle signals
process.on('SIGINT', async () => {
  console.log('Shutting down...');
  clearInterval(heartbeatInterval);
  await unregisterComponent();
  process.exit(0);
});

process.on('SIGTERM', async () => {
  console.log('Shutting down...');
  clearInterval(heartbeatInterval);
  await unregisterComponent();
  process.exit(0);
});

// Start component
(async () => {
  if (await registerComponent()) {
    // Start heartbeat interval
    heartbeatInterval = setInterval(sendHeartbeat, 30000);
    
    // Main component logic...
    // ...
  }
})();
```

## Error Handling and Resilience

### Common Error Scenarios

1. **Hermes Unavailable**: Handle initial connection failures
2. **Token Expired**: Re-register when token expires
3. **Service Not Found**: Handle missing dependencies
4. **Database Errors**: Implement retry logic for database operations

### Best Practices

1. **Graceful Degradation**: Fall back to simpler functionality when dependencies unavailable
2. **Retry Logic**: Implement exponential backoff for transient failures
3. **Circuit Breaking**: Prevent cascading failures by temporarily disabling failing services
4. **Health Monitoring**: Actively monitor service health and report status

### Example Resilient Registration

```python
import time
import random

def register_with_retry(max_attempts=5, initial_backoff=1.0):
    """Register component with exponential backoff retry."""
    backoff = initial_backoff
    
    for attempt in range(1, max_attempts + 1):
        try:
            success, token = registration_client.register_component(
                component_id=component_id,
                name="My Component",
                version="1.0.0",
                component_type="custom",
                endpoint=component_endpoint,
                capabilities=["capability1", "capability2"]
            )
            
            if success:
                return token
            
        except Exception as e:
            print(f"Registration attempt {attempt} failed: {e}")
        
        # Calculate backoff with jitter
        jitter = random.uniform(0, 0.1 * backoff)
        sleep_time = backoff + jitter
        
        print(f"Retrying in {sleep_time:.2f} seconds")
        time.sleep(sleep_time)
        
        # Exponential backoff
        backoff *= 2
    
    # All attempts failed
    raise Exception(f"Failed to register after {max_attempts} attempts")
```

## Testing Integration

### Mock Hermes Services

When testing components, you can use mock services for Hermes:

```python
# Mock registration client
class MockRegistrationClient:
    def register_component(self, **kwargs):
        return True, "mock-token"
    
    def unregister_component(self, **kwargs):
        return True
    
    def send_heartbeat(self, **kwargs):
        return True

# Mock service registry
class MockServiceRegistry:
    def get_service(self, service_id):
        return {
            "id": service_id,
            "name": f"Mock {service_id}",
            "version": "1.0.0",
            "endpoint": f"http://localhost:8000/api",
            "capabilities": ["mock"],
            "healthy": True
        }
    
    def find_by_capability(self, capability):
        return [{
            "id": "mock-service",
            "name": "Mock Service",
            "version": "1.0.0",
            "endpoint": "http://localhost:8000/api",
            "capabilities": [capability],
            "healthy": True
        }]
```

### Test Utilities

Tekton provides test utilities for Hermes integration:

```python
# Example test using Tekton test utilities
from tekton.testing import MockHermesClient

def test_component_integration():
    # Create mock client
    mock_hermes = MockHermesClient()
    
    # Configure mock responses
    mock_hermes.register_service("engram", {
        "endpoint": "http://localhost:8000/api",
        "capabilities": ["memory"]
    })
    
    # Test component with mock
    my_component = MyComponent(hermes_client=mock_hermes)
    result = my_component.process_data({"test": "data"})
    
    # Assert expected behavior
    assert result.status == "success"
```

## Conclusion

Integrating with Hermes provides your component with access to the entire Tekton ecosystem. By following these patterns and best practices, you can ensure reliable, scalable, and resilient integration.

Remember:
1. Always use environment variables for port references
2. Register early in your component's lifecycle
3. Implement proper error handling and retry logic
4. Unregister during shutdown
5. Follow namespace conventions for database operations

For detailed API documentation, refer to the [Hermes Technical Documentation](./Hermes_Technical_Documentation.md).
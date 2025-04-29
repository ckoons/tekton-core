# Hermes Quick Reference Guide

## Overview
Hermes is the central message bus and component registration system for Tekton, providing:
- Component registration and discovery
- Message routing between components
- Centralized database services
- Lifecycle management

## Port and Endpoint
- **Port**: 8001 (default)
- **Environment Variable**: `HERMES_PORT`
- **Base URL**: `http://localhost:8001`
- **API Base URL**: `http://localhost:8001/api`
- **Health Check**: `http://localhost:8001/health`

## Key APIs

### Registration API
```python
# Register a component
success, token = registration_client.register_component(
    component_id="my-component",
    name="My Component",
    version="1.0.0",
    component_type="custom",
    endpoint="http://localhost:8xxx/api",
    capabilities=["capability1", "capability2"],
    metadata={"key": "value"}
)

# Unregister a component
success = registration_client.unregister_component(
    component_id="my-component",
    token=token
)

# Send heartbeat
success = registration_client.send_heartbeat(
    component_id="my-component",
    token=token,
    status={"state": "running"}
)
```

### Service Discovery API
```python
# Get a specific service
service = service_client.get_service("component-id")

# Find services by capability
services = service_client.find_by_capability("capability-name")

# Get all services
all_services = service_client.get_all_services()
```

### Message Bus API
```python
# Publish a message
success = message_client.publish(
    topic="tekton.topic.name",
    message={"key": "value"},
    headers={"priority": "high"}
)

# Subscribe to a topic
success = message_client.subscribe(
    topic="tekton.topic.name",
    callback=my_callback_function
)

# Unsubscribe from a topic
success = message_client.unsubscribe(
    topic="tekton.topic.name",
    callback=my_callback_function
)
```

### Database API
```python
# Get a vector database connection
vector_db = database_client.get_vector_db(
    namespace="my-namespace"
)

# Store vectors
success = vector_db.store(
    ids=["id1", "id2"],
    vectors=[[0.1, 0.2], [0.3, 0.4]],
    metadata=[{"source": "doc1"}, {"source": "doc2"}]
)

# Query vectors
results = vector_db.query(
    vector=[0.1, 0.2],
    top_k=5
)

# Available database types:
# - vector_db: Semantic search, embeddings
# - graph_db: Knowledge graphs, relationships
# - key_value_db: Simple key-value storage
# - document_db: Unstructured document storage
# - cache_db: High-performance caching
# - relational_db: Structured data with relationships
```

## Common Integration Patterns

### Component Startup
```python
import os
from hermes.core.registration import RegistrationClient

# Initialize client
hermes_url = f"http://localhost:{os.environ.get('HERMES_PORT', 8001)}/api"
client = RegistrationClient(hermes_url)

# Register component
token = client.register_component(
    component_id="my-component",
    name="My Component",
    version="1.0.0", 
    component_type="custom",
    endpoint=f"http://localhost:{os.environ.get('MY_COMPONENT_PORT', 8xxx)}/api",
    capabilities=["capability1", "capability2"]
)

# Store token securely for future API calls
```

### Component Shutdown
```python
# Unregister on shutdown
client.unregister_component(
    component_id="my-component",
    token=token
)
```

### Service Discovery Pattern
```python
from hermes.core.service_discovery import ServiceRegistry

# Find services with specific capability
matching_services = service_registry.find_by_capability("database")

# Get endpoint for the first healthy service
for service in matching_services:
    if service["healthy"]:
        endpoint = service["endpoint"]
        break
```

### Message Bus Pattern
```python
from hermes.core.message_bus import MessageBus

# Create message bus
message_bus = MessageBus()

# Define callback
def handle_message(message):
    payload = message["payload"]
    headers = message["headers"]
    # Process message...

# Subscribe to topic
message_bus.subscribe("tekton.events.data_updated", handle_message)

# Publish message
message_bus.publish(
    topic="tekton.events.task_completed",
    message={"task_id": "123", "status": "complete"},
    headers={"component_id": "my-component"}
)
```

### Database Access Pattern
```python
from hermes.core.database_manager import DatabaseManager

# Create database manager
db_manager = DatabaseManager()

# Get database connection
async def get_db():
    vector_db = await db_manager.get_vector_db(namespace="my-namespace")
    return vector_db

# Use database
async def store_data():
    db = await get_db()
    await db.store(
        ids=["id1"],
        vectors=[[0.1, 0.2, 0.3]],
        metadata=[{"source": "document1"}]
    )
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HERMES_PORT` | 8001 | Port for the Hermes API server |
| `HERMES_HOST` | 0.0.0.0 | Host for the Hermes API server |
| `HERMES_DATA_DIR` | ~/.tekton/data | Base directory for database storage |
| `HERMES_SECRET_KEY` | tekton-secret-key | Secret key for token generation |
| `DB_MCP_PORT` | 8002 | Port for the Database MCP server |
| `DB_MCP_HOST` | 127.0.0.1 | Host for the Database MCP server |
| `DEBUG` | False | Enable debug mode |

## Deployment

```bash
# Start Hermes
./scripts/tekton_launch --components hermes

# Check status
curl http://localhost:8001/health

# Stop Hermes
./scripts/tekton-kill --components hermes
```

## Troubleshooting

### Common Issues
1. **Connection Refused**: Hermes not running or wrong port
2. **Authentication Failed**: Invalid or expired token
3. **Service Not Found**: Component not registered
4. **Database Error**: Missing namespace or backend issue

### Debug Mode
```bash
export DEBUG=True
./scripts/tekton_launch --components hermes
```

### Check Logs
```bash
tail -f ~/.tekton/logs/hermes.log
```
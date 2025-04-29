# Hermes Technical Documentation

## Overview

Hermes is the central message bus and component registration system for the Tekton ecosystem. It facilitates communication between components, manages component lifecycles, and provides service discovery capabilities. Hermes serves as the foundation for component interoperability across the Tekton platform.

## Architecture

Hermes follows a modular architecture with several key subsystems:

### Core Subsystems

1. **Registration System**: Manages component registration, authentication, and lifecycle tracking
2. **Service Discovery**: Tracks available components and their capabilities
3. **Message Bus**: Routes messages between components
4. **Database Services**: Provides unified database access for all components
5. **Logging System**: Centralized logging infrastructure
6. **API Server**: HTTP/WebSocket interface for all Hermes services

### Component Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        Hermes API                           │
└───────────┬──────────────┬──────────────┬──────────────┬────┘
            │              │              │              │
┌───────────▼───┐  ┌───────▼────┐  ┌──────▼─────┐  ┌────▼─────┐
│ Registration  │  │   Service   │  │  Message   │  │ Database │
│    System     │  │  Discovery  │  │    Bus     │  │ Services │
└───────────────┘  └────────────┘  └────────────┘  └──────────┘
            │              │              │              │
┌───────────▼──────────────▼──────────────▼──────────────▼────┐
│                    Component Ecosystem                       │
│ (Engram, Ergon, Rhetor, Terma, Athena, Prometheus, etc.)    │
└─────────────────────────────────────────────────────────────┘
```

### Communication Flow

1. Components register with Hermes during startup
2. Hermes validates and stores component information
3. Components discover each other through Hermes
4. Messages are routed between components via the message bus
5. Components access database services through Hermes

## Key Features

### Registration System

The registration system manages the lifecycle of Tekton components:

- **Component Registration**: Register components with a unique ID, endpoint, and capabilities
- **Token-based Authentication**: Secure communication with signed tokens
- **Heartbeat Monitoring**: Track component health and availability
- **Capability Discovery**: Find components by their capabilities

#### Registration Process

1. Component calls `register_component()` with its details
2. Hermes validates the registration and issues a secure token
3. Component uses this token for all subsequent API calls
4. Hermes publishes a registration event to notify other components

### Service Discovery

The service discovery system maintains a registry of all available components:

- **Component Tracking**: Maintains a directory of registered components
- **Health Monitoring**: Periodically checks component health
- **Capability-based Lookup**: Find components by their capabilities
- **Metadata Storage**: Store and retrieve component metadata

#### Discovery Methods

- `get_service()`: Get information about a specific component
- `find_by_capability()`: Find components with a specific capability
- `get_all_services()`: Get all registered components

### Message Bus

The message bus enables asynchronous communication between components:

- **Topic-based Messaging**: Publish/subscribe to named topics
- **Message History**: Maintain a history of recent messages
- **Header Metadata**: Attach metadata to messages
- **Wildcard Subscriptions**: Subscribe to patterns of topics

#### Messaging Patterns

- **Publish/Subscribe**: Broadcast messages to multiple subscribers
- **Request/Response**: Asynchronous request/response communication
- **Event Notifications**: System and component events

### Database Services

The database services provide unified access to different types of databases:

- **Multiple Database Types**: Vector, Graph, Key-Value, Document, Cache, Relational
- **Namespace Isolation**: Separate namespaces for different components
- **Connection Pooling**: Efficient connection management
- **Automatic Backend Selection**: Use appropriate backends for each database type

#### Supported Database Types

- **Vector Databases**: Semantic search, embeddings (FAISS)
- **Graph Databases**: Knowledge graphs, relationships (Neo4j)
- **Key-Value Databases**: Simple structured storage (Redis)
- **Document Databases**: Unstructured document storage
- **Cache Databases**: High-performance caching
- **Relational Databases**: Structured data with relationships

## API Reference

### HTTP API Endpoints

Hermes exposes several API routes for different services:

- `/api`: Main API entry point
- `/api/registration`: Component registration endpoints
- `/api/discovery`: Service discovery endpoints
- `/api/message`: Message bus endpoints
- `/api/database`: Database services endpoints
- `/api/a2a`: Agent-to-agent communication endpoints
- `/api/mcp`: Multimodal Cognitive Protocol endpoints
- `/health`: System health check endpoint

### Registration API

```
POST /api/registration/register
{
  "component_id": "unique-id",
  "name": "Component Name",
  "version": "1.0.0",
  "component_type": "type",
  "endpoint": "http://localhost:port/api",
  "capabilities": ["capability1", "capability2"]
}

Response:
{
  "success": true,
  "token": "auth-token"
}
```

```
POST /api/registration/unregister
{
  "component_id": "unique-id",
  "token": "auth-token"
}

Response:
{
  "success": true
}
```

### Service Discovery API

```
GET /api/discovery/service/{service_id}

Response:
{
  "id": "unique-id",
  "name": "Component Name",
  "version": "1.0.0",
  "endpoint": "http://localhost:port/api",
  "capabilities": ["capability1", "capability2"],
  "healthy": true,
  "metadata": { ... }
}
```

```
GET /api/discovery/capability/{capability}

Response:
[
  {
    "id": "unique-id",
    "name": "Component Name",
    "version": "1.0.0",
    "endpoint": "http://localhost:port/api",
    "capabilities": ["capability1", "capability2"],
    "healthy": true,
    "metadata": { ... }
  },
  ...
]
```

### Message Bus API

```
POST /api/message/publish
{
  "topic": "tekton.topic.name",
  "message": { ... },
  "headers": { ... }
}

Response:
{
  "success": true
}
```

```
POST /api/message/subscribe
{
  "topic": "tekton.topic.name",
  "callback_url": "http://localhost:port/api/callback"
}

Response:
{
  "success": true,
  "subscription_id": "sub-id"
}
```

### Database API

```
POST /api/database/{db_type}/{namespace}/query
{
  "query": { ... }
}

Response:
{
  "results": [ ... ]
}
```

## Integration with Tekton Components

### Component Integration Pattern

Components integrate with Hermes using the following pattern:

1. **Registration**: Component registers with Hermes at startup
2. **Discovery**: Component discovers other services via Hermes
3. **Messaging**: Component uses message bus for event-driven communication
4. **Database Access**: Component uses database services for persistence

### Example Integration Code

```python
from hermes.core.registration import RegistrationClient
from hermes.api.database_client import DatabaseClient
from hermes.api.client import HermesClient

# Initialize clients
hermes_url = f"http://localhost:{os.environ.get('HERMES_PORT', 8001)}/api"
registration_client = RegistrationClient(hermes_url)
database_client = DatabaseClient(hermes_url)
hermes_client = HermesClient(hermes_url)

# Register component
token = registration_client.register(
    component_id="my-component",
    name="My Component",
    version="1.0.0",
    component_type="custom",
    endpoint="http://localhost:8005/api",
    capabilities=["my_capability"]
)

# Discover services
services = hermes_client.find_services_by_capability("database")

# Use database services
vector_db = database_client.get_vector_db(namespace="my_namespace")
results = vector_db.query(vector=[0.1, 0.2, 0.3], top_k=5)

# Subscribe to messages
hermes_client.subscribe("tekton.events.data_updated", callback_function)

# Publish messages
hermes_client.publish(
    topic="tekton.events.task_completed",
    message={"task_id": "123", "status": "complete"},
    headers={"priority": "high"}
)
```

## Configuration

### Environment Variables

- `HERMES_PORT`: Port for the Hermes API server (default: 8001)
- `HERMES_HOST`: Host for the Hermes API server (default: 0.0.0.0)
- `HERMES_DATA_DIR`: Base directory for database storage (default: ~/.tekton/data)
- `HERMES_SECRET_KEY`: Secret key for token generation (default: tekton-secret-key)
- `DB_MCP_PORT`: Port for the Database MCP server (default: 8002)
- `DB_MCP_HOST`: Host for the Database MCP server (default: 127.0.0.1)
- `DEBUG`: Enable debug mode (default: False)

### Configuration Options

Additional configuration options can be specified in the configuration file:

- Message bus settings
- Database connection parameters
- Token expiration periods
- Health check intervals

## Deployment

### Standalone Deployment

Hermes can be deployed as a standalone component:

```bash
# Start Hermes standalone
./scripts/tekton_launch --components hermes

# Check Hermes status
curl http://localhost:8001/health

# Run the registration server
python -m hermes.scripts.run_registration_server
```

### As Part of Tekton

When deployed as part of Tekton, Hermes is typically started first:

```bash
# Start core Tekton components
./scripts/tekton_launch --components hermes,engram,rhetor,ergon

# Check system status
./scripts/tekton_status
```

## Implementation Details

### Threading Model

Hermes uses a hybrid threading model:

- Primary API server runs in the main thread
- Health check monitoring runs in a background thread
- Database connections are managed asynchronously

### Error Handling

Hermes implements a comprehensive error handling strategy:

- API endpoints return appropriate HTTP status codes
- Database errors are captured and logged
- Component failures are detected through health checks
- Reconnection logic is applied for transient failures

### Security

Security measures in Hermes include:

- Token-based authentication for API endpoints
- Signed tokens with expiration
- Component validation before operations
- Namespace isolation for database operations

## Best Practices

### Using Hermes Effectively

1. **Register Early**: Register components during initialization
2. **Use Namespaces**: Use appropriate namespaces for database isolation
3. **Handle Reconnection**: Implement reconnection logic for service disruptions
4. **Send Heartbeats**: Regularly send heartbeats to indicate component health
5. **Use Message Bus**: Prefer message bus for cross-component communication
6. **Discover Dynamically**: Discover services at runtime, not startup

### Common Pitfalls

1. **Hardcoded URLs**: Always use service discovery, not hardcoded URLs
2. **Missing Error Handling**: Always handle potential failures in service calls
3. **Namespace Collisions**: Use unique namespaces for database operations
4. **Token Expiration**: Handle token renewal before expiration
5. **Missing Unregistration**: Always unregister components on shutdown

## Troubleshooting

### Common Issues

1. **Connection Refused**: Check if Hermes is running and accessible
2. **Authentication Failed**: Verify token validity and expiration
3. **Service Not Found**: Check registration status and component ID
4. **Database Error**: Verify database backend availability
5. **Message Not Delivered**: Check topic and subscription status

### Debugging

Enable debug mode for verbose logging:

```bash
# Enable debug mode
export DEBUG=True
./scripts/tekton_launch --components hermes
```

Check logs for detailed error information:

```bash
# View Hermes logs
tail -f ~/.tekton/logs/hermes.log
```

## Roadmap

Future Hermes development includes:

1. **Enhanced Security**: Role-based access control for services
2. **Distributed Deployment**: Support for multi-node deployment
3. **Message Persistence**: Durable message storage and replay
4. **Advanced Monitoring**: Dashboard for system monitoring
5. **Auto-scaling**: Dynamic resource allocation

## Conclusion

Hermes is the central nervous system of the Tekton ecosystem, providing essential infrastructure for component communication, discovery, and data management. Understanding Hermes is key to effectively building and integrating Tekton components.
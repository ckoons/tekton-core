# Tekton Single Port Architecture

## Overview

The Tekton Single Port Architecture is a design pattern that simplifies component communication by using a single port for all operations (HTTP, WebSocket, and Events) via path-based routing. This documentation explains the implementation and benefits of this architecture.

## Port Assignments

Each Tekton component now has a dedicated port for all its operations:

| Component | Port | Environment Variable | Description |
|-----------|------|----------------------|-------------|
| Hephaestus UI | 8080 | HEPHAESTUS_PORT | UI system (standard web UI port) |
| Engram | 8000 | ENGRAM_PORT | Memory system |
| Hermes | 8001 | HERMES_PORT | Service registry & database |
| Ergon | 8002 | ERGON_PORT | Agent system |
| Rhetor | 8003 | RHETOR_PORT | LLM management |
| Terma | 8004 | TERMA_PORT | Terminal system |
| Athena | 8005 | ATHENA_PORT | Knowledge graph |
| Prometheus | 8006 | PROMETHEUS_PORT | Planning system |
| Harmonia | 8007 | HARMONIA_PORT | Workflow system |
| Telos | 8008 | TELOS_PORT | Requirements system |
| Synthesis | 8009 | SYNTHESIS_PORT | Execution engine |
| Tekton Core | 8010 | TEKTON_CORE_PORT | Core orchestration |

## Implementation Details

### 1. Environment Variables

All port values are configured through environment variables, which are set in the `tekton-launch` script and used consistently across all components. For example:

```bash
export HEPHAESTUS_PORT=8080
export ENGRAM_PORT=8000
export HERMES_PORT=8001
# ...etc.
```

### 2. Path-Based Routing

Each component uses path-based routing to direct different types of requests:
- HTTP API: `/api/...`
- WebSocket: `/ws`
- Events: `/events`

Example: 
```
http://localhost:8003/api/message   # HTTP API endpoint on Rhetor
ws://localhost:8003/ws              # WebSocket endpoint on Rhetor
```

### 3. Client-Side Implementation

The frontend uses a configuration system to access component ports:

1. **Environment Variables**: Client-side environment variables provide port values:
   ```javascript
   window.HEPHAESTUS_PORT = 8080;
   window.RHETOR_PORT = 8003;
   // ...etc.
   ```

2. **Server Configuration Endpoint**: The UI server provides current port values:
   ```
   GET /api/config/ports
   ```

3. **Dynamic URL Construction**: Components build URLs using these variables:
   ```javascript
   const wsUrl = `ws://localhost:${window.RHETOR_PORT}/ws`;
   ```

### 4. Server-Side Implementation

Each service has been updated to:

1. Use a single port for all operations
2. Read port values from environment variables
3. Implement path-based routing for different protocols
4. Support WebSocket connections on the same port as HTTP

## Benefits

1. **Simplified Configuration**: Only one port per component to configure and remember
2. **Easier Firewall Management**: Fewer ports to manage and expose
3. **Consistent Pattern**: All components follow the same model
4. **Better Environment Variable Management**: Clean naming scheme for ports
5. **Enhanced Documentation**: Clear port assignments make integration easier

## Migrating to Single Port Architecture

When updating existing components to use the Single Port Architecture:

1. Update environment variable usage to read from the new port variables
2. Modify WebSocket server initialization to use the same port as HTTP
3. Implement path-based routing for different types of requests
4. Update client-side code to construct URLs using the environment variables

## Testing Single Port Components

To verify that a component correctly implements the Single Port Architecture:

1. Launch the component using the standard environment variable
2. Test HTTP API access on the component's port with `/api/...` endpoints
3. Test WebSocket connections on the same port with the `/ws` path
4. Verify that the component reads the port from the correct environment variable

## Future Enhancements

Future enhancements to the Single Port Architecture may include:

1. Standardized health check endpoints across all components
2. Automatic port conflict detection and resolution
3. Component-specific path prefixes for better routing (e.g., `/rhetor/api/...`)
4. Enhanced logging of port usage and connections
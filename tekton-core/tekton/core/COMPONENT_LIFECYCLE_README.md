# Component Lifecycle Management

This document describes the enhanced component lifecycle management system in Tekton, including state management, heartbeat monitoring with health metrics, and graceful degradation capabilities.

## State Management

### Component States

The system supports the following component states:

- `UNKNOWN` - State not known or not tracked
- `INITIALIZING` - Starting up but not ready for operations
- `READY` - Fully operational and accepting requests
- `ACTIVE` - Actively processing tasks
- `DEGRADED` - Running with limited functionality
- `INACTIVE` - Temporarily not accepting new requests
- `ERROR` - Operational error state but recoverable
- `FAILED` - Failed to start or crashed
- `STOPPING` - Graceful shutdown in progress
- `RESTARTING` - Temporary unavailable during restart

### State Transitions

State transitions are validated to ensure components follow proper lifecycle paths. Each state has defined valid transitions to other states. The system maintains a history of state transitions with timestamps, reason codes, and detailed descriptions.

### State Persistence

Component states are persisted in the registry and can be restored on system restart. This ensures that degraded or failed components are properly identified after system restarts.

## Health Monitoring

### Health Metrics

Components can report health metrics as part of their heartbeat messages:

- `cpu_usage` - CPU usage percentage (0.0-1.0)
- `memory_usage` - Memory usage percentage (0.0-1.0)
- `request_latency` - Average request latency in milliseconds
- `error_rate` - Error rate percentage (0.0-1.0)
- `throughput` - Requests per second

### Heartbeat System

The heartbeat system has been enhanced with:

- Configurable heartbeat intervals based on component type
- Staggered heartbeat timing to prevent thundering herd
- Automatic health metrics collection
- Component-specific thresholds for auto-degradation

### Automatic Recovery

Components that enter a degraded or error state can be automatically recovered:

- Recovery attempts are tracked and limited
- Multiple recovery strategies are supported (restart, reset, failover)
- Escalation path for persistent failures

## Graceful Degradation

### Capability Levels

Components can register capabilities with level indicators:

- Higher levels indicate better quality/performance
- Fallbacks can be registered at different levels
- System automatically selects highest available level

### Circuit Breaker Pattern

The system implements the circuit breaker pattern:

- Tracks failure rates for each capability
- Opens circuit after threshold failures
- Half-open state for testing recovery
- Automatic recovery after timeout

### Fallback Chain

Multiple fallbacks can be registered for each capability:

- Primary implementation (highest level)
- Secondary implementations (medium level)
- Emergency implementations (lowest level)
- Automatic selection based on availability

## Example Usage

### Component Registration

```python
# Register component with registry
registration = ComponentRegistration(
    component_id="example.service",
    component_name="Example Service",
    component_type="api"
)
success, message = await registry.register_component(registration)
```

### Capability Registration

```python
# Register capability with handler
await registry.register_capability(
    component_id="example.service",
    capability_name="process_data",
    capability_level=100,
    description="Process data with full functionality",
    parameters={"data": "object"},
    handler=process_data_function
)
```

### Fallback Registration

```python
# Register fallback for capability
await registry.register_fallback_handler(
    component_id="target.service",
    capability_name="process_data",
    provider_id="fallback.service",
    fallback_handler=fallback_function,
    capability_level=50
)
```

### Using Capabilities with Fallback

```python
# Execute capability with automatic fallback
try:
    result = await registry.execute_with_fallback(
        component_id="target.service",
        capability_name="process_data",
        data=input_data
    )
except NoFallbackAvailableError:
    # Handle case where all fallbacks failed
    pass
```

## Testing

A comprehensive test script is available at `scripts/test_component_lifecycle.py` that demonstrates:

- Component registration and state management
- Health metrics reporting
- Automatic degradation based on metrics
- Fallback mechanism with multiple levels
- Circuit breaker pattern implementation

To run the test:

```bash
python scripts/test_component_lifecycle.py
```
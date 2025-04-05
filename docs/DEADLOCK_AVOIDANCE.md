# Tekton Deadlock Avoidance System

## Overview

This document describes the deadlock avoidance system implemented in the Tekton component launcher. The system addresses potential deadlocks in the component startup process by introducing enhanced lifecycle management, dependency resolution, and component tracking mechanisms.

## Key Components

### 1. Component Lifecycle States

The system introduces a fine-grained component state model that allows for better tracking of component health and transitions:

```python
class ComponentState(Enum):
    UNKNOWN = "unknown"            # State not known or not tracked
    INITIALIZING = "initializing"  # Starting up but not ready for operations
    READY = "ready"                # Fully operational and accepting requests
    DEGRADED = "degraded"          # Running with limited functionality
    FAILED = "failed"              # Failed to start or crashed
    STOPPING = "stopping"          # Graceful shutdown in progress
    RESTARTING = "restarting"      # Temporary unavailable during restart
```

This model allows the system to distinguish between various component states and handle each appropriately.

### 2. Component Registration with UUID

Each component instance is registered with a unique identifier, launcher ID, and timestamp to prevent duplicate instances and enable proper instance tracking:

```python
registration = ComponentRegistration(
    component_id=component,
    instance_id=str(uuid.uuid4()),
    timestamp=time.time(),
    launcher_id=self.instance_id,
    metadata=metadata
)
```

This allows the system to:
- Detect when multiple launcher instances try to start the same component
- Resolve conflicts based on timestamp (newer wins)
- Track component ownership and lifecycle

### 3. Persistent Message Queue

A persistent message queue ensures that messages are not lost during component restarts or system failures:

```python
class PersistentMessageQueue:
    async def add_message(self, topic: str, message: Dict[str, Any]) -> bool:
        # Store message with sequence number and timestamp
        # ...

    async def get_messages(self, topic: str) -> List[Dict[str, Any]]:
        # Retrieve messages for topic
        # ...

    async def get_history(self, topic: str) -> List[Dict[str, Any]]:
        # Get message history for replay/recovery
        # ...
```

This allows for message replay during recovery and ensures no messages are lost during component transitions.

### 4. Dependency Cycle Detection and Resolution

The system actively detects and resolves circular dependencies between components:

```python
cycles = await self.dependency_resolver.detect_cycles()
if cycles:
    logger.warning(f"Dependency cycles detected: {cycles}")
    logger.info("Auto-resolving dependency cycles by breaking lowest priority edges")
    await self.dependency_resolver.resolve_cycles()
```

Cycle resolution uses a combination of:
- Priority-based breaking of dependency edges
- Alternative startup paths
- Degraded mode when necessary

### 5. Timeout Handling

All operations now have explicit timeouts to prevent indefinite hanging:

```python
try:
    launch_task = asyncio.create_task(super().launch_component(component, component_info))
    success = await asyncio.wait_for(launch_task, timeout=self.default_timeout)
    # ...
except asyncio.TimeoutError:
    logger.error(f"Component {component} launch timed out after {self.default_timeout}s")
    # Handle timeout...
```

### 6. Heartbeat System with Instance Tracking

The heartbeat system now includes instance tracking and health assessment:

```python
async def _on_heartbeat_received(self, component_id: str, heartbeat: Dict[str, Any]) -> None:
    # Extract component name from ID
    component_name = heartbeat.get("component_name", component_id.split(".")[-1])
    
    # Update component state
    if component_name in self.component_states:
        # Update to READY if it was previously degraded or initializing
        current_state = self.component_states[component_name]
        if current_state in [ComponentState.INITIALIZING, ComponentState.DEGRADED]:
            self.component_states[component_name] = ComponentState.READY
            logger.info(f"Component {component_name} transitioned to READY state")
```

### 7. Thundering Herd Prevention

Staggered restarts with jitter prevent multiple components from restarting simultaneously:

```python
# Schedule restart with jitter to prevent thundering herd
jitter = (hash(component_name) % 10) / 10.0  # 0.0 to 0.9
await asyncio.sleep(5 + jitter)
```

## Deadlock Scenarios Addressed

### 1. Circular Dependencies

**Problem:** Components A depends on B, which depends on C, which depends on A.

**Solution:**
- Automatic cycle detection with graph analysis
- Edge breaking based on component priority
- Partial satisfaction with degraded mode

### 2. Timeout Issues

**Problem:** Component stuck waiting indefinitely for a dependency.

**Solution:**
- Explicit timeouts on all operations
- State transitions to FAILED after timeout
- Retries with backoff

### 3. Hermes Availability Deadlock

**Problem:** Components waiting for Hermes, which is itself starting.

**Solution:**
- Readiness conditions instead of binary dependency checks
- Wait for component READY state, not just existence
- Support for degraded mode operation

### 4. Race Conditions with Message Bus

**Problem:** Message delivered before subscriber ready, message lost.

**Solution:**
- Persistent message queue with history
- Message replay capability during restart
- Subscription tracking with state

### 5. Incomplete Error Handling

**Problem:** Failed component blocking system progress.

**Solution:**
- Comprehensive error states (FAILED vs DEGRADED)
- Auto-restarting of failed components
- Breaking dependency chains when needed

### 6. Heartbeat Synchronization Issues

**Problem:** Missed heartbeats causing false failure detection.

**Solution:**
- Multiple missed heartbeats before state change
- Sequence numbers to track message order
- Different thresholds for DEGRADED vs FAILED

### 7. Duplicate Component Prevention

**Problem:** Multiple instances of same component causing conflicts.

**Solution:**
- UUID-based instance tracking
- Timestamp comparison for conflict resolution
- Launcher ID tracking for ownership

## Usage

The enhanced component launcher can be used with the following options:

```bash
python tekton_launcher.py --resolve-deadlocks --timeout 60 [components]
```

Key parameters:
- `--resolve-deadlocks`: Periodically check for and resolve potential deadlocks
- `--timeout`: Default timeout for component operations in seconds (default: 120)

## Testing

The system includes a comprehensive test suite in `test_deadlock_avoidance.py` that validates:
1. Component registration with instance tracking
2. Dependency cycle detection and resolution
3. Graceful handling of unhealthy components
4. Timeout handling for component operations
5. Proper lifecycle state transitions

Run tests with:

```bash
python scripts/test_deadlock_avoidance.py
```
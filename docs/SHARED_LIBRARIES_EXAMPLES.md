# Shared Libraries for Common Patterns

This document provides concrete examples of how to implement and utilize shared libraries for loops, events, and variables across Tekton components.

## 1. Loop Handling Library

### Implementation

```python
# tekton/utils/tekton_loops.py

from typing import List, Dict, Any, Callable, Optional, Union, TypeVar
import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass

T = TypeVar('T')
R = TypeVar('R')

@dataclass
class LoopResult:
    """Results from a loop execution."""
    completed: bool
    results: List[Any]
    errors: List[Dict[str, Any]]
    iterations: int

class LoopHandler:
    """Base class for all loop handlers."""
    
    def __init__(self, max_concurrency: int = 5, timeout: Optional[float] = None):
        self.max_concurrency = max_concurrency
        self.timeout = timeout
        self._stopped = False
    
    def stop(self):
        """Signal the loop to stop."""
        self._stopped = True
    
    def should_continue(self) -> bool:
        """Check if the loop should continue executing."""
        return not self._stopped

class ForLoopHandler(LoopHandler):
    """Handle classic for loops with range."""
    
    async def execute_async(self, 
                      start: int, 
                      end: int, 
                      step: int = 1, 
                      handler: Callable[[int], R]) -> LoopResult:
        """Execute a for loop asynchronously."""
        results = []
        errors = []
        iterations = 0
        
        for i in range(start, end, step):
            if not self.should_continue():
                break
                
            iterations += 1
            try:
                result = handler(i)
                results.append(result)
            except Exception as e:
                errors.append({
                    "iteration": i,
                    "error": str(e),
                    "exception": e
                })
                
        return LoopResult(
            completed=iterations == (end - start) // step,
            results=results,
            errors=errors,
            iterations=iterations
        )

class ForEachLoopHandler(LoopHandler):
    """Handle foreach loops that iterate over collections."""
    
    async def execute_async(self, 
                      items: List[T], 
                      handler: Callable[[T], R],
                      parallel: bool = False) -> LoopResult:
        """Execute a foreach loop, optionally in parallel."""
        results = []
        errors = []
        iterations = 0
        
        if not parallel:
            # Sequential execution
            for item in items:
                if not self.should_continue():
                    break
                    
                iterations += 1
                try:
                    result = handler(item)
                    results.append(result)
                except Exception as e:
                    errors.append({
                        "item": item,
                        "error": str(e),
                        "exception": e
                    })
        else:
            # Parallel execution with concurrency limit
            semaphore = asyncio.Semaphore(self.max_concurrency)
            
            async def process_item(item, idx):
                async with semaphore:
                    if not self.should_continue():
                        return None, None, idx
                        
                    try:
                        # Run CPU-bound handler in threadpool to avoid blocking the event loop
                        loop = asyncio.get_event_loop()
                        result = await loop.run_in_executor(None, handler, item)
                        return result, None, idx
                    except Exception as e:
                        error = {
                            "item": item,
                            "error": str(e),
                            "exception": e
                        }
                        return None, error, idx
            
            tasks = [process_item(item, i) for i, item in enumerate(items)]
            task_results = await asyncio.gather(*tasks)
            
            # Process results maintaining original order
            ordered_results = [None] * len(items)
            ordered_errors = [None] * len(items)
            
            for result, error, idx in task_results:
                if result is not None:
                    ordered_results[idx] = result
                if error is not None:
                    ordered_errors[idx] = error
            
            results = [r for r in ordered_results if r is not None]
            errors = [e for e in ordered_errors if e is not None]
            iterations = len(results) + len(errors)
                
        return LoopResult(
            completed=iterations == len(items),
            results=results,
            errors=errors,
            iterations=iterations
        )

class WhileLoopHandler(LoopHandler):
    """Handle while loops with condition functions."""
    
    async def execute_async(self, 
                      condition: Callable[[], bool], 
                      handler: Callable[[], R],
                      max_iterations: Optional[int] = 1000) -> LoopResult:
        """Execute a while loop with a condition function."""
        results = []
        errors = []
        iterations = 0
        
        while condition() and self.should_continue():
            if max_iterations is not None and iterations >= max_iterations:
                break
                
            iterations += 1
            try:
                result = handler()
                results.append(result)
            except Exception as e:
                errors.append({
                    "iteration": iterations,
                    "error": str(e),
                    "exception": e
                })
                
        return LoopResult(
            completed=not condition() or (max_iterations is not None and iterations >= max_iterations),
            results=results,
            errors=errors,
            iterations=iterations
        )
```

### Usage Example in Synthesis

```python
# synthesis/core/loop_handlers.py

from tekton.utils.tekton_loops import ForEachLoopHandler, LoopResult
from typing import Dict, Any, List
import asyncio
import logging

logger = logging.getLogger(__name__)

async def handle_foreach_loop(context: Dict[str, Any], step: Dict[str, Any]) -> Dict[str, Any]:
    """Handle a foreach loop step using the shared loop handler."""
    items = step.get("items", [])
    
    # Support variable substitution in items
    if isinstance(items, str) and items.startswith("$"):
        items_var = items[1:]
        items = context.get("variables", {}).get(items_var, [])
    
    step_template = step.get("step_template", {})
    parallel = step.get("parallel", False)
    max_concurrency = step.get("max_concurrency", 5)
    
    # Create loop handler from shared library
    loop_handler = ForEachLoopHandler(max_concurrency=max_concurrency)
    
    # Define handler function for each item
    async def process_item(item):
        # Create a new context with the item
        item_context = context.copy()
        item_context["variables"] = item_context.get("variables", {}).copy()
        item_context["variables"]["item"] = item
        
        # Execute the step template
        return await execute_step(item_context, step_template)
    
    # Execute the loop
    result = await loop_handler.execute_async(items, process_item, parallel=parallel)
    
    # Update context with results
    context["last_iteration"] = result.iterations
    context["loop_results"] = result.results
    context["loop_errors"] = result.errors
    context["loop_completed"] = result.completed
    
    return context
```

### Usage Example in Harmonia

```python
# harmonia/core/workflow.py

from tekton.utils.tekton_loops import ForEachLoopHandler
import logging
import asyncio

logger = logging.getLogger(__name__)

class WorkflowExecutor:
    def __init__(self, max_concurrency=5):
        self.max_concurrency = max_concurrency
    
    async def execute_parallel_tasks(self, workflow, task_nodes):
        """Execute workflow tasks in parallel using the shared loop handler."""
        loop_handler = ForEachLoopHandler(max_concurrency=self.max_concurrency)
        
        async def execute_task(task_node):
            task_id = task_node['id']
            logger.info(f"Executing task {task_id} in workflow {workflow.id}")
            return await self.execute_task(workflow, task_node)
        
        result = await loop_handler.execute_async(
            task_nodes, 
            execute_task,
            parallel=True
        )
        
        if result.errors:
            logger.error(f"Errors encountered in workflow {workflow.id}: {result.errors}")
            
        return result.results
```

## 2. Event System Library

### Implementation

```python
# tekton/utils/tekton_events.py

import asyncio
import uuid
from typing import Dict, List, Any, Set, Callable, Coroutine, Optional, Union
from dataclasses import dataclass, field
import json
import logging
import time
import weakref

logger = logging.getLogger(__name__)

@dataclass
class Event:
    """Base event class for all Tekton events."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: str = "event"
    timestamp: float = field(default_factory=time.time)
    source: str = "unknown"
    data: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary."""
        return {
            "id": self.id,
            "type": self.type,
            "timestamp": self.timestamp,
            "source": self.source,
            "data": self.data
        }
    
    def to_json(self) -> str:
        """Convert event to JSON string."""
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Event':
        """Create event from dictionary."""
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            type=data.get("type", "event"),
            timestamp=data.get("timestamp", time.time()),
            source=data.get("source", "unknown"),
            data=data.get("data", {})
        )

EventHandler = Callable[[Event], Coroutine[Any, Any, None]]

class EventBus:
    """Central event bus for publishing and subscribing to events."""
    
    def __init__(self):
        self._subscribers: Dict[str, Set[EventHandler]] = {}
        self._client_subscribers: Dict[str, Set[weakref.ref]] = {}
        self._event_history: List[Event] = []
        self._max_history = 1000
    
    async def publish(self, event: Event) -> None:
        """Publish an event to all subscribers."""
        if not isinstance(event, Event):
            event = Event.from_dict(event)
            
        logger.debug(f"Publishing event: {event.type}")
        
        # Store in history
        self._event_history.append(event)
        if len(self._event_history) > self._max_history:
            self._event_history = self._event_history[-self._max_history:]
        
        # Notify subscribers
        event_types = [event.type, "*"]  # Handle wildcard subscriptions
        tasks = []
        
        for event_type in event_types:
            subscribers = self._subscribers.get(event_type, set())
            for subscriber in subscribers:
                try:
                    tasks.append(asyncio.create_task(subscriber(event)))
                except Exception as e:
                    logger.error(f"Error notifying subscriber: {e}")
        
        # Notify WebSocket clients
        for event_type in event_types:
            clients = self._client_subscribers.get(event_type, set())
            dead_refs = []
            
            for client_ref in clients:
                client = client_ref()
                if client is None:
                    dead_refs.append(client_ref)
                    continue
                    
                try:
                    await client.send_json(event.to_dict())
                except Exception as e:
                    logger.error(f"Error sending to WebSocket client: {e}")
                    dead_refs.append(client_ref)
            
            # Clean up dead references
            for ref in dead_refs:
                clients.discard(ref)
        
        # Wait for all subscriber notifications to complete
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    def subscribe(self, event_type: str, handler: EventHandler) -> None:
        """Subscribe to events of a specific type."""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = set()
        self._subscribers[event_type].add(handler)
        
    def unsubscribe(self, event_type: str, handler: EventHandler) -> None:
        """Unsubscribe from events of a specific type."""
        if event_type in self._subscribers:
            self._subscribers[event_type].discard(handler)
    
    def subscribe_client(self, event_type: str, client) -> None:
        """Subscribe a WebSocket client to events."""
        if event_type not in self._client_subscribers:
            self._client_subscribers[event_type] = set()
        self._client_subscribers[event_type].add(weakref.ref(client))
    
    def unsubscribe_client(self, event_type: str, client) -> None:
        """Unsubscribe a WebSocket client from events."""
        if event_type in self._client_subscribers:
            client_ref = None
            for ref in self._client_subscribers[event_type]:
                if ref() is client:
                    client_ref = ref
                    break
            
            if client_ref:
                self._client_subscribers[event_type].discard(client_ref)
    
    def get_history(self, event_type: Optional[str] = None, limit: int = 100) -> List[Event]:
        """Get event history, optionally filtered by type."""
        if event_type:
            filtered = [e for e in self._event_history if e.type == event_type]
            return filtered[-limit:]
        return self._event_history[-limit:]

# Create a global instance for easy import
event_bus = EventBus()
```

### Usage Example in Synthesis

```python
# synthesis/api/app.py

from fastapi import FastAPI, WebSocket, Depends, HTTPException
from tekton.utils.tekton_events import event_bus, Event
import json
from typing import List, Dict, Any

app = FastAPI()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    # Handle the initial subscription message
    try:
        message = await websocket.receive_text()
        data = json.loads(message)
        
        if data.get("type") == "subscribe":
            event_types = data.get("event_types", ["execution_update"])
            
            # Subscribe the client to requested event types
            for event_type in event_types:
                event_bus.subscribe_client(event_type, websocket)
            
            # Send confirmation
            await websocket.send_json({
                "type": "subscription_confirmed",
                "event_types": event_types
            })
            
            # Keep the connection alive until client disconnects
            try:
                while True:
                    await websocket.receive_text()
            except Exception:
                # Client disconnected
                for event_type in event_types:
                    event_bus.unsubscribe_client(event_type, websocket)
    except Exception as e:
        # Handle connection errors
        if websocket.client_state.CONNECTED:
            await websocket.close()

@app.post("/api/executions/{execution_id}/events")
async def create_execution_event(execution_id: str, event_data: Dict[str, Any]):
    """Create and publish an execution event."""
    event = Event(
        type="execution_update",
        source="synthesis",
        data={
            "execution_id": execution_id,
            **event_data
        }
    )
    
    await event_bus.publish(event)
    return {"status": "published", "event_id": event.id}
```

### Usage Example in Prometheus

```python
# prometheus/core/planning_engine.py

from tekton.utils.tekton_events import event_bus, Event
import asyncio
import logging

logger = logging.getLogger(__name__)

class PlanningEngine:
    async def execute_plan(self, plan_id: str, plan_data: dict):
        """Execute a planning operation with event notifications."""
        # Publish plan started event
        await event_bus.publish(Event(
            type="plan_update",
            source="prometheus",
            data={
                "plan_id": plan_id,
                "status": "started",
                "message": f"Starting plan execution for {plan_id}"
            }
        ))
        
        try:
            # Execute plan steps...
            logger.info(f"Executing plan {plan_id}")
            
            # For each milestone in the plan
            for i, milestone in enumerate(plan_data.get("milestones", [])):
                # Publish milestone started event
                await event_bus.publish(Event(
                    type="plan_milestone",
                    source="prometheus",
                    data={
                        "plan_id": plan_id,
                        "milestone_index": i,
                        "milestone_id": milestone.get("id"),
                        "status": "started"
                    }
                ))
                
                # Process milestone...
                
                # Publish milestone completed event
                await event_bus.publish(Event(
                    type="plan_milestone",
                    source="prometheus",
                    data={
                        "plan_id": plan_id,
                        "milestone_index": i,
                        "milestone_id": milestone.get("id"),
                        "status": "completed"
                    }
                ))
            
            # Publish plan completed event
            await event_bus.publish(Event(
                type="plan_update",
                source="prometheus",
                data={
                    "plan_id": plan_id,
                    "status": "completed",
                    "message": f"Plan {plan_id} completed successfully"
                }
            ))
            
            return {"status": "success", "plan_id": plan_id}
            
        except Exception as e:
            logger.error(f"Error executing plan {plan_id}: {e}")
            
            # Publish error event
            await event_bus.publish(Event(
                type="plan_update",
                source="prometheus",
                data={
                    "plan_id": plan_id,
                    "status": "error",
                    "message": f"Error executing plan: {str(e)}"
                }
            ))
            
            return {"status": "error", "plan_id": plan_id, "error": str(e)}
```

## 3. Variable Substitution Library

### Implementation

```python
# tekton/utils/tekton_variables.py

import re
import os
from typing import Dict, Any, Union, List, Optional, Set
import logging
import json

logger = logging.getLogger(__name__)

class VariableSubstitutor:
    """Handle variable substitution in strings, objects, and commands."""
    
    def __init__(self, 
                 variables: Dict[str, Any] = None, 
                 include_env: bool = True,
                 missing_var_strategy: str = "leave",
                 max_recursion: int = 10):
        """
        Initialize the variable substitutor.
        
        Args:
            variables: Dictionary of variables for substitution
            include_env: Whether to include environment variables
            missing_var_strategy: How to handle missing variables:
                - "leave": Leave the variable reference unchanged
                - "empty": Replace with empty string
                - "error": Raise an error
            max_recursion: Maximum recursion depth for nested substitutions
        """
        self.variables = variables or {}
        self.include_env = include_env
        self.missing_var_strategy = missing_var_strategy
        self.max_recursion = max_recursion
        
        # Regex for variable patterns
        self.var_pattern = re.compile(r'\$\{([^{}]+)\}')  # ${var_name}
        self.simple_var_pattern = re.compile(r'\$([a-zA-Z0-9_]+)')  # $var_name
    
    def _get_variable_value(self, var_name: str) -> Any:
        """Get a variable value from the variables dict or environment."""
        # Check variables dict first
        if var_name in self.variables:
            return self.variables[var_name]
            
        # Check environment if enabled
        if self.include_env and var_name in os.environ:
            return os.environ[var_name]
            
        # Handle missing variables based on strategy
        if self.missing_var_strategy == "error":
            raise ValueError(f"Variable '{var_name}' not found")
        elif self.missing_var_strategy == "empty":
            return ""
        else:  # "leave" strategy
            return None
    
    def substitute_string(self, text: str, recursion_depth: int = 0) -> str:
        """Substitute variables in a string."""
        if not isinstance(text, str):
            return text
            
        if recursion_depth > self.max_recursion:
            logger.warning(f"Maximum recursion depth ({self.max_recursion}) reached during variable substitution")
            return text
            
        # Track substitutions to detect circular references
        substituted = False
        
        # Handle ${var_name} pattern
        def replace_var(match):
            nonlocal substituted
            var_name = match.group(1)
            value = self._get_variable_value(var_name)
            
            if value is None:  # Not found, using "leave" strategy
                return match.group(0)
                
            substituted = True
            return str(value)
            
        result = self.var_pattern.sub(replace_var, text)
        
        # Handle $var_name pattern
        def replace_simple_var(match):
            nonlocal substituted
            var_name = match.group(1)
            value = self._get_variable_value(var_name)
            
            if value is None:  # Not found, using "leave" strategy
                return match.group(0)
                
            substituted = True
            return str(value)
            
        result = self.simple_var_pattern.sub(replace_simple_var, result)
        
        # If substitutions were made, recursively process for nested variables
        if substituted and recursion_depth < self.max_recursion:
            result = self.substitute_string(result, recursion_depth + 1)
            
        return result
    
    def substitute_object(self, obj: Any, recursion_depth: int = 0) -> Any:
        """Recursively substitute variables in an object (dict, list, etc.)."""
        if recursion_depth > self.max_recursion:
            logger.warning(f"Maximum recursion depth ({self.max_recursion}) reached during variable substitution")
            return obj
            
        if isinstance(obj, str):
            return self.substitute_string(obj, recursion_depth)
            
        elif isinstance(obj, dict):
            return {k: self.substitute_object(v, recursion_depth + 1) for k, v in obj.items()}
            
        elif isinstance(obj, list):
            return [self.substitute_object(item, recursion_depth + 1) for item in obj]
            
        elif isinstance(obj, (int, float, bool, type(None))):
            return obj
            
        else:
            # For other types, convert to string, substitute, and try to convert back
            try:
                str_value = str(obj)
                substituted = self.substitute_string(str_value, recursion_depth)
                
                # If no substitution occurred, return original
                if substituted == str_value:
                    return obj
                    
                # Try to convert back to original type
                return type(obj)(substituted)
            except:
                # If conversion fails, return as string
                return self.substitute_string(str(obj), recursion_depth)
    
    def substitute_command(self, command: str, shell: bool = True) -> str:
        """
        Substitute variables in a command string.
        
        Args:
            command: The command string to process
            shell: Whether the command will be executed in a shell
                  (affects escaping of special characters)
        """
        result = self.substitute_string(command)
        
        # If shell is True, we need to handle escaping
        if shell:
            # Escape quotes and backslashes in variable values
            # This is complex and depends on the shell, simplified here
            result = result.replace('"', '\\"')
            
        return result
    
    def update_variables(self, new_variables: Dict[str, Any]) -> None:
        """Update the variables dictionary with new values."""
        self.variables.update(new_variables)
        
    def set_variable(self, name: str, value: Any) -> None:
        """Set a single variable value."""
        self.variables[name] = value
        
    def get_variable(self, name: str, default: Any = None) -> Any:
        """Get a variable value with an optional default."""
        return self.variables.get(name, default)
        
    def merge_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge the variables into a context dictionary and 
        substitute variables in the context.
        """
        if "variables" not in context:
            context["variables"] = {}
            
        # Merge variables
        context["variables"].update(self.variables)
        
        # Substitute variables in the entire context
        return self.substitute_object(context)
```

### Usage Example in Synthesis

```python
# synthesis/core/execution_engine.py

from tekton.utils.tekton_variables import VariableSubstitutor
from typing import Dict, Any, List
import logging
import os

logger = logging.getLogger(__name__)

class ExecutionContext:
    def __init__(self, variables=None, environment=None):
        # Initialize with provided variables and environment
        self.variables = variables or {}
        self.env = environment or {}
        
        # Create variable substitutor
        self.substitutor = VariableSubstitutor(
            variables=self.variables,
            include_env=True,
            missing_var_strategy="leave"
        )
    
    def substitute(self, value):
        """Substitute variables in a value."""
        return self.substitutor.substitute_object(value)
    
    def update_variables(self, new_variables):
        """Update context variables."""
        self.variables.update(new_variables)
        self.substitutor.update_variables(new_variables)
    
    def get_command(self, command_template):
        """Get a command with variables substituted."""
        return self.substitutor.substitute_command(command_template)

async def execute_command_step(context, step):
    """Execute a command step with variable substitution."""
    command_template = step.get("command", "")
    
    # Get command with variables substituted
    command = context.get_command(command_template)
    
    # Execute the command...
    # ...
    
    return result

async def execute_http_step(context, step):
    """Execute an HTTP request step with variable substitution."""
    # Substitute variables in URL, headers, and body
    request_data = context.substitute({
        "url": step.get("url", ""),
        "method": step.get("method", "GET"),
        "headers": step.get("headers", {}),
        "body": step.get("body", {})
    })
    
    # Make the HTTP request...
    # ...
    
    return response
```

### Usage Example in Harmonia

```python
# harmonia/core/template.py

from tekton.utils.tekton_variables import VariableSubstitutor
import logging

logger = logging.getLogger(__name__)

class WorkflowTemplate:
    def __init__(self, template_data):
        self.template = template_data
        self.name = template_data.get("name", "Unnamed Template")
        self.description = template_data.get("description", "")
        self.parameters = template_data.get("parameters", {})
    
    def instantiate(self, parameter_values=None):
        """
        Instantiate a workflow from the template with parameter values.
        """
        parameter_values = parameter_values or {}
        
        # Validate required parameters
        for param_name, param_def in self.parameters.items():
            if param_def.get("required", False) and param_name not in parameter_values:
                raise ValueError(f"Required parameter '{param_name}' not provided")
        
        # Apply default values for missing parameters
        for param_name, param_def in self.parameters.items():
            if param_name not in parameter_values and "default" in param_def:
                parameter_values[param_name] = param_def["default"]
        
        # Create variable substitutor with the parameter values
        substitutor = VariableSubstitutor(
            variables=parameter_values,
            include_env=True,
            missing_var_strategy="error"  # Fail if a parameter is missing
        )
        
        # Create a deep copy of the template with variables substituted
        workflow_data = substitutor.substitute_object(self.template)
        
        # Remove template-specific sections
        if "parameters" in workflow_data:
            del workflow_data["parameters"]
        
        return workflow_data
```

## Integration in UI Components

### WebSocket Event Subscription Example

```javascript
// tekton-ui-common.js

class TektonEventSubscriber {
  constructor(componentId, wsUrl = null) {
    this.componentId = componentId;
    this.wsUrl = wsUrl || `ws://${window.location.host}/ws`;
    this.socket = null;
    this.eventHandlers = {};
    this.connected = false;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectDelay = 1000;
  }
  
  connect() {
    if (this.socket) {
      this.disconnect();
    }
    
    this.socket = new WebSocket(this.wsUrl);
    
    this.socket.onopen = () => {
      console.log(`[${this.componentId}] WebSocket connected`);
      this.connected = true;
      this.reconnectAttempts = 0;
      
      // Subscribe to events
      if (Object.keys(this.eventHandlers).length > 0) {
        this.subscribe(Object.keys(this.eventHandlers));
      }
    };
    
    this.socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        
        // Handle subscription confirmation
        if (data.type === 'subscription_confirmed') {
          console.log(`[${this.componentId}] Subscribed to: ${data.event_types.join(', ')}`);
          return;
        }
        
        // Dispatch to event handlers
        if (data.type && this.eventHandlers[data.type]) {
          this.eventHandlers[data.type].forEach(handler => {
            try {
              handler(data);
            } catch (e) {
              console.error(`[${this.componentId}] Error in event handler:`, e);
            }
          });
        }
        
        // Dispatch to wildcard handlers
        if (this.eventHandlers['*']) {
          this.eventHandlers['*'].forEach(handler => {
            try {
              handler(data);
            } catch (e) {
              console.error(`[${this.componentId}] Error in wildcard handler:`, e);
            }
          });
        }
      } catch (e) {
        console.error(`[${this.componentId}] Error processing WebSocket message:`, e);
      }
    };
    
    this.socket.onclose = (event) => {
      this.connected = false;
      console.log(`[${this.componentId}] WebSocket closed:`, event.code, event.reason);
      
      // Attempt to reconnect
      if (this.reconnectAttempts < this.maxReconnectAttempts) {
        this.reconnectAttempts++;
        const delay = this.reconnectDelay * Math.pow(1.5, this.reconnectAttempts - 1);
        console.log(`[${this.componentId}] Reconnecting in ${delay}ms...`);
        
        setTimeout(() => this.connect(), delay);
      }
    };
    
    this.socket.onerror = (error) => {
      console.error(`[${this.componentId}] WebSocket error:`, error);
    };
  }
  
  disconnect() {
    if (this.socket) {
      this.socket.close();
      this.socket = null;
      this.connected = false;
    }
  }
  
  subscribe(eventTypes) {
    if (!Array.isArray(eventTypes)) {
      eventTypes = [eventTypes];
    }
    
    if (this.connected) {
      this.socket.send(JSON.stringify({
        type: 'subscribe',
        event_types: eventTypes
      }));
    }
  }
  
  on(eventType, handler) {
    if (!this.eventHandlers[eventType]) {
      this.eventHandlers[eventType] = [];
      
      // If already connected, subscribe to this event type
      if (this.connected) {
        this.subscribe([eventType]);
      }
    }
    
    this.eventHandlers[eventType].push(handler);
    return this; // For chaining
  }
  
  off(eventType, handler) {
    if (this.eventHandlers[eventType]) {
      if (handler) {
        // Remove specific handler
        this.eventHandlers[eventType] = this.eventHandlers[eventType]
          .filter(h => h !== handler);
      } else {
        // Remove all handlers for this event type
        delete this.eventHandlers[eventType];
      }
    }
    return this; // For chaining
  }
}
```

### Usage in Synthesis UI Component

```javascript
// synthesis-component.js

import { TektonEventSubscriber } from '../../lib/tekton-ui-common.js';

class SynthesisComponent extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    
    // Create event subscriber
    this.events = new TektonEventSubscriber('synthesis-component');
    
    // Initialize component
    this.init();
  }
  
  async init() {
    // Set up shadow DOM
    this.shadowRoot.innerHTML = `
      <link rel="stylesheet" href="styles/synthesis.css">
      <div class="synthesis-container">
        <div class="execution-controls">
          <!-- Controls here -->
        </div>
        <div class="execution-view">
          <!-- Execution visualization here -->
        </div>
        <div class="execution-log">
          <!-- Log output here -->
        </div>
      </div>
    `;
    
    // Set up event handlers
    this.setupEventHandlers();
    
    // Connect to WebSocket for real-time updates
    this.events.connect();
    
    // Subscribe to execution events
    this.events
      .on('execution_update', this.handleExecutionUpdate.bind(this))
      .on('execution_step_update', this.handleStepUpdate.bind(this))
      .on('execution_completed', this.handleExecutionCompleted.bind(this));
  }
  
  setupEventHandlers() {
    // UI event handlers
    // ...
  }
  
  handleExecutionUpdate(event) {
    console.log('Execution update:', event);
    // Update UI with execution status
    // ...
  }
  
  handleStepUpdate(event) {
    console.log('Step update:', event);
    // Update step visualization
    // ...
  }
  
  handleExecutionCompleted(event) {
    console.log('Execution completed:', event);
    // Show completion status
    // ...
  }
  
  disconnectedCallback() {
    // Clean up event subscribers
    this.events.disconnect();
  }
}

customElements.define('synthesis-component', SynthesisComponent);
```

## Benefits of Shared Libraries

These shared libraries provide numerous benefits to the Tekton ecosystem:

1. **Consistency**: Ensure consistent behavior across components
2. **Reduced Duplication**: Eliminate redundant code
3. **Simplified Maintenance**: Fix bugs once, benefit everywhere
4. **Faster Development**: Accelerate implementation of new components
5. **Better Testing**: Centralize testing of critical functionality
6. **Improved Documentation**: Document patterns once in a central location
7. **Enhanced Reliability**: Well-tested shared code is more reliable

## Implementation Strategy

1. **Initial Extraction**: Extract existing patterns from implemented components
2. **Comprehensive Tests**: Create thorough tests for each shared library
3. **Documentation**: Document usage patterns with clear examples
4. **Gradual Adoption**: Refactor existing components to use shared libraries
5. **Integration in Templates**: Include in component templates for new development
6. **Version Management**: Implement proper versioning for shared utilities

By implementing these shared libraries, we can significantly reduce development time and improve consistency across the Tekton ecosystem while making the system more maintainable and robust.
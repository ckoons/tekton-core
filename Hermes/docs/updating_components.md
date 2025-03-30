# Updating Components to Centralized Services

This guide explains how to update existing Tekton components to use the centralized services in Hermes, including the Unified Registration Protocol and Centralized Logging System.

## Centralized Logging System

### Basic Integration

The simplest way to update a component to use the Centralized Logging System is to replace the standard Python logging with the Hermes logging system:

1. Replace logging imports:

```python
# Old imports
import logging

# New imports
try:
    from hermes.utils.logging_helper import setup_logging
    USE_CENTRALIZED_LOGGING = True
except ImportError:
    # Fall back to standard logging if Hermes is not available
    import logging
    USE_CENTRALIZED_LOGGING = False
```

2. Replace logger initialization:

```python
# Old initialization
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("component.module")

# New initialization
if USE_CENTRALIZED_LOGGING:
    # Use Centralized Logging System
    logger = setup_logging("component.module")
else:
    # Fall back to standard logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    logger = logging.getLogger("component.module")
```

3. Update log calls to use additional features (optional):

```python
# Basic logging (works with both systems)
logger.info("User logged in")
logger.error("Database connection failed")

# Enhanced logging (only with Centralized Logging)
if USE_CENTRALIZED_LOGGING:
    # Log with context
    logger.info(
        "User action",
        code="USER001",
        context={"user_id": "user123", "action": "login"}
    )
    
    # Log system events using NORMAL level
    logger.normal("System started", code="SYS001")
    
    # Create correlated logger
    correlation_id = "transaction-123"
    correlated_logger = logger.with_correlation(correlation_id)
    correlated_logger.info("Transaction started", code="TRANS001")
    correlated_logger.info("Transaction completed", code="TRANS002")
```

### Converting Print Statements

Many components use `print()` statements for output. These can be converted to proper logging:

```python
# Old code
print(f"Processing task {task_id}")

# New code
logger.info(f"Processing task {task_id}")
```

For debugging print statements:

```python
# Old code
print(f"DEBUG: Variable value: {value}")

# New code
logger.debug(f"Variable value: {value}")
```

### Stdout/Stderr Redirection

For components that can't easily change all print statements, you can redirect stdout/stderr:

```python
from hermes.utils.logging_helper import patch_stdout_stderr

# Redirect stdout/stderr to the logging system
patch_stdout_stderr("component.module")

# Now all print statements will go to the logging system
print("This will be logged as INFO")
print("This will be logged as ERROR", file=sys.stderr)
```

### Python Logging Interception

For components using Python's logging extensively:

```python
from hermes.utils.logging_helper import intercept_python_logging

# Intercept all Python logging
intercept_python_logging("component.module")

# Now all Python logging calls will go to the Centralized Logging System
import logging
logging.getLogger("some.module").info("This will be redirected")
```

## Unified Registration Protocol

### Basic Integration

To update a component to use the Unified Registration Protocol:

1. Add imports:

```python
from hermes.utils.registration_helper import register_component
```

2. Add registration code at component startup:

```python
async def start_component():
    # Register with Hermes
    registration = await register_component(
        component_id="my_component_id",
        component_name="My Component",
        component_type="custom",
        component_version="1.0.0",
        capabilities=["custom.capability1", "custom.capability2"]
    )
    
    if not registration:
        logger.fatal("Failed to register with Hermes, component cannot start")
        return False
    
    # Store registration for later use
    global _registration
    _registration = registration
    
    # Component successfully started
    return True
```

3. Add cleanup code at component shutdown:

```python
async def stop_component():
    # Unregister from Hermes
    if _registration:
        await _registration.unregister()
        await _registration.close()
    
    # Component successfully stopped
    return True
```

### Using Messaging

Once registered, you can use the messaging system:

```python
# Publish a message
_registration.publish_message(
    topic="my.topic",
    message={"data": "Hello World"}
)

# Subscribe to a topic
def handle_message(message):
    print(f"Received message: {message}")

_registration.subscribe_to_topic(
    topic="other.topic",
    callback=handle_message
)
```

## Converting Multiple Components

The `scripts/update_engram_logging.py` script is an example of how to automate the conversion process. You can use it as a template for updating other components:

```bash
python scripts/update_engram_logging.py --engram-path /path/to/Engram
```

## Testing the Integration

After updating a component, test it to ensure it works correctly:

1. Run the component with Hermes available
2. Check that logs are appearing in the Centralized Logging System
3. Run the component without Hermes (should fall back to standard logging)
4. Verify the component functions correctly in both scenarios

## Best Practices

- **Backward Compatibility**: Always maintain backward compatibility so components work even if Hermes is not available
- **Correlation IDs**: Use correlation IDs for related operations to make debugging easier
- **Context Information**: Add relevant context to log entries
- **Log Levels**: Use appropriate log levels for different types of messages
- **System Events**: Use the NORMAL log level for system lifecycle events
- **Documentation**: Update component documentation to mention the integration with Hermes
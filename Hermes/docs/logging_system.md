# Centralized Logging System

The Centralized Logging System (CLS) is a comprehensive logging infrastructure for Tekton components, providing structured, schema-versioned logging with effective timestamps and extensive querying capabilities.

## Overview

The CLS provides the following benefits:

- **Structured Logging**: All logs follow a standardized schema
- **Schema Versioning**: Log schema evolution is tracked for backward compatibility
- **Effective Timestamps**: Distinguish between when an event occurred vs. when it was logged
- **Log Levels**: Seven standardized log levels (FATAL, ERROR, WARN, INFO, NORMAL, DEBUG, TRACE)
- **Contextual Information**: Rich context for all log entries
- **Correlation**: Track related log entries across components
- **Query Capabilities**: Advanced log query and analysis tools
- **Storage**: Persistent storage of logs with efficient retrieval

## Log Levels

The CLS defines seven standardized log levels:

1. **FATAL**: At least one system component is inoperable, causing a fatal error within the larger system, typically requiring immediate attention and system restart
2. **ERROR**: At least one system component is inoperable and is interfering with the operability of other functionalities
3. **WARN**: An unexpected event has occurred that may disrupt or delay other processes but does not prevent system operation
4. **INFO**: An event has occurred that does not appear to affect operations and usually can be ignored
5. **NORMAL**: System lifecycle events such as component startup/shutdown, user login/logout, or expected state transitions
6. **DEBUG**: Relevant details useful during software debugging or troubleshooting within test environments
7. **TRACE**: Execution of code with full visibility within the application or third-party libraries

## Integration Guide

### Basic Integration

The simplest way to integrate with the CLS is to use the `logging_helper` module:

```python
from hermes.utils.logging_helper import setup_logging

# Set up logging for your component
logger = setup_logging("my.component")

# Log messages at different levels
logger.fatal("Fatal error occurred", code="FATAL001")
logger.error("Error occurred", code="ERROR001")
logger.warn("Warning condition", code="WARN001")
logger.info("Informational message", code="INFO001")
logger.normal("System startup", code="NORMAL001")
logger.debug("Debug information", code="DEBUG001")
logger.trace("Trace information", code="TRACE001")

# Log with context
logger.info(
    "User action",
    code="USER001",
    context={
        "user_id": "user123",
        "action": "login",
        "ip_address": "192.168.1.1"
    }
)

# Log with correlation ID for tracking related events
correlation_id = "transaction-123"
logger.info(
    "Transaction started",
    code="TRANS001",
    correlation_id=correlation_id
)
```

### Extended Integration

For more advanced integration, you can use additional features:

```python
from hermes.utils.logging_helper import (
    setup_logging, intercept_python_logging,
    patch_stdout_stderr, create_correlation_context
)

# Set up logging for your component
logger = setup_logging("my.component")

# Create a logger with default context
user_logger = logger.with_context({
    "user_id": "user123",
    "session_id": "session456"
})

# All logs from this logger will include the context
user_logger.info("User logged in")
user_logger.info("User action", context={"action": "update"})

# Create correlation context for tracking related events
correlation_id = create_correlation_context()
correlated_logger = logger.with_correlation(correlation_id)

# All logs from this logger will use the same correlation ID
correlated_logger.info("Operation started")
correlated_logger.info("Step 1 completed")
correlated_logger.info("Operation completed")

# Intercept Python's logging system
intercept_python_logging("my.component")

# Now standard Python logging will redirect to Tekton logging
import logging
logging.error("This will go to Tekton logs")

# Redirect stdout/stderr to logging system
patch_stdout_stderr("my.component")

# Now print statements will go to Tekton logs
print("This will be logged as INFO")
print("This will be logged as ERROR", file=sys.stderr)
```

### Querying Logs

The CLS provides powerful querying capabilities:

```python
from hermes.core.logging import get_logger, LogLevel

# Get logger
logger = get_logger("my.component")

# Query logs
logs = logger.log_manager.query(
    start_time=time.time() - 86400,  # Last 24 hours
    end_time=time.time(),
    components=["my.component"],
    levels=[LogLevel.ERROR, LogLevel.FATAL],
    limit=100
)

# Process logs
for log in logs:
    print(f"[{log.level.name}] {log.timestamp} - {log.message}")
    if log.context:
        print(f"  Context: {log.context}")
```

## Schema

All log entries follow this standardized schema:

```json
{
  "timestamp": 1625097600.123,
  "effective_timestamp": 1625097500.456,
  "component": "my.component",
  "level": "INFO",
  "schema_version": "1.0.0",
  "correlation_id": "550e8400-e29b-41d4-a716-446655440000",
  "client_id": "client123",
  "message": "User logged in",
  "code": "USER001",
  "context": {
    "user_id": "user123",
    "ip_address": "192.168.1.1"
  },
  "stack_trace": null
}
```

## Best Practices

1. **Use Proper Levels**: Choose the appropriate log level for each message
2. **Include Context**: Add relevant contextual information to logs
3. **Use Correlation IDs**: Track related operations across components
4. **Use Event Codes**: Assign standardized event codes for easier analysis
5. **Include Effective Timestamps**: When logging events that occurred at a different time
6. **Use NORMAL for Lifecycle Events**: System startup/shutdown, user login/logout, etc.
7. **Schema Versioning**: Update schema version when log structure changes
8. **Handle Sensitive Data**: Avoid logging sensitive information or use redaction

## Implementation Details

The CLS consists of the following components:

- **LogLevel**: Enumeration of standardized log levels
- **LogEntry**: Structured representation of a log entry
- **LogStorage**: Storage backend for log entries
- **LogManager**: Central manager for log processing
- **Logger**: Interface for components to log messages
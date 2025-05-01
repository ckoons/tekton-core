# Harmonia Advanced Features

This document covers advanced features of the Harmonia workflow orchestration engine, including expression evaluation, conditional logic, webhooks, and dynamic workflow behavior.

## Table of Contents

1. [Expression System](#expression-system)
2. [Conditional Task Execution](#conditional-task-execution)
3. [Webhook Integration](#webhook-integration)
4. [Dynamic Workflows](#dynamic-workflows)
5. [Advanced Scheduling](#advanced-scheduling)
6. [Component Communication](#component-communication)

## Expression System

Harmonia's expression system allows for dynamic, context-aware workflows through a flexible parameter substitution mechanism.

### Expression Syntax

Expressions in Harmonia use the following syntax:

```
${<expression>}
```

where `<expression>` can be any of these types:

- **Parameters**: `${param.<parameter_name>}`
- **Task Outputs**: `${tasks.<task_id>.output.<property>}`
- **Environment Variables**: `${env.<env_var>}`
- **Context Values**: `${context.<context_property>}`
- **Evaluated Expressions**: `${expr.<expression>}` (requires safe mode disabled)

### Parameter Substitution

Parameters can be used in task input values:

```json
{
  "task_id": "format_message",
  "component": "text_processor",
  "action": "format",
  "input": {
    "template": "Hello, ${param.name}!",
    "variables": {
      "timestamp": "${context.execution.start_time}",
      "previous_result": "${tasks.previous_task.output.result}"
    }
  }
}
```

### Nested Properties

You can access nested properties using dot notation:

```json
{
  "data_path": "${tasks.fetch_data.output.results.items[0].id}"
}
```

This accesses the ID of the first item in the results array from the `fetch_data` task's output.

### Expression Evaluation

For more complex logic, you can use the `expr` prefix (when safe mode is disabled):

```json
{
  "condition": "${expr.len(tasks.get_items.output.items) > 5}"
}
```

This evaluates whether the number of items in the output of the `get_items` task is greater than 5.

### Context Variables

The following context variables are available in expressions:

- `workflow`: Information about the workflow definition
  - `id`: Workflow ID
  - `name`: Workflow name
- `execution`: Information about the current execution
  - `id`: Execution ID
  - `start_time`: Start time of execution
- `input`: Workflow input parameters
- `tasks`: Results from completed tasks

Example:

```json
{
  "log_message": "Executing ${context.workflow.name} with ID ${context.execution.id}"
}
```

## Conditional Task Execution

Harmonia supports conditional task execution based on the results of previous tasks or other context variables.

### Simple Conditions

Tasks can include a condition in their metadata:

```json
{
  "task_id": "process_large_dataset",
  "component": "data_processor",
  "action": "process",
  "input": {
    "data": "${tasks.fetch_data.output.data}"
  },
  "metadata": {
    "condition": "${tasks.fetch_data.output.item_count > 100}"
  }
}
```

The `process_large_dataset` task will only execute if the `item_count` in the output of the `fetch_data` task is greater than 100.

### Complex Logical Conditions

For more complex conditions, you can use structured condition objects:

```json
{
  "task_id": "notify_admin",
  "component": "notification",
  "action": "send_email",
  "input": {
    "to": "admin@example.com",
    "subject": "Data Processing Alert",
    "body": "The data processing job has encountered issues."
  },
  "metadata": {
    "condition": {
      "or": [
        {"gt": ["${tasks.process_data.output.error_count}", 0]},
        {"lt": ["${tasks.process_data.output.success_rate}", 0.9]}
      ]
    }
  }
}
```

This task will execute if either the error count is greater than 0 OR the success rate is less than 90%.

### Condition Operators

The following logical operators are supported:

- `and`: All conditions must be true
- `or`: At least one condition must be true
- `not`: The condition must be false

The following comparison operators are supported:

- `eq`: Equal to
- `neq`: Not equal to
- `gt`: Greater than
- `gte`: Greater than or equal to
- `lt`: Less than
- `lte`: Less than or equal to
- `in`: Value is in collection
- `contains`: Collection contains value

### Skip Logic

When a task's condition evaluates to false, the task is skipped, and its dependencies are updated accordingly. Skipped tasks don't affect the overall workflow status, but they're recorded in the execution history for auditing and debugging.

## Webhook Integration

Harmonia provides powerful webhook functionality for triggering workflows from external events and for workflow tasks to notify external systems.

### Inbound Webhooks

Inbound webhooks allow external systems to trigger workflow executions by sending HTTP requests to Harmonia.

#### Creating a Webhook

```json
{
  "name": "GitHub Push Webhook",
  "description": "Triggered when changes are pushed to the repository",
  "endpoint": "/webhooks/github/push",
  "trigger_type": "http_post",
  "workflow_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "input_mapping": {
    "repository": "$.repository.full_name",
    "branch": "$.ref",
    "commits": "$.commits"
  },
  "auth_type": "hmac",
  "auth_config": {
    "secret": "your-webhook-secret",
    "header": "X-Hub-Signature-256",
    "algorithm": "sha256"
  }
}
```

This webhook:
- Creates an endpoint at `/webhooks/github/push`
- Maps JSON fields from the webhook payload to workflow input parameters
- Uses HMAC authentication to verify the request

#### Input Mapping

The `input_mapping` field uses JSONPath expressions to extract values from the webhook payload:

- `$.repository.full_name`: Get the repository name from the payload
- `$.ref`: Get the branch reference
- `$.commits`: Get the array of commits

#### Authentication Types

Harmonia supports multiple authentication methods for webhooks:

- `none`: No authentication
- `basic`: HTTP Basic authentication
- `bearer`: Bearer token authentication
- `api_key`: API key in header or query parameter
- `hmac`: HMAC signature validation
- `custom`: Custom authentication logic

### Outbound Webhooks

Workflows can notify external systems about events using outbound webhooks.

#### Creating a Webhook Subscription

```json
{
  "name": "Slack Notification",
  "description": "Send notifications to Slack channel",
  "external_url": "https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX",
  "payload_template": {
    "text": "Workflow ${context.workflow.name} completed with status: ${context.execution.status}"
  },
  "headers": {
    "Content-Type": "application/json"
  },
  "auth_type": "none",
  "retry_config": {
    "max_retries": 3,
    "initial_delay": 1.0,
    "max_delay": 60.0,
    "backoff_multiplier": 2.0
  }
}
```

This subscription will send notifications to a Slack webhook when triggered.

#### Triggering Outbound Webhooks

Outbound webhooks can be triggered:

1. **As a task in a workflow**:
```json
{
  "task_id": "notify_slack",
  "component": "webhook",
  "action": "send",
  "input": {
    "subscription_id": "webhook-subscription-id",
    "additional_data": {
      "details": "${tasks.process_data.output.summary}"
    }
  }
}
```

2. **On workflow events**:
```json
{
  "subscription_id": "webhook-subscription-id",
  "event_type": "workflow_completed",
  "filter": "${context.execution.status == 'completed'}"
}
```

## Dynamic Workflows

Harmonia supports dynamic workflows that can adapt their structure at runtime.

### Dynamic Task Generation

Tasks can generate additional tasks during workflow execution:

```json
{
  "task_id": "generate_processing_tasks",
  "component": "workflow_controller",
  "action": "generate_tasks",
  "input": {
    "data_sources": ["source1", "source2", "source3"],
    "task_template": {
      "component": "data_processor",
      "action": "process",
      "input": {
        "source": "${item}"
      }
    }
  }
}
```

This task will generate one processing task for each data source.

### Workflow Composition

Workflows can be composed from other workflows using the workflow reference task:

```json
{
  "task_id": "run_subworkflow",
  "component": "workflow_engine",
  "action": "execute_workflow",
  "input": {
    "workflow_id": "subworkflow-id",
    "input": {
      "param1": "${tasks.previous_task.output.result}"
    }
  }
}
```

This allows for modular workflow design and reusability.

### Task Retry Policies

Tasks can specify custom retry policies for handling transient failures:

```json
{
  "task_id": "unreliable_api_call",
  "component": "api_client",
  "action": "make_request",
  "input": {
    "url": "https://api.example.com/data",
    "method": "POST",
    "data": "${tasks.prepare_data.output.payload}"
  },
  "retry_policy": {
    "max_retries": 5,
    "initial_delay": 1.0,
    "max_delay": 60.0,
    "backoff_multiplier": 2.0,
    "retry_on": ["connection_error", "server_error", "timeout"]
  }
}
```

## Advanced Scheduling

Harmonia supports advanced scheduling features for workflow execution.

### Cron Scheduling

Workflows can be scheduled using cron expressions:

```json
{
  "name": "Daily Data Processing",
  "workflow_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "schedule": "0 0 * * *",  // Run at midnight every day
  "input": {
    "date": "${execution.scheduled_time.format('YYYY-MM-DD')}"
  },
  "enabled": true,
  "timezone": "UTC"
}
```

### Time-Based Triggers

Tasks can be scheduled relative to workflow execution or other events:

```json
{
  "task_id": "delayed_notification",
  "component": "notification",
  "action": "send_email",
  "input": {
    "to": "user@example.com",
    "subject": "Your Report is Ready",
    "body": "Your report has been processed and is ready for download."
  },
  "schedule": {
    "delay": "1h",  // 1 hour delay
    "reference": "workflow_start"  // Relative to workflow start time
  }
}
```

### Execution Windows

Workflows can be restricted to specific execution windows:

```json
{
  "name": "Business Hours Processing",
  "workflow_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "execution_window": {
    "days": ["monday", "tuesday", "wednesday", "thursday", "friday"],
    "hours_start": 9,
    "hours_end": 17,
    "timezone": "America/New_York"
  }
}
```

## Component Communication

Harmonia provides several methods for components to communicate beyond simple task input/output.

### Task Streaming

For long-running tasks that generate incremental results, streaming allows partial results to be processed:

```json
{
  "task_id": "stream_processor",
  "component": "data_processor",
  "action": "process_stream",
  "input": {
    "source": "large_data_feed"
  },
  "streaming": {
    "enabled": true,
    "chunk_size": 1000,
    "target_task": "process_chunk"
  }
}
```

### Event-Based Communication

Components can communicate through events without direct task dependencies:

```json
{
  "task_id": "monitor_processor",
  "component": "event_listener",
  "action": "listen",
  "input": {
    "event_type": "data_processor.progress",
    "timeout": 3600
  }
}
```

### Shared State

Components can share state through the workflow context:

```json
{
  "task_id": "update_shared_state",
  "component": "state_manager",
  "action": "update",
  "input": {
    "key": "processed_count",
    "value": "${context.state.processed_count + tasks.process_batch.output.count}"
  }
}
```

## Advanced Documentation

For more information on these advanced features, refer to the following resources:

- [API Reference](./API_REFERENCE.md) - Detailed API documentation
- [Integration Guide](./INTEGRATION_GUIDE.md) - Guide for integrating with Harmonia
- [Example Workflows](./examples/) - Example workflows demonstrating various features
- [Expression Reference](./docs/expressions.md) - Detailed reference for the expression system
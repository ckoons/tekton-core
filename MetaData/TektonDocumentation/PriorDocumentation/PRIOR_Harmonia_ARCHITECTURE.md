# Harmonia Architecture

## High-Level Architecture Diagram

```
+-------------------------------------------------------+
|                   Harmonia Component                   |
+-------------------------------------------------------+
|                                                       |
|  +-------------------+        +-------------------+   |
|  |     API Layer     |        |      Client       |   |
|  +-------------------+        +-------------------+   |
|  | - HTTP REST API   |        | - Python Client   |   |
|  | - WebSocket API   |<------>| - JS Client       |   |
|  | - SSE Endpoints   |        | - CLI Interface   |   |
|  +-------------------+        +-------------------+   |
|           ^                                           |
|           |                                           |
|           v                                           |
|  +-------------------+        +-------------------+   |
|  |   Core Engine     |        |  Component Registry|  |
|  +-------------------+        +-------------------+   |
|  | - Task Scheduler  |<------>| - Hermes Integration| |
|  | - Dependency Mgmt |        | - Component Adapters| |
|  | - Retry Logic     |        | - Service Discovery | |
|  | - Event System    |        +-------------------+   |
|  +-------------------+                 ^              |
|           ^                            |              |
|           |                            v              |
|           v                  +-------------------+    |
|  +-------------------+       | External Components|   |
|  |   State Manager   |       +-------------------+    |
|  +-------------------+       | - Engram (Memory) |    |
|  | - Checkpoints     |<----->| - Rhetor (LLM)    |    |
|  | - Persistence     |       | - Prometheus      |    |
|  | - Recovery        |       | - Ergon           |    |
|  | - History Tracking|       | - Synthesis       |    |
|  +-------------------+       +-------------------+    |
|                                                       |
+-------------------------------------------------------+
                        ^
                        |
                        v
+-------------------------------------------------------+
|                  Tekton Ecosystem                     |
+-------------------------------------------------------+
```

## Workflow Execution Flow

```
+-------------+     +--------------+     +----------------+
| Client      |     | Harmonia API |     | Workflow Engine|
+-------------+     +--------------+     +----------------+
       |                   |                     |
       | Create Workflow   |                     |
       |------------------>|                     |
       |                   | Store Definition    |
       |                   |-------------------->|
       |                   |                     |
       | Execute Workflow  |                     |
       |------------------>|                     |
       |                   | Initialize Execution|
       |                   |-------------------->|
       |                   |                     |
       |                   |                     | Build Dependency
       |                   |                     | Graph
       |                   |                     |------------+
       |                   |                     |            |
       |                   |                     |<-----------+
       |                   |                     |
       |                   |                     | Execute Root Tasks
       |                   |                     |------------+
       |                   |                     |            |
       |                   |                     |<-----------+
       |                   |                     |
       |                   |                     | Execute Dependent
       |                   |                     | Tasks
       |                   |                     |------------+
       |                   |                     |            |
       |                   |                     |<-----------+
       |                   |                     |
       | Poll Status       |                     | Complete Workflow
       |------------------>|                     |------------+
       |                   | Request Status      |            |
       |                   |-------------------->|            |
       |                   | Return Status       |            |
       |                   |<--------------------|<-----------+
       | Status Response   |                     |
       |<------------------|                     |
       |                   |                     |
```

## Component Integration Model

```
+----------------+     +----------------+     +----------------+
| Client App     |     | Harmonia       |     | Other Component|
+----------------+     +----------------+     +----------------+
       |                      |                      |
       | Create Workflow      |                      |
       | with Component Tasks |                      |
       |--------------------->|                      |
       |                      |                      |
       |                      | Register Capabilities|
       |                      |<-------------------->|
       |                      |                      |
       | Execute Workflow     |                      |
       |--------------------->|                      |
       |                      |                      |
       |                      | Execute Task         |
       |                      |--------------------->|
       |                      |                      |
       |                      | Task Result          |
       |                      |<---------------------|
       |                      |                      |
       | WebSocket/SSE        |                      |
       | Real-time Updates    |                      |
       |<---------------------|                      |
       |                      |                      |
       | Get Final Status     |                      |
       |--------------------->|                      |
       |                      |                      |
       | Status Response      |                      |
       |<---------------------|                      |
       |                      |                      |
```

## State Management and Checkpointing

```
+----------------+     +----------------+     +----------------+
| Workflow Engine|     | State Manager  |     | Storage        |
+----------------+     +----------------+     +----------------+
       |                      |                      |
       | Execute Workflow     |                      |
       |--------------------->|                      |
       |                      |                      |
       |                      | Save Initial State   |
       |                      |--------------------->|
       |                      |                      |
       | Execute Tasks        |                      |
       |------------+         |                      |
       |            |         |                      |
       |<-----------+         |                      |
       |                      |                      |
       | Periodic Checkpoint  |                      |
       |--------------------->|                      |
       |                      | Create Checkpoint    |
       |                      |--------------------->|
       |                      |                      |
       | Task State Update    |                      |
       |--------------------->|                      |
       |                      | Update Task State    |
       |                      |--------------------->|
       |                      |                      |
       | Complete Workflow    |                      |
       |--------------------->|                      |
       |                      | Save Final State     |
       |                      |--------------------->|
       |                      |                      |
```

## Event Propagation System

```
+----------------+     +----------------+     +----------------+
| Workflow Engine|     | Event System   |     | Subscribers    |
+----------------+     +----------------+     +----------------+
       |                      |                      |
       | Task Started         |                      |
       |--------------------->|                      |
       |                      | Notify Subscribers   |
       |                      |--------------------->|
       |                      |                      |
       | Task Completed       |                      |
       |--------------------->|                      |
       |                      | Notify Subscribers   |
       |                      |--------------------->|
       |                      |                      |
       | Workflow Completed   |                      |
       |--------------------->|                      |
       |                      | Notify Subscribers   |
       |                      |--------------------->|
       |                      |                      |
       | Record Event History |                      |
       |--------------------->|                      |
       |                      |                      |
```
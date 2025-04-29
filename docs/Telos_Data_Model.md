# Telos Data Model

This document provides a comprehensive overview of the Telos data model, including entity relationships, attributes, and persistence mechanisms.

## Table of Contents

1. [Overview](#overview)
2. [Core Entities](#core-entities)
   - [Project](#project)
   - [Requirement](#requirement)
   - [Trace](#trace)
   - [Validation](#validation)
3. [Entity Relationships](#entity-relationships)
4. [Data Types](#data-types)
5. [Metadata Structure](#metadata-structure)
6. [History Tracking](#history-tracking)
7. [Data Persistence](#data-persistence)
8. [Data Schemas](#data-schemas)
9. [JSON Representations](#json-representations)
10. [Data Constraints](#data-constraints)
11. [Extension Points](#extension-points)

## Overview

The Telos data model is centered around requirements management, with hierarchical organization of requirements within projects, bidirectional tracing between requirements, and validation of requirement quality. The model is designed to be flexible, extensible, and capable of supporting complex requirement hierarchies and relationships.

## Core Entities

### Project

The Project entity is the top-level container for requirements:

| Attribute | Type | Description | Required |
| --------- | ---- | ----------- | -------- |
| `project_id` | String | Unique identifier for the project (UUID) | Yes |
| `name` | String | Project name | Yes |
| `description` | String | Project description | No |
| `created_at` | Float | Unix timestamp of creation time | Yes |
| `updated_at` | Float | Unix timestamp of last update time | Yes |
| `metadata` | Dictionary | Additional project metadata | No |
| `requirements` | Dictionary | Map of requirement ID to Requirement objects | Yes |

The Project entity is modeled in Python as:

```python
class Project:
    """A project containing requirements."""
    
    def __init__(
        self,
        name: str,
        description: str = "",
        project_id: Optional[str] = None,
        created_at: Optional[float] = None,
        updated_at: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.name = name
        self.description = description
        self.project_id = project_id or str(uuid.uuid4())
        self.created_at = created_at or datetime.now().timestamp()
        self.updated_at = updated_at or self.created_at
        self.metadata = metadata or {}
        self.requirements: Dict[str, Requirement] = {}
```

### Requirement

The Requirement entity represents an individual user requirement:

| Attribute | Type | Description | Required |
| --------- | ---- | ----------- | -------- |
| `requirement_id` | String | Unique identifier for the requirement (UUID) | Yes |
| `title` | String | Short title of the requirement | Yes |
| `description` | String | Detailed description of the requirement | Yes |
| `requirement_type` | String | Type of requirement (functional, non-functional, etc.) | Yes |
| `priority` | String | Priority level (low, medium, high, critical) | Yes |
| `status` | String | Current status (new, in-progress, completed, rejected) | Yes |
| `created_by` | String | ID or name of the creator | No |
| `created_at` | Float | Unix timestamp of creation time | Yes |
| `updated_at` | Float | Unix timestamp of last update time | Yes |
| `tags` | List[String] | List of tags for categorization | No |
| `parent_id` | String | ID of parent requirement if this is a sub-requirement | No |
| `dependencies` | List[String] | IDs of requirements this depends on | No |
| `metadata` | Dictionary | Additional requirement metadata | No |
| `history` | List[Dictionary] | History of changes to the requirement | Yes |

The Requirement entity is modeled in Python as:

```python
class Requirement:
    """A user requirement or goal."""
    
    def __init__(
        self,
        title: str,
        description: str,
        requirement_id: Optional[str] = None,
        requirement_type: str = "functional",
        priority: str = "medium",
        status: str = "new",
        created_by: Optional[str] = None,
        created_at: Optional[float] = None,
        updated_at: Optional[float] = None,
        tags: Optional[List[str]] = None,
        parent_id: Optional[str] = None,
        dependencies: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.title = title
        self.description = description
        self.requirement_id = requirement_id or str(uuid.uuid4())
        self.requirement_type = requirement_type
        self.priority = priority
        self.status = status
        self.created_by = created_by
        self.created_at = created_at or datetime.now().timestamp()
        self.updated_at = updated_at or self.created_at
        self.tags = tags or []
        self.parent_id = parent_id
        self.dependencies = dependencies or []
        self.metadata = metadata or {}
        self.history: List[Dict[str, Any]] = []
        
        # Add the initial state to history
        self._add_history_entry("created", "Requirement created")
```

### Trace

The Trace entity represents a relationship between requirements:

| Attribute | Type | Description | Required |
| --------- | ---- | ----------- | -------- |
| `trace_id` | String | Unique identifier for the trace | Yes |
| `source_id` | String | ID of the source requirement | Yes |
| `target_id` | String | ID of the target requirement | Yes |
| `trace_type` | String | Type of trace relationship | Yes |
| `description` | String | Description of the relationship | No |
| `created_at` | Float | Unix timestamp of creation time | Yes |
| `updated_at` | Float | Unix timestamp of last update time | No |
| `metadata` | Dictionary | Additional trace metadata | No |

Traces are stored within the Project's metadata as a list of trace objects:

```python
# Example trace structure
trace = {
    "trace_id": "trace_123456789",
    "source_id": "req_123",
    "target_id": "req_456",
    "trace_type": "depends_on",
    "description": "Authentication must be implemented before authorization",
    "created_at": 1682456789.123,
    "updated_at": 1682456800.456,
    "metadata": {
        "reviewer": "security-team",
        "approved": True
    }
}
```

### Validation

The Validation entity represents quality assessment for requirements:

| Attribute | Type | Description | Required |
| --------- | ---- | ----------- | -------- |
| `requirement_id` | String | ID of the validated requirement | Yes |
| `title` | String | Title of the requirement (for reference) | Yes |
| `issues` | List[ValidationIssue] | List of identified issues | Yes |
| `passed` | Boolean | Whether the requirement passed validation | Yes |
| `score` | Float | Quality score (0.0-1.0) | No |

```python
# Example validation result
validation_result = {
    "requirement_id": "req_123",
    "title": "User Authentication",
    "issues": [
        {
            "type": "completeness",
            "message": "Description is too short or missing details",
            "severity": "warning",
            "suggestion": "Add more details about authentication methods"
        }
    ],
    "passed": False,
    "score": 0.6
}
```

## Entity Relationships

The relationships between entities in the Telos data model are:

1. **Project to Requirement**: One-to-many relationship
   - A project contains multiple requirements
   - A requirement belongs to exactly one project

2. **Requirement to Requirement (Hierarchy)**:
   - Parent-child relationship through the `parent_id` attribute
   - A requirement can have one parent
   - A requirement can have multiple children

3. **Requirement to Requirement (Dependencies)**:
   - Many-to-many relationship through the `dependencies` list
   - A requirement can depend on multiple requirements
   - A requirement can be depended on by multiple requirements

4. **Requirement to Trace**:
   - Bidirectional relationship
   - A trace connects two requirements (source and target)
   - A requirement can be involved in multiple traces

5. **Requirement to Validation**:
   - One-to-many relationship
   - A requirement can have multiple validation results over time
   - A validation result belongs to exactly one requirement

## Data Types

Telos uses the following data types:

| Data Type | Python Type | Description | Example |
| --------- | ----------- | ----------- | ------- |
| String | `str` | Text values | "User Authentication" |
| Integer | `int` | Whole numbers | 42 |
| Float | `float` | Decimal numbers, used for timestamps | 1682456789.123 |
| Boolean | `bool` | True/False values | True |
| List | `list` | Ordered collections | ["tag1", "tag2"] |
| Dictionary | `dict` | Key-value collections | {"key": "value"} |
| UUID | `str` | Universally unique identifiers stored as strings | "550e8400-e29b-41d4-a716-446655440000" |
| Timestamp | `float` | Unix timestamps (seconds since epoch) | 1682456789.123 |

## Metadata Structure

Both Project and Requirement entities support flexible metadata:

```python
# Project metadata example
project_metadata = {
    "priority": "high",
    "deadline": "2025-12-31",
    "stakeholders": ["Product Team", "Engineering"],
    "status": "active",
    "owner": "project-manager-1",
    "traces": [
        # List of trace objects
    ],
    "plans": [
        # List of plan objects
    ]
}

# Requirement metadata example
requirement_metadata = {
    "source": "User Interview",
    "complexity": "medium",
    "effort_estimate": "3 days",
    "reviewer": "senior-engineer",
    "clarifications": [
        {
            "question": "What authentication methods are required?",
            "answer": "OAuth2 and username/password",
            "timestamp": 1682457000.123
        }
    ]
}
```

## History Tracking

Requirements maintain a history of changes:

```python
# Example history entry
history_entry = {
    "timestamp": 1682456789.123,
    "action": "updated",
    "description": "Updated attributes: title, priority -> high"
}
```

The history is captured automatically when changes are made:

```python
def _add_history_entry(self, action: str, description: str) -> None:
    """Add an entry to the requirement history."""
    self.history.append({
        "timestamp": datetime.now().timestamp(),
        "action": action,
        "description": description
    })

def update(self, **kwargs) -> None:
    """Update requirement attributes."""
    changes = []
    for key, value in kwargs.items():
        if hasattr(self, key) and getattr(self, key) != value:
            old_value = getattr(self, key)
            setattr(self, key, value)
            changes.append(f"{key}: {old_value} -> {value}")
    
    if changes:
        self.updated_at = datetime.now().timestamp()
        self._add_history_entry("updated", "Updated attributes: " + ", ".join(changes))
```

## Data Persistence

Telos uses a file-based persistence system for storing projects and requirements:

### Storage Directory

The storage directory is configured with the `TELOS_STORAGE_DIR` environment variable:

```python
storage_dir = os.environ.get("TELOS_STORAGE_DIR", os.path.join(os.getcwd(), "data", "requirements"))
```

### File Format

Projects are stored as JSON files, with one file per project. The filename is the project ID:

```
{storage_dir}/{project_id}.json
```

### Saving Projects

Projects are serialized and saved to disk:

```python
def _save_project(self, project: Project) -> None:
    """Save a project to disk."""
    if not self.storage_dir:
        return
    
    os.makedirs(self.storage_dir, exist_ok=True)
    file_path = os.path.join(self.storage_dir, f"{project.project_id}.json")
    
    with open(file_path, 'w') as f:
        json.dump(project.to_dict(), f, indent=2)
```

### Loading Projects

Projects are loaded from disk during initialization:

```python
def load_projects(self) -> None:
    """Load all projects from the storage directory."""
    if not self.storage_dir or not os.path.exists(self.storage_dir):
        logger.warning(f"Storage directory {self.storage_dir} does not exist")
        return
    
    for filename in os.listdir(self.storage_dir):
        if not filename.endswith('.json'):
            continue
        
        file_path = os.path.join(self.storage_dir, filename)
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            project = Project.from_dict(data)
            self.projects[project.project_id] = project
            logger.info(f"Loaded project {project.project_id}: {project.name}")
        except Exception as e:
            logger.error(f"Error loading project from {file_path}: {e}")
```

## Data Schemas

### Project Schema

```json
{
  "project_id": "string",
  "name": "string",
  "description": "string",
  "created_at": "number",
  "updated_at": "number",
  "metadata": {
    "additionalProperties": true
  },
  "requirements": {
    "additionalProperties": {
      "$ref": "#/definitions/Requirement"
    }
  }
}
```

### Requirement Schema

```json
{
  "requirement_id": "string",
  "title": "string",
  "description": "string",
  "requirement_type": "string",
  "priority": "string",
  "status": "string",
  "created_by": "string",
  "created_at": "number",
  "updated_at": "number",
  "tags": [
    "string"
  ],
  "parent_id": "string",
  "dependencies": [
    "string"
  ],
  "metadata": {
    "additionalProperties": true
  },
  "history": [
    {
      "timestamp": "number",
      "action": "string",
      "description": "string"
    }
  ]
}
```

### Trace Schema

```json
{
  "trace_id": "string",
  "source_id": "string",
  "target_id": "string",
  "trace_type": "string",
  "description": "string",
  "created_at": "number",
  "updated_at": "number",
  "metadata": {
    "additionalProperties": true
  }
}
```

### Validation Schema

```json
{
  "requirement_id": "string",
  "title": "string",
  "issues": [
    {
      "type": "string",
      "message": "string",
      "severity": "string",
      "suggestion": "string"
    }
  ],
  "passed": "boolean",
  "score": "number"
}
```

## JSON Representations

### Project JSON

```json
{
  "project_id": "project-1",
  "name": "Authentication System",
  "description": "User authentication and authorization system",
  "created_at": 1682456789.123,
  "updated_at": 1682457000.456,
  "metadata": {
    "priority": "high",
    "deadline": "2025-12-31",
    "stakeholders": ["Product", "Engineering"]
  },
  "requirements": {
    "req-1": {
      "requirement_id": "req-1",
      "title": "User Authentication",
      "description": "The system must authenticate users with username and password.",
      "requirement_type": "functional",
      "priority": "high",
      "status": "new",
      "created_by": "user-1",
      "created_at": 1682456800.123,
      "updated_at": 1682456800.123,
      "tags": ["security", "user-management"],
      "parent_id": null,
      "dependencies": [],
      "metadata": {
        "source": "Product Team",
        "complexity": "medium"
      },
      "history": [
        {
          "timestamp": 1682456800.123,
          "action": "created",
          "description": "Requirement created"
        }
      ]
    },
    "req-2": {
      "requirement_id": "req-2",
      "title": "User Authorization",
      "description": "The system must authorize users based on their roles.",
      "requirement_type": "functional",
      "priority": "high",
      "status": "new",
      "created_by": "user-1",
      "created_at": 1682456900.456,
      "updated_at": 1682456900.456,
      "tags": ["security", "user-management"],
      "parent_id": null,
      "dependencies": ["req-1"],
      "metadata": {
        "source": "Product Team",
        "complexity": "high"
      },
      "history": [
        {
          "timestamp": 1682456900.456,
          "action": "created",
          "description": "Requirement created"
        }
      ]
    }
  }
}
```

### Requirement JSON

```json
{
  "requirement_id": "req-1",
  "title": "User Authentication",
  "description": "The system must authenticate users with username and password.",
  "requirement_type": "functional",
  "priority": "high",
  "status": "new",
  "created_by": "user-1",
  "created_at": 1682456800.123,
  "updated_at": 1682456800.123,
  "tags": ["security", "user-management"],
  "parent_id": null,
  "dependencies": [],
  "metadata": {
    "source": "Product Team",
    "complexity": "medium"
  },
  "history": [
    {
      "timestamp": 1682456800.123,
      "action": "created",
      "description": "Requirement created"
    }
  ]
}
```

## Data Constraints

The following constraints apply to the Telos data model:

1. **Uniqueness Constraints**:
   - Project IDs must be unique across all projects
   - Requirement IDs must be unique within a project
   - Trace IDs must be unique within a project

2. **Referential Integrity Constraints**:
   - `parent_id` must reference a valid requirement ID in the same project
   - Each ID in `dependencies` must reference a valid requirement ID in the same project
   - `source_id` and `target_id` in traces must reference valid requirement IDs in the same project

3. **Value Constraints**:
   - `requirement_type` should be one of: "functional", "non-functional", "constraint", etc.
   - `priority` should be one of: "low", "medium", "high", "critical"
   - `status` should be one of: "new", "in-progress", "completed", "rejected"
   - `trace_type` should be one of: "depends_on", "implements", "refines", "conflicts_with", etc.

4. **Required Fields**:
   - Project: `name`, `project_id`
   - Requirement: `title`, `description`, `requirement_id`
   - Trace: `source_id`, `target_id`, `trace_type`, `trace_id`

## Extension Points

The Telos data model provides several extension points:

1. **Metadata**:
   - Both Project and Requirement entities include a flexible `metadata` dictionary
   - This can be used to store custom data not covered by the core model

2. **Custom Requirement Types**:
   - The `requirement_type` field can be extended with custom types
   - Examples might include: "security", "performance", "usability", etc.

3. **Custom Trace Types**:
   - The `trace_type` field can be extended with custom relationship types
   - Examples might include: "similar_to", "alternative_to", "derived_from", etc.

4. **Custom History Actions**:
   - The `action` field in history entries can be extended
   - Examples might include: "reviewed", "approved", "rejected", etc.

5. **Tags**:
   - The `tags` list can be used for custom categorization
   - Tags are free-form strings that can be used for filtering and grouping
# Telos Data Model

This document provides a detailed description of the Telos data model, including the structure of projects, requirements, traces, and other entities in the system.

## Core Entities

### Project

The Project entity represents a collection of related requirements. It serves as the top-level container for requirements management.

#### Attributes

| Attribute     | Type      | Description                                        | Required |
|---------------|-----------|----------------------------------------------------| -------- |
| project_id    | String    | Unique identifier for the project                  | Yes      |
| name          | String    | Human-readable name for the project                | Yes      |
| description   | String    | Detailed description of the project                | No       |
| created_at    | Timestamp | When the project was created                       | Yes      |
| updated_at    | Timestamp | When the project was last updated                  | Yes      |
| metadata      | Object    | Arbitrary key-value pairs for project metadata     | No       |
| requirements  | Object    | Map of requirement IDs to Requirement objects      | Yes      |

#### Example

```json
{
  "project_id": "project-123",
  "name": "User Authentication System",
  "description": "Implementation of the authentication system for the application",
  "created_at": 1650000000,
  "updated_at": 1650001000,
  "metadata": {
    "priority": "high",
    "category": "security",
    "status": "in_progress"
  },
  "requirements": {
    "req-1": { /* Requirement object */ },
    "req-2": { /* Requirement object */ }
  }
}
```

### Requirement

The Requirement entity represents a single requirement within a project. It defines a specific capability, constraint, or property the system must have.

#### Attributes

| Attribute        | Type      | Description                                             | Required |
|------------------|-----------|--------------------------------------------------------| -------- |
| requirement_id   | String    | Unique identifier for the requirement                   | Yes      |
| title            | String    | Short, descriptive title                               | Yes      |
| description      | String    | Detailed description of the requirement                | Yes      |
| requirement_type | String    | Type of requirement (functional, non-functional, etc.) | Yes      |
| priority         | String    | Priority level (low, medium, high, critical)           | No       |
| status           | String    | Current status (new, in_progress, completed, etc.)     | Yes      |
| tags             | String[]  | Array of tags for categorization                       | No       |
| parent_id        | String    | ID of parent requirement (for hierarchy)               | No       |
| dependencies     | String[]  | IDs of requirements this one depends on                | No       |
| created_at       | Timestamp | When the requirement was created                       | Yes      |
| updated_at       | Timestamp | When the requirement was last updated                  | Yes      |
| created_by       | String    | User who created the requirement                       | No       |
| metadata         | Object    | Arbitrary key-value pairs for requirement metadata     | No       |
| history          | Object[]  | Array of historical changes                            | Yes      |

#### Example

```json
{
  "requirement_id": "req-1",
  "title": "User Authentication",
  "description": "The system shall authenticate users with a username and password. Passwords must be at least 8 characters long and include at least one number and one special character.",
  "requirement_type": "functional",
  "priority": "high",
  "status": "in_progress",
  "tags": ["security", "user", "authentication"],
  "parent_id": null,
  "dependencies": ["req-5", "req-7"],
  "created_at": 1650002000,
  "updated_at": 1650003000,
  "created_by": "jane.doe",
  "metadata": {
    "acceptance_criteria": "User can sign in with valid credentials and cannot sign in with invalid credentials",
    "effort_estimate": "medium",
    "implementation_notes": "Use industry-standard password hashing"
  },
  "history": [
    {
      "action": "created",
      "timestamp": 1650002000,
      "user": "jane.doe"
    },
    {
      "action": "updated",
      "timestamp": 1650003000,
      "user": "jane.doe",
      "changes": {
        "description": "Added password requirements"
      }
    }
  ]
}
```

### Trace

The Trace entity represents a relationship between requirements. It enables bidirectional tracing for impact analysis and requirement relationships.

#### Attributes

| Attribute     | Type      | Description                                        | Required |
|---------------|-----------|----------------------------------------------------| -------- |
| trace_id      | String    | Unique identifier for the trace                    | Yes      |
| source_id     | String    | ID of the source requirement                       | Yes      |
| target_id     | String    | ID of the target requirement                       | Yes      |
| trace_type    | String    | Type of trace relationship                         | Yes      |
| description   | String    | Description of the relationship                    | No       |
| created_at    | Timestamp | When the trace was created                         | Yes      |
| updated_at    | Timestamp | When the trace was last updated                    | No       |
| metadata      | Object    | Arbitrary key-value pairs for trace metadata       | No       |

#### Example

```json
{
  "trace_id": "trace_1650004000",
  "source_id": "req-1",
  "target_id": "req-2",
  "trace_type": "depends-on",
  "description": "Authentication must be completed before authorization",
  "created_at": 1650004000,
  "updated_at": 1650005000,
  "metadata": {
    "criticality": "high",
    "verified_by": "john.smith"
  }
}
```

### Validation Result

The Validation Result entity represents the outcome of validating a requirement or project against quality criteria.

#### Attributes

| Attribute     | Type      | Description                                        | Required |
|---------------|-----------|----------------------------------------------------| -------- |
| validation_id | String    | Unique identifier for the validation               | Yes      |
| project_id    | String    | ID of the project being validated                  | Yes      |
| timestamp     | Timestamp | When the validation was performed                  | Yes      |
| criteria      | Object    | Criteria used for validation                       | Yes      |
| results       | Object[]  | Array of individual requirement validation results | Yes      |
| summary       | Object    | Summary statistics of validation                   | Yes      |

#### Example

```json
{
  "validation_id": "val_1650006000",
  "project_id": "project-123",
  "timestamp": 1650006000,
  "criteria": {
    "check_completeness": true,
    "check_clarity": true,
    "check_verifiability": true
  },
  "results": [
    {
      "requirement_id": "req-1",
      "title": "User Authentication",
      "issues": [
        {
          "type": "verifiability",
          "message": "Requirement may not be easily verifiable"
        }
      ],
      "passed": false
    },
    {
      "requirement_id": "req-2",
      "title": "User Authorization",
      "issues": [],
      "passed": true
    }
  ],
  "summary": {
    "total_requirements": 2,
    "passed": 1,
    "failed": 1,
    "pass_percentage": 50
  }
}
```

## Relationships

The following diagram illustrates the relationships between the core entities:

```
Project
   │
   ├─── Requirements (1:many)
   │      │
   │      ├─── Parent-Child Relationships (1:many)
   │      │
   │      └─── Dependencies (many:many)
   │
   ├─── Traces (1:many)
   │      │
   │      ├─── Source Requirement (1:1)
   │      │
   │      └─── Target Requirement (1:1)
   │
   └─── Validation Results (1:many)
```

## Hierarchical Model

Requirements can be organized in a hierarchical structure using parent-child relationships:

```
Project
   │
   ├─── Epic Requirement
   │      │
   │      ├─── Feature Requirement 1
   │      │      │
   │      │      ├─── User Story 1
   │      │      │
   │      │      └─── User Story 2
   │      │
   │      └─── Feature Requirement 2
   │             │
   │             └─── User Story 3
   │
   └─── Non-functional Requirement
```

## Data Persistence

Telos implements a file-based persistence model with the following structure:

```
~/.tekton/data/telos/
   │
   └─── requirements/
          │
          └─── project_<id>/
                 │
                 ├─── project.json   # Project metadata
                 │
                 └─── requirements/  # Individual requirement files
                        │
                        ├─── req_<id1>.json
                        │
                        ├─── req_<id2>.json
                        │
                        └─── ...
```

## Enumerations

### Requirement Types

- `functional`: Describes a specific system behavior or capability
- `non-functional`: Describes quality attributes or constraints
- `business`: Describes business rules or constraints
- `user`: Describes user interactions or expectations
- `interface`: Describes system interfaces or integrations
- `constraint`: Describes limitations or boundaries
- `performance`: Describes performance characteristics
- `security`: Describes security requirements
- `usability`: Describes usability requirements

### Requirement Priorities

- `critical`: Essential for system functionality
- `high`: Important for system functionality
- `medium`: Desirable but not critical
- `low`: Nice to have

### Requirement Statuses

- `new`: Newly created requirement
- `in_progress`: Requirement is being worked on
- `completed`: Requirement has been implemented
- `verified`: Requirement has been verified against acceptance criteria
- `rejected`: Requirement has been rejected
- `deferred`: Requirement has been postponed

### Trace Types

- `depends-on`: Source depends on target
- `implements`: Source implements target
- `refines`: Source provides more detail about target
- `affects`: Changes to source affect target
- `constrains`: Source constrains target
- `conflicts-with`: Source conflicts with target
- `related-to`: Source is related to target in some way
- `derived-from`: Source is derived from target

## Data Validation

Telos validates all data against these rules:

### Project Validation

- `name`: Required, string, 3-100 characters
- `description`: Optional, string, 0-2000 characters
- `metadata`: Optional, object with string keys and any values

### Requirement Validation

- `title`: Required, string, 3-100 characters
- `description`: Required, string, 10-10000 characters
- `requirement_type`: Required, one of the enumerated types
- `priority`: Optional, one of the enumerated priorities
- `status`: Required, one of the enumerated statuses
- `tags`: Optional, array of strings
- `parent_id`: Optional, must reference an existing requirement
- `dependencies`: Optional, array of strings referencing existing requirements

### Trace Validation

- `source_id`: Required, must reference an existing requirement
- `target_id`: Required, must reference an existing requirement
- `trace_type`: Required, one of the enumerated trace types
- `description`: Optional, string, 0-1000 characters

## Schema Evolution

As the Telos data model evolves, these strategies ensure backward compatibility:

1. **Additive Changes**: New fields are added as optional
2. **Field Deprecation**: Fields are marked deprecated before removal
3. **Version Tracking**: Data includes schema version information
4. **Migration Utilities**: Tools are provided for data migration
5. **Default Values**: Sensible defaults are used for missing fields

## Extensions

The Telos data model can be extended through:

### Custom Metadata

Both projects and requirements support arbitrary metadata as key-value pairs:

```json
"metadata": {
  "domain": "finance",
  "regulatory_compliance": ["GDPR", "PCI-DSS"],
  "stakeholders": ["Finance Team", "Security Team"],
  "custom_field": "custom value"
}
```

### Custom Requirement Attributes

Projects can define custom requirement attributes through the project metadata:

```json
"metadata": {
  "custom_requirement_attributes": [
    {
      "name": "compliance_requirements",
      "type": "array",
      "description": "List of compliance requirements this satisfies"
    },
    {
      "name": "test_coverage",
      "type": "number",
      "description": "Percentage of test coverage for this requirement"
    }
  ]
}
```

### Custom Validation Rules

Projects can define custom validation rules through the project metadata:

```json
"metadata": {
  "validation_rules": [
    {
      "name": "security_keywords",
      "description": "Security requirements must mention encryption or authentication",
      "applies_to": "requirement_type:security",
      "rule": "contains_any_keywords:['encrypt', 'authenticate', 'secure']"
    }
  ]
}
```

## Integrations

### Prometheus Integration

Telos integrates with Prometheus by providing requirement data for planning:

```json
{
  "project": {
    "project_id": "project-123",
    "name": "User Authentication System"
  },
  "requirements": [
    {
      "requirement_id": "req-1",
      "title": "User Authentication",
      "description": "...",
      "priority": "high",
      "status": "in_progress",
      "effort_estimate": "medium"
    }
  ],
  "dependencies": [
    {
      "source_id": "req-1",
      "target_id": "req-2",
      "trace_type": "depends-on"
    }
  ]
}
```

### Rhetor Integration

Telos integrates with Rhetor for LLM-powered requirement analysis:

```json
{
  "requirement": {
    "requirement_id": "req-1",
    "title": "User Authentication",
    "description": "...",
    "requirement_type": "functional"
  },
  "analysis_type": "quality_assessment"
}
```

## Implementation Details

### Project Class

The `Project` class provides these key methods:

- `add_requirement`: Add a new requirement to the project
- `get_requirement`: Get a requirement by ID
- `update_requirement`: Update an existing requirement
- `delete_requirement`: Delete a requirement
- `get_all_requirements`: Get all requirements with optional filtering
- `get_requirement_hierarchy`: Get the hierarchical structure of requirements
- `add_trace`: Add a trace between requirements
- `get_traces`: Get traces for a requirement
- `to_dict`: Convert project to dictionary representation
- `from_dict`: Create project from dictionary representation

### Requirement Class

The `Requirement` class provides these key methods:

- `validate`: Validate the requirement against criteria
- `add_dependency`: Add a dependency on another requirement
- `remove_dependency`: Remove a dependency
- `add_history_entry`: Add an entry to the requirement history
- `to_dict`: Convert requirement to dictionary representation
- `from_dict`: Create requirement from dictionary representation

### RequirementsManager Class

The `RequirementsManager` class provides these key methods:

- `create_project`: Create a new project
- `get_project`: Get a project by ID
- `update_project`: Update an existing project
- `delete_project`: Delete a project
- `get_all_projects`: Get all projects
- `add_requirement`: Add a requirement to a project
- `get_requirement`: Get a requirement by ID
- `update_requirement`: Update an existing requirement
- `delete_requirement`: Delete a requirement
- `validate_project`: Validate all requirements in a project
- `export_project`: Export a project to various formats
- `import_project`: Import a project from various formats

## API Contracts

The Telos API adheres to these data contracts:

### Project API

- GET `/api/projects` returns an array of project summaries
- GET `/api/projects/{id}` returns a complete project with requirements
- POST `/api/projects` creates a new project from request body
- PUT `/api/projects/{id}` updates a project from request body
- DELETE `/api/projects/{id}` deletes a project

### Requirement API

- GET `/api/projects/{id}/requirements` returns an array of requirements
- GET `/api/projects/{id}/requirements/{req_id}` returns a specific requirement
- POST `/api/projects/{id}/requirements` creates a new requirement
- PUT `/api/projects/{id}/requirements/{req_id}` updates a requirement
- DELETE `/api/projects/{id}/requirements/{req_id}` deletes a requirement

## Sample Code

### Creating a Project and Requirements

```python
# Create a requirements manager
manager = RequirementsManager(storage_dir="/path/to/storage")

# Create a new project
project_id = manager.create_project(
    name="User Management System",
    description="System for managing users and their permissions"
)

# Get the project
project = manager.get_project(project_id)

# Add requirements
req1_id = manager.add_requirement(
    project_id=project_id,
    title="User Authentication",
    description="The system shall authenticate users with username and password",
    requirement_type="functional",
    priority="high"
)

req2_id = manager.add_requirement(
    project_id=project_id,
    title="User Authorization",
    description="The system shall authorize users based on their roles",
    requirement_type="functional",
    priority="high",
    dependencies=[req1_id]  # Authorization depends on authentication
)

# Create a parent-child relationship
req3_id = manager.add_requirement(
    project_id=project_id,
    title="Password Requirements",
    description="Passwords must be at least 8 characters long",
    requirement_type="functional",
    priority="medium",
    parent_id=req1_id  # Child of authentication
)
```

## Best Practices

1. **Use unique IDs**: Ensure all entities have unique identifiers
2. **Validate input**: Validate all data against the schema before storage
3. **Maintain history**: Keep a history of changes to requirements
4. **Use appropriate types**: Follow the enumerated types for consistency
5. **Create meaningful traces**: Use appropriate trace types for relationships
6. **Keep metadata structured**: Use consistent structure for metadata
7. **Follow hierarchy**: Use parent-child relationships for logical organization
8. **Document dependencies**: Use dependencies to track relationships
9. **Validate regularly**: Run validation to ensure high-quality requirements
10. **Export for backup**: Export projects regularly for backup

## Conclusion

The Telos data model provides a flexible, extensible foundation for requirements management within the Tekton ecosystem. It supports hierarchical organization, bidirectional tracing, and comprehensive validation to ensure high-quality requirements.
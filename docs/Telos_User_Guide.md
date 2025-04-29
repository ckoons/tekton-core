# Telos User Guide

## Table of Contents
1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Projects](#projects)
4. [Requirements](#requirements)
5. [Requirement Management](#requirement-management)
6. [Requirement Hierarchy](#requirement-hierarchy)
7. [Requirement Tracing](#requirement-tracing)
8. [Requirement Validation](#requirement-validation)
9. [Requirement Refinement](#requirement-refinement)
10. [Planning Integration](#planning-integration)
11. [Export and Import](#export-and-import)
12. [CLI Usage](#cli-usage)
13. [API Usage](#api-usage)
14. [WebSocket Integration](#websocket-integration)
15. [Troubleshooting](#troubleshooting)

## Introduction

Telos is the comprehensive requirements management and tracing system for the Tekton ecosystem. It provides an intuitive platform for documenting, organizing, tracking, and validating project requirements with support for hierarchical visualization and bidirectional tracing.

This guide will walk you through using Telos, from basic requirement management to advanced features like requirement validation, tracing, and planning integration.

## Getting Started

### Installation

Telos can be installed as part of the Tekton ecosystem or as a standalone component:

```bash
# Install with Tekton installer
./tekton-install.sh --components telos

# Or install from source
cd Tekton/Telos
pip install -e .
```

### Starting Telos

You can start Telos using the Tekton launcher or directly:

```bash
# Start with Tekton
./scripts/tekton-launch --components telos

# Or start directly
python -m telos.api.app
```

### Accessing Telos

Once started, Telos is available at:

- **UI**: Through the Hephaestus UI at http://localhost:8080
- **API**: Directly at http://localhost:8008/api
- **WebSocket**: At ws://localhost:8008/ws

## Projects

Projects are the top-level organizational units in Telos, containing related requirements.

### Creating a Project

To create a project using the UI:

1. Open the Telos component in Hephaestus UI
2. Click the "New Project" button
3. Enter project name and description
4. Click "Create Project"

To create a project using the CLI:

```bash
telos project create --name "My Project" --description "Project description"
```

### Managing Projects

From the UI, you can:
- View all projects in the left sidebar
- Click on a project to view its requirements
- Edit a project by selecting it and clicking the settings icon
- Delete a project by selecting it and using the delete action

## Requirements

Requirements are the core entities of Telos, representing individual project needs or constraints.

### Requirement Types

Telos supports different types of requirements:
- **Functional**: What the system should do
- **Non-Functional**: How the system should perform
- **Constraint**: Limitations or boundaries

### Requirement Attributes

Each requirement includes:
- **Title**: Short descriptive name
- **Description**: Detailed explanation
- **Type**: Functional, non-functional, constraint, etc.
- **Priority**: Critical, high, medium, low
- **Status**: New, in-progress, completed, rejected
- **Tags**: For categorization
- **Parent/Child Relationships**: For hierarchical organization
- **Dependencies**: Other requirements this one depends on

## Requirement Management

### Creating Requirements

To create a requirement using the UI:

1. Select a project
2. Click "Add Requirement"
3. Fill in the required fields (title, description)
4. Set the type, priority, and other attributes
5. Click "Create Requirement"

To create a requirement using the CLI:

```bash
telos requirement add --project-id my-project-id --title "User Authentication" --description "The system must authenticate users with username and password" --priority high --type functional
```

### Viewing Requirements

Telos offers multiple views for requirements:
- **List View**: Table format with all requirements
- **Board View**: Kanban-style view organized by status
- **Hierarchy View**: Tree view showing parent-child relationships
- **Trace View**: Visualizes traces between requirements

To switch views, use the "View" dropdown in the requirements interface.

### Filtering Requirements

You can filter requirements by:
- **Status**: New, in-progress, completed, rejected
- **Type**: Functional, non-functional, constraint
- **Priority**: Critical, high, medium, low
- **Search**: Full-text search across titles and descriptions

### Editing Requirements

To edit a requirement:

1. Select the requirement in any view
2. View the requirement details
3. Click "Edit" to modify fields
4. Save your changes

## Requirement Hierarchy

Telos supports hierarchical relationships between requirements.

### Creating Hierarchies

To establish a parent-child relationship:

1. When creating a new requirement, select a parent from the dropdown
2. Or edit an existing requirement and set its parent

### Viewing Hierarchies

The hierarchy view displays requirements in a tree structure:

1. Select "Hierarchy" from the View dropdown
2. Expand/collapse nodes to navigate the hierarchy
3. Click on any requirement to view its details

## Requirement Tracing

Tracing connects related requirements for impact analysis.

### Creating Traces

To create a trace between requirements:

1. Navigate to a requirement's details
2. Select the "Traces" tab
3. Click "Create Trace"
4. Select the target requirement and trace type
5. Add an optional description and click "Create"

### Viewing Traces

To view traces:

1. From a requirement's details, select the "Traces" tab
2. Or use the "Trace View" to visualize all traces in the project

### Trace Types

Common trace types include:
- **Depends On**: This requirement depends on the target
- **Implements**: This requirement implements the target
- **Refines**: This requirement refines the target
- **Conflicts With**: This requirement conflicts with the target

## Requirement Validation

Telos can automatically validate requirements for quality.

### Running Validation

To validate requirements:

1. Select a project or individual requirement
2. Click "Validate"
3. Select validation criteria
4. View the validation results

### Validation Criteria

Telos checks requirements against:
- **Completeness**: Is the requirement fully specified?
- **Clarity**: Is the requirement clear and unambiguous?
- **Verifiability**: Can the requirement be verified?
- **Consistency**: Is the requirement consistent with others?
- **Feasibility**: Is the requirement achievable?

### Validation Results

Validation results include:
- **Overall Score**: Quality score from 0-10
- **Issues**: Specific problems detected
- **Suggestions**: Recommendations for improvement

## Requirement Refinement

Telos can help refine requirements using LLM integration.

### Refining Requirements

To refine a requirement:

1. Select a requirement
2. Click "Refine"
3. Provide feedback or select automatic refinement
4. Review the suggestions
5. Apply the changes if desired

### Refinement Features

Refinement can help with:
- **Clarity**: Improving wording for clarity
- **Completeness**: Adding missing details
- **Precision**: Making vague requirements more specific
- **Consistency**: Aligning with project terminology

## Planning Integration

Telos integrates with Prometheus for planning.

### Preparing for Planning

To prepare requirements for planning:

1. Select a project
2. Click "Analyze" under planning options
3. Review the readiness assessment
4. Address any issues with requirements that need refinement

### Creating a Plan

To create a plan:

1. Ensure requirements are ready for planning
2. Click "Create Plan"
3. Review the generated plan
4. Export or integrate with Prometheus for detailed planning

## Export and Import

Telos supports exporting and importing requirements.

### Exporting

To export a project:

1. Select a project
2. Click "Export"
3. Choose the export format (JSON, Markdown)
4. Select sections to include
5. Download the export file

### Importing

To import a project:

1. Click "Import"
2. Upload a JSON or Markdown file
3. Select import options
4. Review and confirm the import

## CLI Usage

Telos provides a comprehensive CLI for requirement management.

### Project Management

```bash
# Create a project
telos project create --name "My Project" --description "Project description"

# List all projects
telos project list

# Show project details
telos project show --project-id my-project-id

# Delete a project
telos project delete --project-id my-project-id
```

### Requirement Management

```bash
# Add a requirement
telos requirement add --project-id my-project-id --title "User Authentication" --description "Description..."

# List requirements
telos requirement list --project-id my-project-id

# Show requirement details
telos requirement show --project-id my-project-id --requirement-id req-id

# Update a requirement
telos requirement update --project-id my-project-id --requirement-id req-id --title "New Title"

# Delete a requirement
telos requirement delete --project-id my-project-id --requirement-id req-id
```

### Validation and Refinement

```bash
# Validate requirements
telos validate --project-id my-project-id

# Refine a requirement
telos refine requirement --project-id my-project-id --requirement-id req-id
```

### Planning Integration

```bash
# Analyze requirements for planning
telos refine analyze --project-id my-project-id

# Create a plan
telos plan create --project-id my-project-id
```

## API Usage

Telos provides a RESTful API for programmatic interaction.

### Project Operations

```python
import requests

# Base URL
base_url = "http://localhost:8008"

# Create a project
response = requests.post(f"{base_url}/api/projects", json={
    "name": "API Project",
    "description": "Created via API"
})
project_id = response.json()["project_id"]

# Get project details
response = requests.get(f"{base_url}/api/projects/{project_id}")
project = response.json()
```

### Requirement Operations

```python
# Add a requirement
response = requests.post(f"{base_url}/api/projects/{project_id}/requirements", json={
    "title": "API Feature",
    "description": "This requirement was created via the API",
    "requirement_type": "functional",
    "priority": "high"
})
requirement_id = response.json()["requirement_id"]

# Update a requirement
response = requests.put(f"{base_url}/api/projects/{project_id}/requirements/{requirement_id}", json={
    "status": "in-progress"
})
```

### Validation and Refinement

```python
# Validate a requirement
response = requests.post(f"{base_url}/api/projects/{project_id}/requirements/{requirement_id}/validate", json={
    "criteria": {
        "check_completeness": True,
        "check_verifiability": True,
        "check_clarity": True
    }
})

# Refine a requirement
response = requests.post(f"{base_url}/api/projects/{project_id}/requirements/{requirement_id}/refine", json={
    "feedback": "This requirement should be more specific about the authentication method",
    "auto_update": False
})
```

## WebSocket Integration

Telos provides WebSocket integration for real-time updates.

### Connecting to WebSocket

```javascript
// Connect to WebSocket
const ws = new WebSocket("ws://localhost:8008/ws");

// Listen for messages
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log("Received:", data);
};

// Register client
ws.send(JSON.stringify({
    type: "REGISTER",
    source: "client",
    target: "server",
    timestamp: Date.now(),
    payload: {}
}));

// Subscribe to project updates
ws.send(JSON.stringify({
    type: "PROJECT_SUBSCRIBE",
    source: "client",
    target: "server",
    timestamp: Date.now(),
    payload: {
        project_id: "your-project-id"
    }
}));
```

### WebSocket Events

Telos sends the following events via WebSocket:
- **Project updates**: When a project is created, updated, or deleted
- **Requirement updates**: When a requirement is created, updated, or deleted
- **Trace updates**: When a trace is created, updated, or deleted
- **Validation results**: When validation is completed
- **Refinement results**: When refinement is completed

## Troubleshooting

### Common Issues

#### Connection Issues

If you can't connect to Telos:
1. Ensure the Telos service is running
2. Check that port 8008 is available and not blocked by a firewall
3. Verify that environment variables are correctly set

#### API Errors

Common API error responses:
- **404 Not Found**: Resource (project/requirement) doesn't exist
- **400 Bad Request**: Invalid input data
- **503 Service Unavailable**: Requirements manager not initialized

#### UI Issues

If the UI doesn't load or behave correctly:
1. Check browser console for JavaScript errors
2. Verify that all required scripts are loading
3. Try clearing browser cache and reloading

### Getting Help

If you encounter issues:
1. Check the logs for error messages
2. Refer to the technical documentation
3. File an issue in the Tekton repository
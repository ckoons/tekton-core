# Telos User Guide

This guide provides comprehensive information on using the Telos requirements management system within Tekton.

## Overview

Telos is a requirements management, tracing, and validation system designed to provide a robust platform for documenting, organizing, tracking, and validating project requirements. It supports hierarchical visualization and bidirectional tracing to help teams create high-quality requirements that can be effectively planned and implemented.

## Getting Started

### Accessing Telos

Telos can be accessed through multiple interfaces:

1. **Web UI**: Access the Telos component in the Hephaestus UI system at http://localhost:8080
2. **API**: Interact programmatically with Telos at http://localhost:8008
3. **CLI**: Use the command-line interface for requirement management

### Installation

If you haven't installed Telos yet:

```bash
# Clone the repository
git clone https://github.com/example/tekton.git
cd tekton/Telos

# Install Telos and its dependencies
./setup.sh
```

### Starting Telos

You can start Telos in several ways:

```bash
# Start Telos API server only
telos-api

# Start with Tekton (recommended)
./scripts/tekton-launch --components telos

# Register with Hermes (if running separately)
python register_with_hermes.py
```

## Using the Web UI

The Telos web UI provides a user-friendly interface for requirements management.

### Dashboard

The dashboard provides an overview of all projects and key metrics:

- Project count and requirement statistics
- Recent activity
- Quality metrics and validation status
- Planning readiness indicators

### Projects View

In the Projects view, you can:

1. **Create a new project**: Click the "New Project" button and provide a name and description
2. **Browse projects**: View a list of all projects with key metrics
3. **Filter and search**: Find projects by name, status, or other attributes
4. **Open a project**: Click on a project card to open the project detail view

### Requirements View

The Requirements view shows all requirements for a project:

1. **Create a new requirement**: Click "Add Requirement" and fill in the details
2. **View requirements**: See a list or board view of all requirements
3. **Filter and search**: Find requirements by status, type, priority, or tags
4. **Edit a requirement**: Click on a requirement to edit its details
5. **Validate requirements**: Run quality checks on requirements
6. **Export requirements**: Export to various formats (JSON, Markdown)

### Requirement Detail View

When viewing a single requirement, you can:

1. **Edit basic information**: Title, description, type, priority, status
2. **Add tags**: Categorize the requirement for easier filtering
3. **Set relationships**: Define parent-child relationships and dependencies
4. **View traces**: See bidirectional traces to other requirements
5. **View history**: See a history of changes to the requirement
6. **Refine with AI**: Use LLM-powered analysis to improve quality

### Hierarchy View

The Hierarchy view shows the structure of requirements:

1. **Visualize parent-child relationships**: See how requirements are organized
2. **Expand/collapse nodes**: Focus on specific areas of the hierarchy
3. **Drag and drop**: Reorganize the hierarchy visually
4. **Add requirements**: Create new requirements directly in the hierarchy

### Traces View

The Traces view shows the relationships between requirements:

1. **View requirement traces**: See how requirements relate to each other
2. **Create new traces**: Define new relationships between requirements
3. **Filter by trace type**: Focus on specific types of relationships
4. **Visualize impact**: See the impact of changes across requirements

### Validation View

The Validation view helps ensure high-quality requirements:

1. **Run validation checks**: Check requirements against quality criteria
2. **View quality scores**: See scores for clarity, completeness, testability, etc.
3. **Get improvement suggestions**: Receive AI-powered suggestions for improvement
4. **Track progress**: Monitor requirement quality over time

### Planning View

The Planning view integrates with Prometheus for project planning:

1. **Check planning readiness**: See if requirements are ready for planning
2. **Generate implementation plan**: Create a plan based on requirements
3. **View tasks and timeline**: See tasks derived from requirements
4. **Adjust priorities**: Modify priorities to affect planning outcome

## Using the CLI

The Telos CLI provides command-line access to all functionality.

### Project Commands

```bash
# Create a new project
telos project create --name "My Project" --description "Project description"

# List all projects
telos project list

# Show project details
telos project show --project-id my-project-id

# Delete a project
telos project delete --project-id my-project-id
```

### Requirement Commands

```bash
# Add a requirement
telos requirement add --project-id my-project-id --title "User Authentication" --description "The system must authenticate users"

# List requirements
telos requirement list --project-id my-project-id

# Show requirement details
telos requirement show --project-id my-project-id --requirement-id my-requirement-id

# Update a requirement
telos requirement update --project-id my-project-id --requirement-id my-requirement-id --title "Updated Title"

# Delete a requirement
telos requirement delete --project-id my-project-id --requirement-id my-requirement-id
```

### Visualization Commands

```bash
# Visualize requirements hierarchy
telos viz requirements --project-id my-project-id --output requirements.png

# Visualize requirement traces
telos viz traces --project-id my-project-id --output traces.png
```

### Refinement Commands

```bash
# Interactively refine a requirement
telos refine requirement --project-id my-project-id --requirement-id my-requirement-id

# Analyze requirements for planning
telos refine analyze --project-id my-project-id
```

## Using the API

The Telos API provides programmatic access to all functionality. See the [API Reference](telos_api_reference.md) for detailed documentation.

### Example: Creating a Project

```python
import requests

# Create a project
response = requests.post("http://localhost:8008/api/projects", json={
    "name": "API Test Project",
    "description": "Created via API",
    "metadata": {
        "category": "Development",
        "priority": "High"
    }
})

project_id = response.json()["project_id"]
print(f"Created project with ID: {project_id}")
```

### Example: Creating a Requirement

```python
import requests

# Create a requirement
response = requests.post(f"http://localhost:8008/api/projects/{project_id}/requirements", json={
    "title": "User Authentication",
    "description": "The system shall authenticate users with username and password",
    "requirement_type": "functional",
    "priority": "high",
    "status": "new",
    "tags": ["security", "user"]
})

requirement_id = response.json()["requirement_id"]
print(f"Created requirement with ID: {requirement_id}")
```

### Example: WebSocket for Real-time Updates

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

## Best Practices

### Writing Good Requirements

1. **Be specific and clear**: Avoid ambiguous language
2. **Use "shall" statements**: For functional requirements ("The system shall...")
3. **Include context**: Explain why the requirement matters
4. **Make them testable**: Include criteria for verification
5. **Keep them atomic**: Each requirement should describe one capability
6. **Use consistent terminology**: Maintain a glossary of terms
7. **Avoid weak words**: Like "should", "may", "might", "could"
8. **Include acceptance criteria**: Define what "done" means
9. **Add metadata**: Tags, priority, status, etc.
10. **Maintain relationships**: Link related requirements

### Organizing Requirements

1. **Use hierarchical structure**: Group related requirements
2. **Create logical categories**: Functional, non-functional, etc.
3. **Use consistent numbering**: Make requirements easy to reference
4. **Maintain traceability**: Create traces between related requirements
5. **Tag for easy filtering**: Use consistent tags for categorization

### Validating Requirements

1. **Run validation regularly**: Check quality early and often
2. **Address all issues**: Fix problems identified by validation
3. **Use AI-powered refinement**: Get suggestions for improvement
4. **Review before planning**: Ensure requirements are ready for planning
5. **Maintain quality metrics**: Track improvement over time

### Integration with Planning

1. **Ensure requirements are ready**: Validate before planning
2. **Create traces to design**: Link requirements to design elements
3. **Link to implementation tasks**: Connect requirements to tasks
4. **Track progress against requirements**: Monitor implementation status
5. **Update requirements as needed**: Requirements evolve as projects progress

## Troubleshooting

### Common Issues

1. **API connection failure**:
   - Ensure Telos API server is running (`telos-api`)
   - Check port 8008 is available and not blocked
   - Verify network connectivity

2. **UI component not loading**:
   - Ensure Hephaestus UI server is running
   - Check browser console for errors
   - Clear browser cache and reload

3. **WebSocket disconnects**:
   - Check network stability
   - Implement reconnection logic in clients

4. **LLM analysis not working**:
   - Verify Rhetor is running and registered with Hermes
   - Check LLM client configuration
   - Ensure API keys are set if using external LLMs

### Getting Help

If you encounter issues not covered here:

1. Check logs in the Tekton Dashboard
2. Review documentation in the docs directory
3. Contact the Tekton team for support

## Advanced Topics

### Custom Validation Rules

You can create custom validation rules by extending the validation engine:

```python
# Example: Custom validation rule
def validate_security_requirements(requirement):
    """Validate that security requirements follow specific patterns."""
    if requirement.tags and "security" in requirement.tags:
        if not any(word in requirement.description.lower() for word in ["encrypt", "secure", "protect", "authenticate"]):
            return {
                "valid": False,
                "issue": "Security requirement missing specific security actions"
            }
    return {"valid": True}
```

### Requirement Templates

Create templates for common requirement types:

```python
# Example: Functional requirement template
functional_template = {
    "title": "{{feature}} Capability",
    "description": "The system shall provide the capability to {{action}} {{object}} by {{means}}.",
    "requirement_type": "functional",
    "tags": ["feature"],
    "metadata": {
        "template": "functional"
    }
}
```

### Integration with External Systems

Telos can integrate with external systems through:

1. **API integration**: Use the REST API for system integration
2. **WebSocket for real-time updates**: Subscribe to changes
3. **Export/Import functionality**: Transfer requirements between systems
4. **Prometheus integration**: Connect to planning systems

## Resources

- [API Reference](telos_api_reference.md) - Detailed API documentation
- [SINGLE_PORT_ARCHITECTURE.md](../docs/SINGLE_PORT_ARCHITECTURE.md) - Architecture details
- [README.md](../Telos/README.md) - Quick reference guide
- [port_assignments.md](../config/port_assignments.md) - Port configuration
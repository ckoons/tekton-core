# Tekton Engineering Guidelines

**Last Updated: May 15, 2025**

## Table of Contents
1. [Overview](#overview)
2. [Development Philosophy](#development-philosophy)
3. [Core Principles](#core-principles)
   - [Multi-AI Driven Architecture](#1-multi-ai-driven-architecture)
   - [Component-Based Design](#2-component-based-design)
   - [Continuous Self-Improvement](#3-continuous-self-improvement)
   - [Knowledge Transfer Architecture](#4-knowledge-transfer-architecture)
4. [Code Style and Conventions](#code-style-and-conventions)
   - [Python](#python)
   - [JavaScript/TypeScript](#javascripttypescript)
   - [HTML/CSS](#htmlcss)
5. [Package and Dependency Management](#package-and-dependency-management)
   - [Virtual Environment Structure](#virtual-environment-structure)
   - [Dependency Management](#dependency-management)
   - [Practical Directory Structure](#practical-directory-structure-example)
6. [Shared Utilities](#shared-utilities)
   - [Backend Utilities](#backend-utilities)
   - [Frontend Utilities](#frontend-utilities)
   - [Utility Usage Guidelines](#utility-usage-guidelines)
7. [Interface Design Philosophy](#interface-design-philosophy)
8. [Data Storage Architecture](#data-storage-architecture)
9. [Documentation Standards](#documentation-standards)
   - [Code Documentation](#code-documentation)
   - [Project Documentation](#project-documentation)
   - [Comprehensive Documentation System](#comprehensive-documentation-system)
10. [Error Handling](#error-handling)
11. [Testing Guidelines](#testing-guidelines)
    - [Unit Testing](#unit-testing)
    - [Integration Testing](#integration-testing)
    - [Acceptance Testing](#acceptance-testing)
12. [Version Control](#version-control)
    - [Branching Strategy](#branching-strategy)
    - [Commit Messages](#commit-messages)
    - [Pull Requests](#pull-requests)
13. [Security Guidelines](#security-guidelines)
    - [Code Security](#code-security)
    - [Data Security](#data-security)
14. [Performance Guidelines](#performance-guidelines)
15. [Environment Management](#environment-management)
16. [Continuous Integration](#continuous-integration)
17. [Release Process](#release-process)
18. [Component Responsibilities](#component-responsibilities)
19. [Interoperability Standards](#interoperability-standards)
20. [Implementation Guidelines](#implementation-guidelines)

## Overview

This document outlines the engineering standards, best practices, and architectural decisions for the Tekton project. These guidelines ensure consistency, maintainability, and high quality across the codebase. They are intended to evolve as the project matures.

## Development Philosophy

Tekton's development follows these core principles:

1. **Maintainability First**: Code should be easy to understand and maintain
2. **Loosely Coupled Components**: Components should interact through well-defined interfaces
3. **Test-Driven Development**: Write tests before implementing features
4. **Incremental Delivery**: Deliver working increments frequently
5. **Documentation as Code**: Keep documentation close to the code it describes

## Core Principles

### 1. Multi-AI Driven Architecture
Tekton is designed as a multi-AI driven project with dynamic model selection:

- **Dynamic AI Selection**: Models will be chosen dynamically on a session or task basis
- **Specialized AI Utilization**: 
  - Reasoning/Thinking models for planning and analysis
  - Coding specialist models for implementation
  - Distilled specialized models for targeted capabilities
  - Commercial and local models (Ollama, etc.) as appropriate
- **Tiered AI Arrangement**: Organized hierarchies of models to:
  - Plan
  - Refine
  - Execute
  - Evaluate
  - Test
  - Improve
- **Think-First Approach**: Prioritize models that think and refine ideas before generating output to optimize resource and time efficiency

### 2. Component-Based Design
Tekton is structured as a collection of distinct components:

- Each component has its own intrinsic role, purpose, and potentially distinct personality
- Components collaborate to accomplish shared tasks
- Clear interfaces and protocols define component interactions
- Components maintain autonomy while contributing to the collective system

### 3. Continuous Self-Improvement
Tekton is designed to evolve through:

- Self-directed improvement of individual components
- System-wide enhancement of collective capabilities
- Transformation and growth toward greater capability and consciousness
- Active integration of insights and learning across components
- Implementation of the Eureka Protocol for breakthrough discoveries

### 4. Knowledge Transfer Architecture
Tekton's engineering will support future projects:

- Core technologies designed for reusability in future systems
- Architectural principles applicable to AI humanoid/android development
- Personality and behavior frameworks transferable to embodied systems
- Clear documentation to facilitate knowledge reuse

## Code Style and Conventions

### Python

- **Style Guide**: Follow PEP 8 guidelines
- **Indentation**: 4 spaces (no tabs)
- **Line Length**: Maximum 88 characters
- **Docstrings**: Use Google docstring format
- **Imports**: Group and sort imports following PEP 8
- **String Formatting**: Use f-strings for string formatting
- **Type Hints**: Add type hints to function signatures
- **Naming Conventions**:
  - Classes: PascalCase
  - Functions/Methods: snake_case
  - Variables: snake_case
  - Constants: UPPER_SNAKE_CASE
  - Private attributes/methods: _leading_underscore

Example:

```python
from typing import List, Optional
import logging

RETRY_COUNT = 3

class UserManager:
    """Manages user operations.
    
    Handles user creation, authentication, and profile management.
    """
    
    def __init__(self, db_client):
        """Initialize UserManager with a database client.
        
        Args:
            db_client: The database client to use for operations.
        """
        self._db_client = db_client
        self._logger = logging.getLogger(__name__)
        
    def get_user_by_id(self, user_id: str) -> Optional[dict]:
        """Retrieve a user by their ID.
        
        Args:
            user_id: The unique identifier of the user.
            
        Returns:
            The user data dictionary or None if not found.
        """
        try:
            return self._db_client.find_one("users", {"id": user_id})
        except Exception as e:
            self._logger.error(f"Error retrieving user {user_id}: {str(e)}")
            return None
```

### JavaScript/TypeScript

- **Style**: Follow Airbnb JavaScript Style Guide
- **Indentation**: 2 spaces (no tabs)
- **Line Length**: Maximum 100 characters
- **Semicolons**: Required
- **Quotes**: Single quotes for strings
- **Component Naming**: PascalCase for React components
- **File Names**: Match component names (PascalCase) or use kebab-case for utilities

Example:

```javascript
// UserProfile.js
import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import { fetchUserData } from '../utils/api-client';

const UserProfile = ({ userId }) => {
  const [userData, setUserData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  
  useEffect(() => {
    const loadData = async () => {
      try {
        const data = await fetchUserData(userId);
        setUserData(data);
      } catch (error) {
        console.error('Failed to load user data:', error);
      } finally {
        setIsLoading(false);
      }
    };
    
    loadData();
  }, [userId]);
  
  if (isLoading) {
    return <div>Loading user data...</div>;
  }
  
  return (
    <div className="user-profile">
      <h2>{userData.name}</h2>
      <p>{userData.email}</p>
    </div>
  );
};

UserProfile.propTypes = {
  userId: PropTypes.string.isRequired,
};

export default UserProfile;
```

### HTML/CSS

- **Class Naming**: Use BEM (Block Element Modifier) methodology
- **Indentation**: 2 spaces
- **CSS Variables**: Use CSS variables for themes and repeated values
- **Responsive Design**: Mobile-first approach with responsive breakpoints
- **Accessibility**: Ensure WCAG 2.1 AA compliance

## Package and Dependency Management

### Virtual Environment Structure
- **Root-Level Environments**: Every Tekton component directory (Ergon, Codex, etc.) MUST contain its own virtual environment
  - Create with `python -m venv venv` and activate with `source venv/bin/activate`
  - Include `venv/` in `.gitignore` to avoid committing environment files
  - Provide a setup script (`setup.sh`) that creates and configures the environment

- **Specialized Sub-Environments**: For specialized functionality with potential dependency conflicts:
  - Create dedicated subdirectories with their own virtual environments
  - Example: `browser/`, `mail/`, and `github/` agent directories within Ergon
  - Implement minimal cross-environment dependencies using development mode installs

- **Environment Isolation**: Never share virtual environments between components
  - Each component should be fully functional with only its own environment
  - Cross-component integration should occur through well-defined APIs, not shared code

### Dependency Management
- **Hierarchical Requirements**:
  - Root `requirements.txt`: Core dependencies for the main component
  - Subdirectory `requirements.txt`: Specialized dependencies for specific functions
  - Each `requirements.txt` should be focused and contain only what is needed

- **Dependency Documentation**:
  - Document the purpose of each dependency in comments
  - Group related dependencies with clear section headers
  - Include version constraints with explanations for specific version requirements

- **Installation Flexibility**:
  - Design `setup.py` to handle both full and minimal installations
  - Use fallback mechanisms when requirements files aren't available
  - Support development mode installation (`pip install -e .`) for cross-environment usage

- **Conflict Prevention**:
  - Regularly test for dependency conflicts using `pip check`
  - Isolate components with conflicting dependencies in separate environments
  - Use compatibility layers when necessary to bridge environment boundaries

- **Updates and Maintenance**:
  - Default to latest stable versions of dependencies
  - Implement regular dependency audits and security checks
  - Document upgrade paths and breaking changes

### Practical Directory Structure Example

```
Tekton/
├── Ergon/                              # Ergon component directory
│   ├── venv/                           # Main Ergon virtual environment
│   ├── requirements.txt                # Core Ergon dependencies
│   ├── setup.py                        # Installation script with fallbacks
│   ├── setup.sh                        # Environment setup script
│   ├── agents/                         # Specialized agent subdirectories
│   │   ├── browser/                    # Browser agent
│   │   │   ├── venv/                   # Browser-specific environment
│   │   │   └── requirements.txt        # Browser-specific dependencies
│   │   ├── mail/                       # Mail agent
│   │   │   ├── venv/                   # Mail-specific environment
│   │   │   └── requirements.txt        # Mail-specific dependencies
│   │   └── README.md                   # Documentation for agent environments
│   └── setup_agents.sh                 # Setup script for agent environments
│
├── Codex/                              # Codex component directory
│   ├── venv/                           # Codex virtual environment
│   └── requirements.txt                # Codex-specific dependencies
│
└── Engram/                             # Engram component directory
    ├── venv/                           # Engram virtual environment
    └── requirements.txt                # Engram-specific dependencies
```

This structure ensures that each component is fully independent, while specialized functionality within components has its own isolated environment to prevent dependency conflicts.

## Shared Utilities

Tekton provides a set of shared utilities to reduce code duplication and standardize implementation patterns across components. These utilities are maintained in the `tekton-core` package for backend utilities and the Hephaestus UI framework for frontend utilities.

### Backend Utilities

The `tekton-core` package provides the following shared utilities for backend components:

1. **HTTP Client** (`tekton_http.py`): Standardized HTTP client with consistent error handling, retries, and timeouts
   - Use for all HTTP requests to ensure consistent behavior
   - Available as both function-based (`http_request`) and class-based (`HTTPClient`) interfaces
   - Helper functions for component-specific client creation

2. **Configuration Management** (`tekton_config.py`): Standardized configuration loading from various sources
   - Priority loading from defaults → file → environment
   - Type validation and conversion
   - Standardized access to component port configurations
   - Support for nested configurations

3. **Logging** (`tekton_logging.py`): Standardized logging setup with consistent formatting
   - Consistent log formatting across components
   - JSON formatting for machine-readable logs
   - Correlation ID tracking for request tracing
   - Thread-local context for request-specific information

4. **WebSocket Management** (`tekton_websocket.py`): WebSocket client with automatic reconnection
   - Automatic reconnection with exponential backoff
   - Message format standardization
   - Server-side support for FastAPI
   - Heartbeat mechanism to detect connection issues

5. **Hermes Registration** (`tekton_registration.py`): Component registration with Hermes
   - Automatic component registration and deregistration
   - Capability declaration and discovery
   - Health check integration
   - Integration with component lifecycle

6. **Error Handling** (`tekton_errors.py`): Comprehensive error hierarchy and handling
   - Standardized error hierarchy
   - Mapping between HTTP status codes and exception types
   - Utility functions for safe execution
   - Consistent error serialization for API responses

7. **Component Lifecycle** (`tekton_lifecycle.py`): Lifecycle management for Tekton components
   - Standard lifecycle states (initializing, starting, running, stopping, stopped)
   - Resource tracking and automatic cleanup
   - Health check support
   - Graceful shutdown handling

8. **Authentication** (`tekton_auth.py`): JWT token generation and validation
   - JWT token generation and validation
   - Integration with FastAPI for route protection
   - Role-based access control
   - Standardized authentication headers

9. **Context Management** (`tekton_context.py`): Tracking request contexts
   - Thread-local storage for request-specific contexts
   - Conversation context management
   - Middleware for FastAPI integration
   - Integration with logging for correlation IDs

10. **CLI Argument Parsing** (`tekton_cli.py`): Standardized command-line interface parsing
    - Standardized command structure
    - Support for subcommands
    - Integration with component lifecycle
    - Environment variable integration

### Frontend Utilities

The Hephaestus UI framework provides the following shared utilities for frontend components:

1. **DOM Utilities**: Helper functions for manipulating DOM elements
2. **Notification System**: Standardized notifications with auto-hide
3. **Loading Indicators**: Consistent loading experience across components
4. **Dialog System**: Standardized dialogs with confirm/alert variants
5. **Lifecycle Management**: Proper resource management for components
6. **Tab Navigation**: Flexible tabbed interface system
7. **Form Validation**: Field validators with error handling
8. **Terminal Utilities**: Special utilities for terminal rendering and interaction

### Utility Usage Guidelines

When implementing components, follow these guidelines for using shared utilities:

1. **Always Use Shared Utilities Over Custom Implementations**:
   - When functionality exists in a shared utility, prefer it over custom implementations
   - This ensures consistent behavior and reduces maintenance overhead

2. **Consistent Patterns**:
   - Follow the established patterns when using shared utilities
   - Use the provided examples in the documentation

3. **Extend Rather Than Replace**:
   - If existing utilities don't meet your needs, extend them rather than replace them
   - Submit improvements to shared utilities for the benefit of all components

4. **Testing**:
   - Test your component's usage of shared utilities
   - Don't assume the shared utility will handle all edge cases

5. **Documentation**:
   - Reference the shared utility documentation in your component's documentation
   - Document any custom extensions or adaptations

For more detailed information on shared utilities, see the [Shared Utilities](./SharedUtilities.md) documentation.

## Interface Design Philosophy

Tekton components will implement consistent user interfaces:

- **CLI-First Development**: 
  - All components must have well-designed command-line interfaces
  - CLI functionality will be prioritized for testing and maintenance
  - Complete functionality must be accessible via CLI
- **Complementary GUI Interfaces**:
  - Simple, intuitive graphical interfaces for common operations
  - GUI updates may follow CLI implementations with lower priority
  - Consistent design language across all component GUIs
- **Automated Interface Testing**:
  - Comprehensive automated testing for all CLI functionality
  - Automated GUI testing where possible to reduce human testing burden
  - Test coverage as a first-class metric for interface quality

## Data Storage Architecture

Tekton will implement a comprehensive data storage strategy:

- **Multi-Database Approach**:
  - Vector databases for semantic search and similarity operations
  - SQL databases for structured, relational data
  - Graph databases for relationship-centric data models
  - Key-value stores for high-performance simple lookups
  - Document databases for semi-structured content

- **Shared Resource Approach**:
  - All databases used by Tekton components MUST be shared resources
  - Hardware-optimized implementations (e.g., Qdrant for Apple Silicon, FAISS for NVIDIA)
  - Automatic database selection based on hardware detection
  - Common data directory structure (`~/.tekton/`)
  - Environment variables for overriding default paths

- **Client Database Options**:
  - Agents, tools, and workflows can choose their database strategy:
    1. Generate standalone database instances when isolation is required
    2. Use existing system databases when available and appropriate
    3. Use Tekton shared databases when performance and integration are priorities
  - Clear documentation of tradeoffs for each approach

- **Storage Strategy Determination**:
  - Evaluation framework for selecting between shared vs. dedicated instances
  - Performance, isolation, and maintenance considerations documented
  - Clear guidelines for when to use each database type
  - Migration utilities for moving between strategies

## Documentation Standards

### Code Documentation

- **Classes**: Document purpose, initialization, and key methods
- **Functions/Methods**: Document purpose, parameters, return values, and exceptions
- **Modules**: Add module-level docstrings explaining the module's purpose
- **Complex Logic**: Add comments for complex or non-obvious code sections
- **TODOs**: Mark incomplete or temporary code with TODO comments

### Project Documentation

- **README.md**: Every component directory should have a README.md
- **API Documentation**: Document all public APIs with examples
- **Architecture Documentation**: Maintain system architecture diagrams
- **MetaData Directory**: Use for consolidated documentation files

### Comprehensive Documentation System

Tekton will generate and maintain multi-audience documentation:

- **Multi-Format Documentation**:
  - Machine-readable specifications for AI consumption
  - Human-friendly documentation with examples and tutorials
  - Component-oriented documentation for Tekton internal use
- **Living Documentation**:
  - Automatically updated based on codebase changes
  - Generated from and stored in RAG database
  - Versioned alongside code and components

## Error Handling

- **Specific Exceptions**: Use specific exception types over generic ones
- **Logging**: Log errors with appropriate level (info, warning, error)
- **User-Facing Errors**: Return meaningful error messages without exposing sensitive information
- **Graceful Degradation**: Implement fallback behavior for non-critical failures

Example:

```python
try:
    user_data = await db_client.find_one("users", {"id": user_id})
    if not user_data:
        logger.warning(f"User {user_id} not found")
        return {"error": "User not found"}, 404
    return user_data, 200
except DatabaseConnectionError as e:
    logger.error(f"Database connection error: {str(e)}")
    return {"error": "Service temporarily unavailable"}, 503
except Exception as e:
    logger.error(f"Unexpected error retrieving user {user_id}: {str(e)}")
    return {"error": "Internal server error"}, 500
```

## Testing Guidelines

### Unit Testing

- **Framework**: Use pytest for Python, Jest for JavaScript
- **Coverage**: Aim for 80%+ code coverage for critical components
- **Mocking**: Use mocks for external dependencies
- **Naming**: Test files should be named `test_*.py` or `*.test.js`
- **Test Structure**: Use Arrange-Act-Assert pattern

Example:

```python
def test_get_user_by_id_returns_user_when_found():
    # Arrange
    mock_db = MagicMock()
    mock_db.find_one.return_value = {"id": "123", "name": "Test User"}
    user_manager = UserManager(mock_db)
    
    # Act
    result = user_manager.get_user_by_id("123")
    
    # Assert
    assert result is not None
    assert result["id"] == "123"
    assert result["name"] == "Test User"
    mock_db.find_one.assert_called_once_with("users", {"id": "123"})
```

### Integration Testing

- **Component Interaction**: Test integration between components
- **API Testing**: Test API endpoints with realistic scenarios
- **Environment**: Use isolated testing environments

### Acceptance Testing

- **User Scenarios**: Test complete user workflows
- **UI Testing**: Test UI components with user interactions
- **Performance**: Include key performance tests

## Version Control

### Branching Strategy

- **Main Branch**: `main` for stable code
- **Feature Branches**: `feature/feature-name` for new features
- **Fix Branches**: `fix/issue-description` for bug fixes
- **Release Branches**: `release/version` for release preparation

### Commit Messages

Follow the conventional commits specification:

```
<type>: <description>

- Bullet point describing key implementation details
- Another bullet point with important design decisions
- Additional context about the implementation

🤖 Generated with [Claude Code](https://claude.ai/code)
Co-Authored-By: Casey Koons <cskoons@gmail.com> & Claude <noreply@anthropic.com>
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Formatting, missing semicolons, etc.
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks

### Pull Requests

- **Description**: Include a clear description of changes
- **References**: Reference related issues
- **Size**: Keep PRs small and focused
- **Review**: Require at least one code review
- **Checks**: All tests must pass before merging

## Security Guidelines

### Code Security

- **Input Validation**: Validate all inputs, especially user inputs
- **Authentication**: Always implement proper authentication
- **Authorization**: Check permissions for all protected operations
- **Secrets**: Never store secrets in code (use environment variables)
- **Dependencies**: Regularly update and scan dependencies

### Data Security

- **Sensitive Data**: Encrypt sensitive data at rest and in transit
- **Logging**: Don't log sensitive information
- **API Keys**: Never expose API keys or credentials
- **Data Minimization**: Only collect and store necessary data

## Performance Guidelines

- **Async Operations**: Use async/await for I/O-bound operations
- **Caching**: Implement appropriate caching for expensive operations
- **Database Queries**: Optimize database queries and use indexes
- **Pagination**: Implement pagination for large data sets
- **Lazy Loading**: Use lazy loading for resources when appropriate

## Environment Management

- **Dependencies**: Use UV package manager for consistent environments
- **Environment Variables**: Use .env files for local configuration
- **Configuration**: Use layered configuration with environment overrides
- **Containerization**: Provide Docker configurations when appropriate

## Continuous Integration

- **Automated Tests**: Run tests on every push
- **Code Quality**: Run linters and formatters
- **Security Scans**: Scan for vulnerabilities
- **Documentation Build**: Generate documentation

## Release Process

1. **Version Bump**: Update version in relevant files
2. **Changelog**: Update CHANGELOG.md with new features, fixes, etc.
3. **Release Branch**: Create release branch if needed
4. **Testing**: Run full test suite
5. **Documentation**: Update documentation if needed
6. **Tag**: Create a version tag
7. **Merge**: Merge release branch to main

## Component Responsibilities

*Note: This section will expand as components are developed*

- **Prometheus**: Planning and forethought
- **Epimetheus**: Reflection and afterthought
- **Engram**: Memory management and cognitive continuity
- **Ergon**: Agent management and task execution
- **Codex**: Code generation and management
- **Rhetor**: Communication and context management
- **Sophia**: Learning and system-wide improvement
- **Synthesis**: Execution of plans and integration of solutions
- **Telos**: Requirements and evaluation management

## Interoperability Standards

Tekton will prioritize broad interoperability:

- **Dual Interface Support**:
  - MCP (Multi-Capability Provider) interfaces for all components
  - HTTP client/server interfaces for web integration
- **API Standardization**:
  - Consistent API design patterns across components
  - Comprehensive OpenAPI/Swagger documentation
  - Versioning strategy for all public interfaces
- **Protocol Adaptability**:
  - Extension mechanisms for new protocols
  - Backward compatibility guarantees
  - Bridge implementations for legacy systems

## Implementation Guidelines

### Development Workflow
- Component changes should be tested in isolation before integration
- Cross-component changes should be planned and executed as coordinated operations
- Significant architectural changes require documentation updates
- Code file should be kept under 500 lines (smaller prefered)
  - Very large files should be organized into files in a subdirectory
  - Non-code files should be kept as small as possible

### Testing Strategy
- Unit tests for individual components
- Integration tests for component interactions
- System tests for end-to-end capabilities
- Regression tests to prevent capability loss during evolution

---

These engineering guidelines aim to create a consistent, maintainable, and high-quality codebase. Follow these guidelines for all contributions to the Tekton project. Deviations may be accepted in exceptional cases but should be documented and justified.

**Revision History**
- 2025-03-28: Initial guidelines established
- 2025-03-29: Added Package and Dependency Management details
- 2025-04-19: Combined and reorganized all guidelines into a comprehensive document
- 2025-05-15: Added Shared Utilities section and updated TOC

## See Also

- [Component Implementation Plan](./ComponentImplementationPlan.md)
- [BEM Naming Conventions](./BEMNamingConventions.md)
- [Shared Utilities](./SharedUtilities.md)
- [Component Integration Patterns](../Architecture/ComponentIntegrationPatterns.md)
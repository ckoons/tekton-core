# Building New Tekton Components

## Overview

This guide provides the standardized approach for building new Tekton components. All components follow the same patterns for consistency, maintainability, and interoperability within the Tekton ecosystem.

**Core Philosophy: Semper Progresso** - Always moving forward. We use the latest patterns and technologies without backward compatibility concerns.

## What is a Tekton Component?

A Tekton component is a self-contained service that:
- Provides specific functionality to the Tekton ecosystem
- Registers with Hermes for service discovery
- Exposes capabilities via MCP (Model Context Protocol) v2
- Has both CLI and API interfaces
- Includes a Hephaestus UI component for visibility
- Communicates with other components through standardized protocols

## Quick Start Checklist

- [ ] Create component directory structure
- [ ] Implement backend API server (FastAPI)
- [ ] Add MCP v2 endpoints
- [ ] Create CLI interface
- [ ] Register with Hermes
- [ ] Build UI component for Hephaestus
- [ ] Add health check endpoints
- [ ] Configure environment variables
- [ ] Write backend tests
- [ ] Document the component

## Documentation Structure

1. **[Component_Architecture_Guide.md](./Component_Architecture_Guide.md)** - Overall architecture and patterns
2. **[Backend_Implementation_Guide.md](./Backend_Implementation_Guide.md)** - Backend API and business logic
3. **[UI_Implementation_Guide.md](./UI_Implementation_Guide.md)** - Hephaestus UI integration
4. **[Step_By_Step_Tutorial.md](./Step_By_Step_Tutorial.md)** - Complete walkthrough
5. **[Shared_Patterns_Reference.md](./Shared_Patterns_Reference.md)** - Common patterns and utilities
6. **[Testing_Guide.md](./Testing_Guide.md)** - Test-driven development approach
7. **[Documentation_Requirements.md](./Documentation_Requirements.md)** - Required documentation

## Component Directory Structure

```
ComponentName/
├── README.md                    # Component overview and usage
├── setup.py                     # Python package setup
├── setup.sh                     # Installation script
├── run_componentname.sh         # Launch script
├── requirements.txt             # Python dependencies
├── componentname/               # Main package directory
│   ├── __init__.py
│   ├── __main__.py             # Entry point for python -m
│   ├── api/
│   │   ├── __init__.py
│   │   ├── app.py              # FastAPI application
│   │   ├── dependencies.py     # Dependency injection
│   │   ├── models.py           # Pydantic models
│   │   └── endpoints/
│   │       ├── __init__.py
│   │       ├── mcp.py          # MCP v2 endpoints
│   │       └── [feature].py    # Feature-specific endpoints
│   ├── cli/
│   │   ├── __init__.py
│   │   ├── main.py             # CLI entry point
│   │   └── commands/           # CLI command modules
│   ├── core/
│   │   ├── __init__.py
│   │   └── [business_logic].py # Core functionality
│   ├── models/
│   │   ├── __init__.py
│   │   └── [domain_models].py  # Domain models
│   └── utils/
│       └── __init__.py
├── ui/
│   ├── componentname-component.html  # UI component
│   ├── scripts/
│   │   └── componentname.js         # Component JavaScript
│   └── styles/
│       └── componentname.css        # Component styles
├── tests/
│   ├── __init__.py
│   ├── conftest.py             # Test configuration
│   └── test_[feature].py       # Test files
└── examples/
    └── test_fastmcp.py         # FastMCP integration example

```

## Key Principles

1. **Simplicity First** - No clever tricks, just reliable patterns
2. **UI as Visibility Layer** - Simple UI, LLMs handle complexity
3. **Test-Driven** - Tests define success criteria
4. **Living Documentation** - Updated each sprint via retrospectives
5. **Shared Utilities** - Use common modules, eliminate duplication
6. **MCP-Forward** - Shift functionality to MCPs where appropriate

## Port Assignment

Components use ports 8000-8014 (with Hephaestus UI on 8080). When creating a new component, check `/config/port_assignments.md` for the next available port.

## Next Steps

1. Read the [Component Architecture Guide](./Component_Architecture_Guide.md)
2. Follow the [Step By Step Tutorial](./Step_By_Step_Tutorial.md)
3. Use existing components (Apollo, Athena, Prometheus, Metis) as references
4. Keep it simple, keep it working, keep moving forward

---

*Last Updated: Development Sprint - Building_New_Tekton_Components*  
*Next Review: After Shared_Utilities_Sprint completion*
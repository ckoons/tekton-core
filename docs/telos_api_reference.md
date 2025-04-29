# Telos API Reference

This document provides detailed information about the Telos Requirements Management API endpoints, including request parameters, response formats, and examples.

## Table of Contents

- [Overview](#overview)
- [Base URL](#base-url)
- [Authentication](#authentication)
- [Response Format](#response-format)
- [API Endpoints](#api-endpoints)
  - [Projects](#projects)
  - [Requirements](#requirements)
  - [Traces](#traces)
  - [Validation](#validation)
  - [Planning](#planning)
  - [Export/Import](#exportimport)

## Overview

The Telos API follows a RESTful design pattern and provides endpoints for managing requirements, projects, traces, validation, and planning integration. The API implements Tekton's Single Port Architecture, with all HTTP endpoints accessible via `/api/*` paths.

## Base URL

All API endpoints are available under the base URL: `http://localhost:8008/api`

## Authentication

The current implementation does not include authentication. Future versions will implement authentication/authorization mechanisms.

## Response Format

All API responses are in JSON format. Successful responses typically include:

- For GET operations: Requested data
- For POST operations: The created resource or a success response
- For PUT operations: A success response or the updated resource
- For DELETE operations: A success response

Error responses follow a standard format:

```json
{
  "detail": "Error message describing the issue"
}
```

HTTP status codes:
- **200**: Success
- **201**: Created successfully
- **400**: Bad request (invalid input)
- **404**: Resource not found
- **500**: Server error
- **503**: Service unavailable (Requirements manager not initialized)

## API Endpoints

### Projects

#### List All Projects

```
GET /api/projects
```

**Response**:
```json
{
  "projects": [
    {
      "project_id": "project-1",
      "name": "Project One",
      "description": "Description of Project One",
      "created_at": 1682456789.123,
      "updated_at": 1682456789.123,
      "requirement_count": 5
    },
    {
      "project_id": "project-2",
      "name": "Project Two",
      "description": "Description of Project Two",
      "created_at": 1682456800.456,
      "updated_at": 1682456800.456,
      "requirement_count": 3
    }
  ],
  "count": 2
}
```

#### Create a Project

```
POST /api/projects
```

**Request Body**:
```json
{
  "name": "New Project",
  "description": "Description of New Project",
  "metadata": {
    "priority": "high",
    "deadline": "2025-12-31",
    "stakeholders": ["Product", "Engineering"]
  }
}
```

**Response**:
```json
{
  "project_id": "new-project-id",
  "name": "New Project",
  "description": "Description of New Project",
  "created_at": 1682456900.789
}
```

#### Get a Project

```
GET /api/projects/{project_id}
```

**Response**:
```json
{
  "project_id": "project-1",
  "name": "Project One",
  "description": "Description of Project One",
  "created_at": 1682456789.123,
  "updated_at": 1682456789.123,
  "metadata": {
    "priority": "high",
    "deadline": "2025-12-31",
    "stakeholders": ["Product", "Engineering"]
  },
  "requirements": {
    "req-1": {
      "requirement_id": "req-1",
      "title": "User Authentication",
      "status": "new",
      "priority": "high",
      "requirement_type": "functional"
    },
    "req-2": {
      "requirement_id": "req-2",
      "title": "User Authorization",
      "status": "in-progress",
      "priority": "high",
      "requirement_type": "functional"
    }
  },
  "hierarchy": {
    "root": ["req-1"],
    "req-1": ["req-2"]
  }
}
```

#### Update a Project

```
PUT /api/projects/{project_id}
```

**Request Body**:
```json
{
  "name": "Updated Project Name",
  "description": "Updated project description",
  "metadata": {
    "priority": "medium",
    "status": "active"
  }
}
```

**Response**:
```json
{
  "project_id": "project-1",
  "updated": {
    "name": "Updated Project Name",
    "description": "Updated project description",
    "metadata": {
      "priority": "medium",
      "deadline": "2025-12-31",
      "stakeholders": ["Product", "Engineering"],
      "status": "active"
    }
  },
  "updated_at": 1682457000.123
}
```

#### Delete a Project

```
DELETE /api/projects/{project_id}
```

**Response**:
```json
{
  "success": true,
  "project_id": "project-1"
}
```

### Requirements

#### List Requirements

```
GET /api/projects/{project_id}/requirements
```

**Query Parameters**:
- `status` (optional): Filter by status (new, in-progress, completed, rejected)
- `requirement_type` (optional): Filter by type (functional, non-functional, constraint)
- `priority` (optional): Filter by priority (critical, high, medium, low)
- `tag` (optional): Filter by tag

**Response**:
```json
{
  "requirements": [
    {
      "requirement_id": "req-1",
      "title": "User Authentication",
      "description": "The system must authenticate users with username and password.",
      "requirement_type": "functional",
      "priority": "high",
      "status": "new",
      "created_at": 1682456789.123,
      "updated_at": 1682456789.123
    },
    {
      "requirement_id": "req-2",
      "title": "User Authorization",
      "description": "The system must authorize users based on their roles.",
      "requirement_type": "functional",
      "priority": "high",
      "status": "in-progress",
      "created_at": 1682456800.456,
      "updated_at": 1682456800.456
    }
  ],
  "count": 2
}
```

#### Create a Requirement

```
POST /api/projects/{project_id}/requirements
```

**Request Body**:
```json
{
  "title": "Password Complexity",
  "description": "Passwords must have at least 8 characters with a mix of uppercase, lowercase, numbers, and special characters.",
  "requirement_type": "security",
  "priority": "high",
  "status": "new",
  "tags": ["security", "authentication"],
  "parent_id": "req-1",
  "dependencies": ["req-2"],
  "metadata": {
    "source": "Security Team",
    "complexity": "medium"
  }
}
```

**Response**:
```json
{
  "project_id": "project-1",
  "requirement_id": "req-3",
  "title": "Password Complexity",
  "created_at": 1682457100.789
}
```

#### Get a Requirement

```
GET /api/projects/{project_id}/requirements/{requirement_id}
```

**Response**:
```json
{
  "requirement_id": "req-1",
  "title": "User Authentication",
  "description": "The system must authenticate users with username and password.",
  "requirement_type": "functional",
  "priority": "high",
  "status": "new",
  "created_by": "user-1",
  "created_at": 1682456789.123,
  "updated_at": 1682456789.123,
  "tags": ["security", "user-management"],
  "parent_id": null,
  "dependencies": [],
  "metadata": {
    "source": "Product Team",
    "complexity": "medium"
  },
  "history": [
    {
      "timestamp": 1682456789.123,
      "action": "created",
      "description": "Requirement created"
    }
  ]
}
```

#### Update a Requirement

```
PUT /api/projects/{project_id}/requirements/{requirement_id}
```

**Request Body**:
```json
{
  "title": "User Authentication and Identity",
  "description": "The system must authenticate users with username, password, and optional 2FA.",
  "status": "in-progress",
  "priority": "critical"
}
```

**Response**:
```json
{
  "requirement_id": "req-1",
  "updated": ["title", "description", "status", "priority"],
  "updated_at": 1682457200.123
}
```

#### Delete a Requirement

```
DELETE /api/projects/{project_id}/requirements/{requirement_id}
```

**Response**:
```json
{
  "success": true,
  "project_id": "project-1",
  "requirement_id": "req-1"
}
```

#### Refine a Requirement

```
POST /api/projects/{project_id}/requirements/{requirement_id}/refine
```

**Request Body**:
```json
{
  "feedback": "This requirement needs to be more specific about the authentication methods supported.",
  "auto_update": false
}
```

**Response**:
```json
{
  "requirement_id": "req-1",
  "original": {
    "requirement_id": "req-1",
    "title": "User Authentication",
    "description": "The system must authenticate users with username and password."
  },
  "refined": {
    "requirement_id": "req-1",
    "title": "User Authentication",
    "description": "The system must authenticate users with username and password. Additionally, it should support OAuth 2.0 for third-party authentication providers including Google, Microsoft, and Apple ID."
  },
  "status": "success",
  "message": "Refinement successful",
  "changes": [
    "Added specific authentication providers",
    "Added OAuth 2.0 support details"
  ]
}
```

### Traces

#### List Traces

```
GET /api/projects/{project_id}/traces
```

**Query Parameters**:
- `requirement_id` (optional): Filter traces for a specific requirement

**Response**:
```json
{
  "traces": [
    {
      "trace_id": "trace-1",
      "source_id": "req-1",
      "target_id": "req-2",
      "trace_type": "depends_on",
      "description": "Authentication must be implemented before authorization",
      "created_at": 1682456900.123
    },
    {
      "trace_id": "trace-2",
      "source_id": "req-3",
      "target_id": "req-1",
      "trace_type": "refines",
      "description": "Password complexity refines authentication",
      "created_at": 1682457000.456
    }
  ],
  "count": 2
}
```

#### Create a Trace

```
POST /api/projects/{project_id}/traces
```

**Request Body**:
```json
{
  "source_id": "req-4",
  "target_id": "req-2",
  "trace_type": "depends_on",
  "description": "User profile depends on authorization",
  "metadata": {
    "strength": "strong",
    "reviewer": "security-team"
  }
}
```

**Response**:
```json
{
  "trace_id": "trace-3",
  "source_id": "req-4",
  "target_id": "req-2"
}
```

#### Get a Trace

```
GET /api/projects/{project_id}/traces/{trace_id}
```

**Response**:
```json
{
  "trace_id": "trace-1",
  "source_id": "req-1",
  "target_id": "req-2",
  "trace_type": "depends_on",
  "description": "Authentication must be implemented before authorization",
  "created_at": 1682456900.123,
  "metadata": {}
}
```

#### Update a Trace

```
PUT /api/projects/{project_id}/traces/{trace_id}
```

**Request Body**:
```json
{
  "trace_type": "implements",
  "description": "Updated description of the trace relationship",
  "metadata": {
    "reviewed": true,
    "reviewer": "security-team"
  }
}
```

**Response**:
```json
{
  "trace_id": "trace-1",
  "updated": {
    "trace_type": "implements",
    "description": "Updated description of the trace relationship",
    "metadata": {
      "reviewed": true,
      "reviewer": "security-team"
    }
  },
  "updated_at": 1682457300.789
}
```

#### Delete a Trace

```
DELETE /api/projects/{project_id}/traces/{trace_id}
```

**Response**:
```json
{
  "success": true,
  "trace_id": "trace-1"
}
```

### Validation

#### Validate a Project

```
POST /api/projects/{project_id}/validate
```

**Request Body**:
```json
{
  "criteria": {
    "check_completeness": true,
    "check_verifiability": true,
    "check_clarity": true,
    "check_consistency": false,
    "check_feasibility": false
  }
}
```

**Response**:
```json
{
  "project_id": "project-1",
  "validation_date": 1682457400.123,
  "results": [
    {
      "requirement_id": "req-1",
      "title": "User Authentication",
      "issues": [
        {
          "type": "completeness",
          "message": "Description is too short or missing details",
          "severity": "warning",
          "suggestion": "Add more details about authentication methods and security requirements"
        }
      ],
      "passed": false,
      "score": 0.6
    },
    {
      "requirement_id": "req-2",
      "title": "User Authorization",
      "issues": [],
      "passed": true,
      "score": 0.9
    }
  ],
  "summary": {
    "total_requirements": 2,
    "passed": 1,
    "failed": 1,
    "pass_percentage": 50.0,
    "issues_by_type": {
      "completeness": 1
    }
  },
  "criteria": {
    "check_completeness": true,
    "check_verifiability": true,
    "check_clarity": true,
    "check_consistency": false,
    "check_feasibility": false
  }
}
```

### Planning

#### Analyze Requirements for Planning

```
POST /api/projects/{project_id}/analyze
```

**Response**:
```json
{
  "status": "ready",
  "message": "Requirements are ready for planning",
  "context": {
    "project_info": {
      "name": "Project One",
      "description": "Description of Project One",
      "created_at": 1682456789.123,
      "updated_at": 1682456789.123
    },
    "requirements": {
      "functional": [
        {
          "id": "req-1",
          "title": "User Authentication",
          "description": "Description...",
          "status": "new",
          "priority": "high",
          "tags": ["security", "user-management"]
        }
      ],
      "non_functional": [],
      "constraints": []
    },
    "dependencies": {
      "req-2": ["req-1"]
    },
    "priorities": {
      "critical": [],
      "high": ["req-1", "req-2"],
      "medium": [],
      "low": []
    }
  },
  "analysis": {
    "requirements_ready": 2,
    "requirements_total": 2,
    "readiness_percentage": 100.0,
    "analyses": [
      {
        "requirement_id": "req-1",
        "title": "User Authentication",
        "ready": true,
        "score": 0.85,
        "suggestions": []
      },
      {
        "requirement_id": "req-2",
        "title": "User Authorization",
        "ready": true,
        "score": 0.9,
        "suggestions": []
      }
    ]
  }
}
```

#### Create a Plan

```
POST /api/projects/{project_id}/plan
```

**Response**:
```json
{
  "status": "success",
  "message": "Plan created successfully",
  "plan": {
    "thought_id": "plan-1",
    "complexity_score": 0.75,
    "plan": "# Implementation Plan for Project One\n\n## Phase 1: Authentication System\n- Implement user registration\n- Implement username/password authentication\n- Implement password reset flow\n\n## Phase 2: Authorization System\n- Implement role-based access control\n- Implement permission management\n\n## Estimated Timeline\n- Phase 1: 2 weeks\n- Phase 2: 3 weeks"
  }
}
```

### Export/Import

#### Export a Project

```
POST /api/projects/{project_id}/export
```

**Request Body**:
```json
{
  "format": "markdown",
  "sections": ["metadata", "requirements", "traces"]
}
```

**Response**:
```json
{
  "format": "markdown",
  "content": "# Project One\n\nDescription of Project One\n\n## Project Metadata\n\n- **Project ID:** project-1\n- **Created:** 2023-04-25 12:13:09\n- **Last Updated:** 2023-04-25 12:13:09\n\n## Requirements\n\n### Functional Requirements\n\n#### User Authentication (ID: req-1)\n\nThe system must authenticate users with username and password.\n\n- **Status:** new\n- **Priority:** high\n\n#### User Authorization (ID: req-2)\n\nThe system must authorize users based on their roles.\n\n- **Status:** in-progress\n- **Priority:** high\n\n## Requirement Traces\n\n- **depends_on:** User Authentication → User Authorization\n  - Authentication must be implemented before authorization\n"
}
```

#### Import a Project

```
POST /api/projects/import
```

**Request Body**:
```json
{
  "data": {
    "name": "Imported Project",
    "description": "Project imported from external source",
    "requirements": {
      "req-1": {
        "title": "Imported Requirement 1",
        "description": "Description of imported requirement 1",
        "requirement_type": "functional",
        "priority": "high",
        "status": "new"
      },
      "req-2": {
        "title": "Imported Requirement 2",
        "description": "Description of imported requirement 2",
        "requirement_type": "non-functional",
        "priority": "medium",
        "status": "new"
      }
    }
  },
  "format": "json",
  "merge_strategy": "replace"
}
```

**Response**:
```json
{
  "project_id": "imported-project-id",
  "name": "Imported Project",
  "imported_requirements": 2
}
```

## WebSocket API

In addition to the HTTP API, Telos provides a WebSocket interface for real-time updates at `ws://localhost:8008/ws`. See the technical documentation for WebSocket communication details.
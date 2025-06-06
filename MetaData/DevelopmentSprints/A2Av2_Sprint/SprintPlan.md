# A2A v2 Protocol Update - Sprint Plan

## Overview

This document outlines the high-level plan for the A2A v2 Protocol Update Sprint. It provides an overview of the goals, approach, and expected outcomes.

Tekton is an intelligent orchestration system that coordinates multiple AI models and resources to efficiently solve complex software engineering problems. This Development Sprint focuses on updating Tekton's Agent-to-Agent (A2A) communication framework to align with the new A2A Protocol v0.2.1 specification, bringing industry-standard protocols and enterprise-ready features to Tekton's multi-agent orchestration capabilities.

## Sprint Goals

The primary goals of this sprint are:

1. **Protocol Modernization**: Replace custom message format with JSON-RPC 2.0 over HTTP(S) for industry-standard communication
2. **Real-time Capabilities**: Implement Server-Sent Events (SSE) for streaming updates and real-time agent collaboration
3. **Task Lifecycle Management**: Introduce formal task states and lifecycle management with proper state transitions
4. **Enterprise Security**: Add OAuth/JWT authentication, authorization, and webhook-based push notifications
5. **Improved Discovery**: Update Agent Cards to match the new specification with skills, capabilities, and security schemes

## Business Value

This sprint delivers value by:

- **Standards Compliance**: Adopting JSON-RPC 2.0 enables easier integration with external systems and tools
- **Better Interoperability**: The new protocol allows Tekton agents to communicate with any A2A-compliant system
- **Enhanced Real-time Operations**: SSE streaming enables responsive, real-time agent collaboration
- **Enterprise Readiness**: Built-in security and authentication features make Tekton suitable for enterprise deployments
- **Improved Reliability**: Formal task lifecycle management provides better tracking and error handling

## Current State Assessment

### Existing Implementation

Tekton currently implements a custom A2A protocol with:
- Custom message format using Python dataclasses
- Basic agent registry with simple capability matching
- Task management without formal state transitions
- Direct agent-to-agent communication through Hermes message bus
- No streaming or real-time update capabilities
- Basic authentication through component registration

### Pain Points

- Custom protocol limits interoperability with external systems
- No support for long-running tasks with progress updates
- Limited real-time capabilities for agent collaboration
- Missing enterprise security features (OAuth, JWT)
- No standardized error handling or status codes
- Difficult to debug agent interactions without proper state tracking

## Proposed Approach

The update will be implemented in layers, starting with the protocol foundation and building up to full feature parity:

### Key Components Affected

- **tekton-core/tekton/a2a**: Complete overhaul of the A2A module to support JSON-RPC 2.0
- **Hermes/hermes/core/a2a_service.py**: Update to handle JSON-RPC methods and SSE streaming
- **Ergon/ergon/api/a2a_endpoints.py**: Modify endpoints to use new protocol format
- **All Components**: Update agent registration to use new Agent Card format

### Technical Approach

1. **Protocol Layer**: Implement JSON-RPC 2.0 request/response handling with proper error codes
2. **Transport Layer**: Add HTTP(S) server capabilities to components for A2A endpoints
3. **Streaming Layer**: Implement SSE for real-time updates using FastAPI's streaming response
4. **Task Management**: Create formal TaskState enum and state transition logic
5. **Security Layer**: Add authentication middleware supporting multiple schemes (Bearer, API Key)

## Code Quality Requirements

### Debug Instrumentation

All code produced in this sprint **MUST** follow the [Debug Instrumentation Guidelines](/MetaData/TektonDocumentation/DeveloperGuides/Debugging/DebuggingInstrumentation.md):

- Frontend JavaScript must use conditional `TektonDebug` calls
- Backend Python must use the `debug_log` utility and `@log_function` decorators
- All debug calls must include appropriate component names and log levels
- Error handling must include contextual debug information

This instrumentation will enable efficient debugging and diagnostics without impacting performance when disabled.

### Documentation

Code must be documented according to the following guidelines:

- Class and method documentation with clear purpose statements
- API contracts and parameter descriptions
- Requirements for component initialization
- Error handling strategy
- JSON-RPC method signatures and examples

### Testing

The implementation must include appropriate tests:

- Unit tests for JSON-RPC protocol handling
- Integration tests for agent communication
- Performance tests for streaming capabilities
- Security tests for authentication/authorization

## Out of Scope

The following items are explicitly out of scope for this sprint:

- UI updates for new A2A features
- External agent integration (focus on internal Tekton agents first)
- Advanced A2A features like agent collaboration protocols
- Performance optimization (focus on correctness first)
- Backward compatibility (clean implementation of v0.2.1)

## Dependencies

This sprint has the following dependencies:

- FastAPI for HTTP server and SSE streaming support
- jsonrpc package for protocol handling
- Current Tekton infrastructure (Hermes, component registration)
- Existing authentication mechanisms for backward compatibility

## Timeline and Phases

This sprint is planned to be completed in 3 phases:

### Phase 1: Protocol Foundation
- **Duration**: 2-3 days
- **Focus**: JSON-RPC 2.0 implementation and basic HTTP transport
- **Key Deliverables**: 
  - JSON-RPC request/response handling
  - HTTP endpoints for A2A methods
  - Error code implementation
  - Basic tests

### Phase 2: Streaming and Tasks
- **Duration**: 2-3 days
- **Focus**: SSE streaming and formal task management
- **Key Deliverables**:
  - Server-Sent Events implementation
  - TaskState enum and transitions
  - Task status updates
  - Streaming tests

### Phase 3: Security and Agent Cards
- **Duration**: 2-3 days
- **Focus**: Authentication, Agent Cards, and integration
- **Key Deliverables**:
  - Authentication middleware
  - Updated Agent Card format
  - Well-known URI endpoints
  - Integration with existing components

## Risks and Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Steep learning curve for JSON-RPC 2.0 | Medium | Medium | Provide comprehensive examples and documentation |
| Performance impact from HTTP overhead | Medium | Low | Use persistent connections and connection pooling |
| Complex state management for tasks | Medium | Medium | Start with simple states, add complex ones incrementally |
| Security vulnerabilities in auth | High | Low | Use established libraries and patterns |

## Success Criteria

This sprint will be considered successful if:

- JSON-RPC 2.0 protocol is fully implemented and tested
- At least one agent can communicate using the new protocol
- SSE streaming works for real-time updates
- Task state transitions are properly tracked
- All code follows the Debug Instrumentation Guidelines
- Documentation is complete and accurate
- Tests pass with 80% coverage

## Key Stakeholders

- **Casey**: Human-in-the-loop project manager
- **Tekton Core Team**: Affected by protocol changes
- **Component Maintainers**: Need to update their agents

## References

- [A2A Protocol Specification v0.2.1](https://google-a2a.github.io/A2A/specification/)
- [JSON-RPC 2.0 Specification](https://www.jsonrpc.org/specification)
- [Server-Sent Events W3C Specification](https://html.spec.whatwg.org/multipage/server-sent-events.html)
- [Current Tekton A2A Implementation](/Tekton/tekton/a2a/)
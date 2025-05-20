"""
FastMCP Integration - Decorator-based MCP implementation for Tekton.

This module provides a standardized, decorator-based approach to implementing
the Model Context Protocol (MCP) in Tekton components, inspired by FastMCP.
"""

from tekton.mcp.fastmcp.decorators import (
    mcp_tool,
    mcp_capability,
    mcp_processor,
    mcp_context,
    MCPToolMeta
)
from tekton.mcp.fastmcp.adapters import (
    adapt_tool,
    adapt_processor,
    adapt_context
)
from tekton.mcp.fastmcp.schema import (
    ToolSchema,
    ProcessorSchema,
    CapabilitySchema,
    ContextSchema,
    MessageSchema,
    ResponseSchema,
    ContentSchema,
    validate_schema
)
from tekton.mcp.fastmcp.client import (
    MCPClient,
    register_component,
    get_capabilities,
    execute_tool
)

__all__ = [
    # Decorators
    "mcp_tool", "mcp_capability", "mcp_processor", "mcp_context", "MCPToolMeta",
    
    # Adapters
    "adapt_tool", "adapt_processor", "adapt_context",
    
    # Schema
    "ToolSchema", "ProcessorSchema", "CapabilitySchema", "ContextSchema",
    "MessageSchema", "ResponseSchema", "ContentSchema", "validate_schema",
    
    # Client
    "MCPClient", "register_component", "get_capabilities", "execute_tool"
]
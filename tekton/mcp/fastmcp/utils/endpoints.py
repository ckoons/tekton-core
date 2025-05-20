"""
MCP Endpoint Utilities for Tekton Components.

This module provides common utilities for creating and including
FastMCP endpoints in Tekton components.
"""

import logging
from typing import Any, Dict, List, Optional, Union

from fastapi import APIRouter, Depends, Body, HTTPException
from fastapi.responses import JSONResponse

from tekton.mcp.fastmcp.schema import (
    MCPRequest,
    MCPResponse,
    MCPCapability,
    MCPTool
)

logger = logging.getLogger(__name__)

def create_mcp_router(
    prefix: str = "/mcp",
    tags: List[str] = ["mcp"],
    dependencies: List[Depends] = None
) -> APIRouter:
    """
    Create a standard MCP router for a Tekton component.
    
    Args:
        prefix: URL prefix for the router
        tags: FastAPI tags for the router
        dependencies: Optional dependencies for all endpoints
        
    Returns:
        Configured APIRouter for MCP endpoints
    """
    dependencies = dependencies or []
    
    router = APIRouter(
        prefix=prefix,
        tags=tags,
        dependencies=dependencies,
        responses={404: {"description": "Not found"}}
    )
    
    return router


def include_mcp_router(
    app: Any, 
    mcp_router: APIRouter,
    component_name: str
) -> None:
    """
    Include an MCP router in a FastAPI application.
    
    Args:
        app: FastAPI application
        mcp_router: MCP router to include
        component_name: Name of the component (for logging)
    """
    try:
        app.include_router(mcp_router)
        logger.info(f"Added MCP router to {component_name}")
    except Exception as e:
        logger.error(f"Failed to include MCP router for {component_name}: {e}")
        # Continue without MCP router rather than failing the application startup
        pass


def add_standard_mcp_endpoints(
    router: APIRouter,
    get_capabilities_func: Any,
    get_tools_func: Any,
    process_request_func: Any,
    component_manager_dependency: Depends
) -> APIRouter:
    """
    Add standard MCP endpoints to a router.
    
    Args:
        router: APIRouter to add endpoints to
        get_capabilities_func: Function to get capabilities
        get_tools_func: Function to get tools
        process_request_func: Function to process requests
        component_manager_dependency: Dependency to get component manager
        
    Returns:
        Router with added endpoints
    """
    
    @router.get("/health")
    async def mcp_health():
        """MCP health check endpoint."""
        return {"status": "healthy", "message": "MCP service is running"}
    
    @router.get("/capabilities")
    async def get_capabilities(
        manager = Depends(component_manager_dependency)
    ):
        """Get component MCP capabilities."""
        capabilities = get_capabilities_func(manager)
        return {
            "capabilities": [cap.dict() for cap in capabilities],
            "count": len(capabilities)
        }
    
    @router.get("/tools")
    async def get_tools(
        manager = Depends(component_manager_dependency)
    ):
        """Get component MCP tools."""
        tools = get_tools_func(manager)
        return {
            "tools": [tool.dict() for tool in tools],
            "count": len(tools)
        }
    
    @router.post("/process", response_model=MCPResponse)
    async def process_request(
        request: MCPRequest = Body(...),
        manager = Depends(component_manager_dependency)
    ):
        """Process an MCP request."""
        try:
            response = await process_request_func(manager, request)
            return response
        except Exception as e:
            logger.error(f"Error processing MCP request: {e}")
            return MCPResponse(
                status="error",
                error=f"Error processing request: {str(e)}",
                result=None
            )
    
    return router
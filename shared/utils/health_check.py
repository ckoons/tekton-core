"""
Standardized Health Check Response for Tekton Components

Provides a consistent health check format across all components.
"""
from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class HealthCheckResponse(BaseModel):
    """Standard health check response format"""
    status: str = Field(..., description="Health status: healthy, degraded, or unhealthy")
    version: str = Field(..., description="Component version")
    timestamp: str = Field(..., description="ISO-8601 timestamp")
    component: str = Field(..., description="Component name")
    port: int = Field(..., description="Component port")
    registered_with_hermes: bool = Field(default=False, description="Whether registered with Hermes")
    details: Dict[str, Any] = Field(default_factory=dict, description="Component-specific details")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "version": "0.1.0",
                "timestamp": "2025-04-25T10:30:00Z",
                "component": "rhetor",
                "port": 8003,
                "registered_with_hermes": True,
                "details": {
                    "providers_available": 6,
                    "active_contexts": 3
                }
            }
        }


def create_health_response(
    component_name: str,
    port: int,
    version: str,
    status: str = "healthy",
    registered: bool = False,
    details: Optional[Dict[str, Any]] = None
) -> HealthCheckResponse:
    """Helper function to create a standardized health response"""
    return HealthCheckResponse(
        status=status,
        version=version,
        timestamp=datetime.now().isoformat(),
        component=component_name,
        port=port,
        registered_with_hermes=registered,
        details=details or {}
    )
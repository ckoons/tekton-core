#!/usr/bin/env python3
"""
Emergency Fallback Component Module

Implements an emergency fallback component with minimal functionality.
"""

import time
import logging
from typing import Dict, Any, Optional

from tekton.core.component_lifecycle import ComponentRegistry

from .base import BaseComponent

logger = logging.getLogger("tekton.test_lifecycle.components.emergency")


class EmergencyFallbackComponent(BaseComponent):
    """Emergency fallback component with minimal functionality."""
    
    def __init__(self, 
                component_id: str,
                component_name: str,
                registry: ComponentRegistry,
                target_component_id: str):
        """
        Initialize emergency fallback component.
        
        Args:
            component_id: Component ID
            component_name: Human-readable name
            registry: Component registry
            target_component_id: ID of component to provide fallbacks for
        """
        super().__init__(component_id, component_name, "emergency", registry)
        self.target_component_id = target_component_id
        
    async def _register_capabilities(self) -> None:
        """Register emergency fallback handlers."""
        # Register fallback for data processing
        await self.registry.register_fallback_handler(
            component_id=self.target_component_id,
            capability_name="process_data",
            provider_id=self.component_id,
            fallback_handler=self.process_data_emergency,
            capability_level=10
        )
        
        # Register fallback for data retrieval
        await self.registry.register_fallback_handler(
            component_id=self.target_component_id,
            capability_name="retrieve_data",
            provider_id=self.component_id,
            fallback_handler=self.retrieve_data_emergency,
            capability_level=10
        )
    
    async def process_data_emergency(self, data: Dict[str, Any], options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process data with minimal functionality (emergency fallback).
        
        Args:
            data: Data to process
            options: Optional processing options
            
        Returns:
            Processed data with minimal functionality
        """
        # Minimal processing (no delay)
        return {
            "id": data.get("id", "unknown"),
            "processed": False,
            "timestamp": time.time(),
            "result": "Emergency processing only - full result not available",
            "emergency": True,
            "limitations": ["Minimal functionality", "Placeholder data"]
        }
    
    async def retrieve_data_emergency(self, id: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Retrieve data with minimal functionality (emergency fallback).
        
        Args:
            id: Data ID
            options: Optional retrieval options
            
        Returns:
            Retrieved data with minimal functionality
        """
        # Minimal retrieval (no delay)
        return {
            "id": id,
            "retrieved": False,
            "timestamp": time.time(),
            "data": {
                "value": "Emergency fallback data - limited data available",
                "source": self.component_id
            },
            "emergency": True,
            "limitations": ["Minimal functionality", "Placeholder data"]
        }
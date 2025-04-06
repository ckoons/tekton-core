#!/usr/bin/env python3
"""
Fallback Component Module

Implements a fallback component with limited functionality.
"""

import time
import random
import asyncio
import logging
from typing import Dict, Any, Optional

from tekton.core.component_lifecycle import ComponentRegistry

from .base import BaseComponent

logger = logging.getLogger("tekton.test_lifecycle.components.fallback")


class FallbackComponent(BaseComponent):
    """Fallback component for graceful degradation demonstration."""
    
    def __init__(self, 
                component_id: str,
                component_name: str,
                registry: ComponentRegistry,
                target_component_id: str):
        """
        Initialize fallback component.
        
        Args:
            component_id: Component ID
            component_name: Human-readable name
            registry: Component registry
            target_component_id: ID of component to provide fallbacks for
        """
        super().__init__(component_id, component_name, "fallback", registry)
        self.target_component_id = target_component_id
        
    async def _register_capabilities(self) -> None:
        """Register fallback handlers."""
        # Register fallback for data processing
        await self.registry.register_fallback_handler(
            component_id=self.target_component_id,
            capability_name="process_data",
            provider_id=self.component_id,
            fallback_handler=self.process_data_fallback,
            capability_level=50
        )
        
        # Register fallback for data retrieval
        await self.registry.register_fallback_handler(
            component_id=self.target_component_id,
            capability_name="retrieve_data",
            provider_id=self.component_id,
            fallback_handler=self.retrieve_data_fallback,
            capability_level=50
        )
    
    async def process_data_fallback(self, data: Dict[str, Any], options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process data with limited functionality (fallback).
        
        Args:
            data: Data to process
            options: Optional processing options
            
        Returns:
            Processed data with limited functionality
        """
        # Simplified processing
        await asyncio.sleep(0.05)
        
        # Basic result with limitations
        result = {
            "id": data.get("id", str(random.randint(1000, 9999))),
            "processed": True,
            "timestamp": time.time(),
            "result": f"Limited processing by {self.component_id}: {data.get('value', 'unknown')}",
            "fallback": True,
            "limitations": ["Basic processing only", "No advanced features"]
        }
        
        return result
    
    async def retrieve_data_fallback(self, id: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Retrieve data with limited functionality (fallback).
        
        Args:
            id: Data ID
            options: Optional retrieval options
            
        Returns:
            Retrieved data with limited functionality
        """
        # Simplified retrieval
        await asyncio.sleep(0.02)
        
        # Basic result with limitations
        result = {
            "id": id,
            "retrieved": True,
            "timestamp": time.time(),
            "data": {
                "value": f"Basic data for {id}",
                "source": self.component_id
            },
            "fallback": True,
            "limitations": ["Basic data only", "Limited fields"]
        }
        
        return result
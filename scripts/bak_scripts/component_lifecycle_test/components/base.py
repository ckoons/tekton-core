#!/usr/bin/env python3
"""
Base Component Module

Provides a base component class for lifecycle testing.
"""

import time
import logging
from typing import Dict, Any, Optional

from tekton.core.lifecycle import ComponentRegistration
from tekton.core.component_lifecycle import ComponentRegistry

logger = logging.getLogger("tekton.test_lifecycle.components.base")


class BaseComponent:
    """
    Base component class for lifecycle testing.
    """
    
    def __init__(self, 
                component_id: str,
                component_name: str,
                component_type: str,
                registry: ComponentRegistry):
        """
        Initialize base component.
        
        Args:
            component_id: Component ID
            component_name: Human-readable name
            component_type: Type of component
            registry: Component registry
        """
        self.component_id = component_id
        self.component_name = component_name
        self.component_type = component_type
        self.registry = registry
        self.instance_uuid = None
        self.running = False
        self.startup_time = time.time()
        
    async def start(self) -> bool:
        """
        Start the component.
        
        Returns:
            True if successful
        """
        # Create registration
        registration = ComponentRegistration(
            component_id=self.component_id,
            component_name=self.component_name,
            component_type=self.component_type
        )
        
        # Register with registry
        success, message = await self.registry.register_component(registration)
        if not success:
            logger.error(f"Failed to register component {self.component_id}: {message}")
            return False
            
        # Store instance UUID
        self.instance_uuid = registration.instance_uuid
        
        # Register capabilities
        await self._register_capabilities()
        
        logger.info(f"Component {self.component_id} started")
        return True
        
    async def stop(self) -> None:
        """Stop the component."""
        self.running = False
        logger.info(f"Component {self.component_id} stopped")
        
    async def _register_capabilities(self) -> None:
        """Register component capabilities."""
        pass

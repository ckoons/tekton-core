#!/usr/bin/env python3
"""
Base Service Module

Defines base service class for component services.
"""

import time
import random
import asyncio
import logging
from typing import Dict, List, Any, Optional, Set, Callable, Coroutine

from tekton.core.lifecycle import ComponentState
from tekton.core.component_lifecycle import ComponentRegistry
from tekton.core.integration import ComponentHealthAdapter

logger = logging.getLogger("tekton.test_integration.base")


class BaseService:
    """Base service implementation for testing."""
    
    def __init__(self, 
                component_id: str,
                component_name: str,
                component_type: str,
                registry: ComponentRegistry,
                version: str = "1.0.0"):
        """
        Initialize base service.
        
        Args:
            component_id: Component ID
            component_name: Human-readable name
            component_type: Component type
            registry: Component registry
            version: Component version
        """
        self.component_id = component_id
        self.component_name = component_name
        self.component_type = component_type
        self.registry = registry
        self.version = version
        self.health_adapter = ComponentHealthAdapter(
            component_id=component_id,
            component_name=component_name,
            component_type=component_type,
            version=version
        )
        self.running = False
        
    async def start(self) -> bool:
        """
        Start the service.
        
        Returns:
            True if started successfully
        """
        # Start health adapter
        await self.health_adapter.start()
        
        # Register with component registry
        success, _ = await self.registry.register_component(
            {
                "component_id": self.component_id,
                "component_name": self.component_name,
                "component_type": self.component_type,
                "version": self.version,
                "state": ComponentState.INITIALIZING.value
            }
        )
        
        if not success:
            logger.error(f"Failed to register component {self.component_id}")
            return False
            
        # Register capabilities - to be implemented by child classes
        await self._register_capabilities()
        
        # Start background tasks
        self.running = True
        self.health_adapter.run_task(self._metrics_updater)
        
        # Update state to ready
        self.health_adapter.update_state(ComponentState.READY.value, reason="startup.completed")
        
        logger.info(f"Started {self.component_type} service {self.component_id}")
        return True
        
    async def stop(self) -> None:
        """Stop the service."""
        self.running = False
        
        # Update state
        self.health_adapter.update_state(ComponentState.STOPPING.value, reason="shutdown.normal")
        
        # Stop health adapter
        await self.health_adapter.stop()
        
        logger.info(f"Stopped {self.component_type} service {self.component_id}")
        
    async def _register_capabilities(self) -> None:
        """Register capabilities - to be implemented by child classes."""
        pass
        
    async def _metrics_updater(self) -> None:
        """Background task to update metrics - to be implemented by child classes."""
        pass

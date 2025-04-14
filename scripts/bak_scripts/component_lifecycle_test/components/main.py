#!/usr/bin/env python3
"""
Main Test Component Module

Implements the main test component for lifecycle testing.
"""

import time
import random
import asyncio
import logging
from typing import Dict, Any, Optional

from tekton.core.lifecycle import ComponentState
from tekton.core.component_lifecycle import ComponentRegistry

from .base import BaseComponent

logger = logging.getLogger("tekton.test_lifecycle.components.main")


class TestComponent(BaseComponent):
    """Test component for lifecycle management demonstration."""
    
    def __init__(self, 
                component_id: str,
                component_name: str,
                component_type: str,
                registry: ComponentRegistry):
        """
        Initialize test component.
        
        Args:
            component_id: Component ID
            component_name: Human-readable name
            component_type: Type of component
            registry: Component registry
        """
        super().__init__(component_id, component_name, component_type, registry)
        self.health_metrics = {
            "cpu_usage": 0.2,
            "memory_usage": 0.3,
            "request_latency": 50.0,
            "error_rate": 0.01,
            "throughput": 100.0
        }
        
    async def start(self) -> bool:
        """
        Start the component.
        
        Returns:
            True if successful
        """
        success = await super().start()
        
        if success:
            # Start heartbeat task
            self.running = True
            asyncio.create_task(self._heartbeat_loop())
            
        return success
        
    async def stop(self) -> None:
        """Stop the component."""
        self.running = False
        
        # Update state to stopping
        await self.registry.update_component_state(
            component_id=self.component_id,
            instance_uuid=self.instance_uuid,
            state=ComponentState.STOPPING.value,
            metadata={
                "reason": "shutdown.normal",
                "details": "Normal shutdown"
            }
        )
        
        await super().stop()
        
    async def _heartbeat_loop(self) -> None:
        """Heartbeat loop to send health metrics."""
        while self.running:
            try:
                # Update health metrics with random variations
                self._update_health_metrics()
                
                # Send heartbeat
                await self.registry.process_heartbeat(
                    component_id=self.component_id,
                    instance_uuid=self.instance_uuid,
                    sequence=int(time.time()),  # Use timestamp as sequence
                    health_metrics=self.health_metrics,
                    metadata={
                        "uptime": time.time() - self.startup_time,
                    }
                )
            except Exception as e:
                logger.error(f"Error in heartbeat loop: {e}")
                
            # Wait before next heartbeat
            await asyncio.sleep(5)
            
    def _update_health_metrics(self) -> None:
        """Update health metrics with random variations."""
        # Add small random variations
        self.health_metrics["cpu_usage"] = min(0.95, max(0.05, self.health_metrics["cpu_usage"] + (random.random() - 0.5) * 0.1))
        self.health_metrics["memory_usage"] = min(0.95, max(0.05, self.health_metrics["memory_usage"] + (random.random() - 0.5) * 0.1))
        self.health_metrics["request_latency"] = max(10.0, self.health_metrics["request_latency"] + (random.random() - 0.5) * 10.0)
        self.health_metrics["error_rate"] = max(0.0, min(0.2, self.health_metrics["error_rate"] + (random.random() - 0.5) * 0.02))
        self.health_metrics["throughput"] = max(10.0, self.health_metrics["throughput"] + (random.random() - 0.5) * 20.0)
        
    async def _register_capabilities(self) -> None:
        """Register component capabilities."""
        # Register data processing capability
        await self.registry.register_capability(
            component_id=self.component_id,
            capability_name="process_data",
            capability_level=100,
            description="Process data with full functionality",
            parameters={
                "data": "object",
                "options": "object"
            },
            handler=self.process_data
        )
        
        # Register data retrieval capability
        await self.registry.register_capability(
            component_id=self.component_id,
            capability_name="retrieve_data",
            capability_level=100,
            description="Retrieve data with full functionality",
            parameters={
                "id": "string",
                "options": "object"
            },
            handler=self.retrieve_data
        )
    
    async def process_data(self, data: Dict[str, Any], options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process data with full functionality.
        
        Args:
            data: Data to process
            options: Optional processing options
            
        Returns:
            Processed data
        """
        # Simulate processing
        await asyncio.sleep(0.1)
        
        # Randomly fail to demonstrate degradation
        if random.random() < 0.1:
            raise Exception("Processing failed")
            
        # Process data
        result = {
            "id": data.get("id", str(random.randint(1000, 9999))),
            "processed": True,
            "timestamp": time.time(),
            "result": f"Processed by {self.component_id}: {data.get('value', 'unknown')}"
        }
        
        return result
    
    async def retrieve_data(self, id: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Retrieve data with full functionality.
        
        Args:
            id: Data ID
            options: Optional retrieval options
            
        Returns:
            Retrieved data
        """
        # Simulate retrieval
        await asyncio.sleep(0.05)
        
        # Randomly fail to demonstrate degradation
        if random.random() < 0.05:
            raise Exception("Retrieval failed")
            
        # Retrieve data
        result = {
            "id": id,
            "retrieved": True,
            "timestamp": time.time(),
            "data": {
                "value": f"Data for {id}",
                "source": self.component_id
            }
        }
        
        return result
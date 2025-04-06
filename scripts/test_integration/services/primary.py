#!/usr/bin/env python3
"""
Primary Service Module

Implements the primary service for testing.
"""

import time
import random
import asyncio
import logging
from typing import Dict, List, Any

from tekton.core.component_lifecycle import ComponentRegistry
from ..base import BaseService
from ..simulation import simulate_processing, simulate_request_activity

logger = logging.getLogger("tekton.test_integration.services.primary")


class PrimaryService(BaseService):
    """Primary service implementation for testing."""
    
    def __init__(self, 
                component_id: str,
                component_name: str,
                registry: ComponentRegistry):
        """
        Initialize primary service.
        
        Args:
            component_id: Component ID
            component_name: Human-readable name
            registry: Component registry
        """
        super().__init__(
            component_id=component_id,
            component_name=component_name,
            component_type="service",
            registry=registry
        )
        self.request_counter = 0
        self.error_counter = 0
        self.api_endpoint = f"/{component_id.replace('.', '/')}"
        
    async def _register_capabilities(self) -> None:
        """Register service capabilities."""
        # Register capabilities
        await self.registry.register_capability(
            component_id=self.component_id,
            capability_name="process_data",
            capability_level=100,
            description="Process data with full functionality",
            handler=self.process_data
        )
        
        await self.registry.register_capability(
            component_id=self.component_id,
            capability_name="query_data",
            capability_level=100,
            description="Query data with full functionality",
            handler=self.query_data
        )
        
        # Register dependencies
        self.health_adapter.add_dependency("test.database")
        
    async def start(self) -> bool:
        """
        Start the service.
        
        Returns:
            True if started successfully
        """
        success = await super().start()
        
        if success:
            # Start additional background tasks
            self.health_adapter.run_task(self._request_simulator)
            
        return success
        
    async def process_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process data with full functionality.
        
        Args:
            data: Data to process
            
        Returns:
            Processed data
        """
        self.request_counter += 1
        
        # Simulate processing
        success = await simulate_processing(0.05, 0.15, 0.1)
        
        if not success:
            self.error_counter += 1
            raise Exception(f"Failed to process data: random failure")
            
        # Process data
        result = {
            "id": data.get("id", str(random.randint(1000, 9999))),
            "processed": True,
            "timestamp": time.time(),
            "result": f"Processed by {self.component_id}: {data.get('value', 'unknown')}",
            "processor": self.component_name,
            "processing_time": random.random() * 0.1
        }
        
        return result
        
    async def query_data(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Query data with full functionality.
        
        Args:
            query: Query parameters
            
        Returns:
            Query results
        """
        self.request_counter += 1
        
        # Simulate query
        success = await simulate_processing(0.08, 0.23, 0.05)
        
        if not success:
            self.error_counter += 1
            raise Exception(f"Failed to query data: random failure")
            
        # Generate results
        count = query.get("count", 5)
        results = []
        
        for i in range(count):
            results.append({
                "id": f"result-{i+1}",
                "value": f"Result value {i+1}",
                "score": random.random(),
                "timestamp": time.time()
            })
            
        return {
            "query": query,
            "count": len(results),
            "results": results,
            "processor": self.component_name,
            "processing_time": random.random() * 0.2
        }
        
    async def _metrics_updater(self) -> None:
        """Background task to update metrics."""
        while self.running:
            try:
                # Update metrics
                self.health_adapter.update_metrics({
                    "cpu_usage": 0.2 + random.random() * 0.3,
                    "memory_usage": (100 + random.random() * 50) * 1024 * 1024,
                    "memory_limit": 512 * 1024 * 1024,
                    "request_count": self.request_counter,
                    "error_count": self.error_counter,
                    "request_rate": self.request_counter / (time.time() - self.health_adapter.start_time) if self.health_adapter.start_time else 0,
                    "error_rate": self.error_counter / max(1, self.request_counter)
                })
            except Exception as e:
                logger.error(f"Error updating metrics: {e}")
                
            # Wait before next update
            await asyncio.sleep(2)
            
    async def _request_simulator(self) -> None:
        """Background task to simulate requests."""
        while self.running:
            try:
                # Simulate request
                status_code = await simulate_request_activity(
                    self.health_adapter, 
                    self.api_endpoint,
                    self.request_counter,
                    self.error_counter
                )
                
                # If error, increment counter
                if status_code >= 400:
                    self.error_counter += 1
                    
                self.request_counter += 1
                
            except Exception as e:
                logger.error(f"Error in request simulator: {e}")
                
            # Wait before next request
            await asyncio.sleep(random.random() * 0.5)
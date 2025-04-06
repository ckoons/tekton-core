#!/usr/bin/env python3
"""
Backup Service Module

Implements the backup service with reduced functionality.
"""

import time
import random
import asyncio
import logging
from typing import Dict, List, Any

from tekton.core.component_lifecycle import ComponentRegistry
from ..base import BaseService
from ..simulation import simulate_processing

logger = logging.getLogger("tekton.test_integration.services.backup")


class BackupService(BaseService):
    """Backup service implementation with reduced functionality."""
    
    def __init__(self, 
                component_id: str,
                component_name: str,
                registry: ComponentRegistry,
                primary_service_id: str):
        """
        Initialize backup service.
        
        Args:
            component_id: Component ID
            component_name: Human-readable name
            registry: Component registry
            primary_service_id: ID of primary service to back up
        """
        super().__init__(
            component_id=component_id,
            component_name=component_name,
            component_type="backup",
            registry=registry
        )
        self.primary_service_id = primary_service_id
        
    async def _register_capabilities(self) -> None:
        """Register service capabilities."""
        # Register as fallback for primary service
        await self.registry.register_fallback_handler(
            component_id=self.primary_service_id,
            capability_name="process_data",
            provider_id=self.component_id,
            fallback_handler=self.process_data_fallback,
            capability_level=50
        )
        
        await self.registry.register_fallback_handler(
            component_id=self.primary_service_id,
            capability_name="query_data",
            provider_id=self.component_id,
            fallback_handler=self.query_data_fallback,
            capability_level=50
        )
        
    async def process_data_fallback(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process data with reduced functionality.
        
        Args:
            data: Data to process
            
        Returns:
            Processed data with fallback notice
        """
        # Simulate processing (faster than primary)
        await simulate_processing(0.01, 0.06, 0.01)
        
        # Process data
        result = {
            "id": data.get("id", str(random.randint(1000, 9999))),
            "processed": True,
            "timestamp": time.time(),
            "result": f"Fallback processing by {self.component_id}: {data.get('value', 'unknown')}",
            "processor": self.component_name,
            "processing_time": random.random() * 0.05,
            "fallback": True,
            "limitations": ["Simplified processing", "Limited features"]
        }
        
        return result
        
    async def query_data_fallback(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """
        Query data with reduced functionality.
        
        Args:
            query: Query parameters
            
        Returns:
            Query results with fallback notice
        """
        # Simulate query (faster than primary)
        await simulate_processing(0.03, 0.1, 0.02)
        
        # Limit result count
        count = min(query.get("count", 5), 2)
        results = []
        
        for i in range(count):
            results.append({
                "id": f"result-{i+1}",
                "value": f"Fallback result {i+1}",
                "timestamp": time.time()
            })
            
        return {
            "query": query,
            "count": len(results),
            "results": results,
            "processor": self.component_name,
            "processing_time": random.random() * 0.1,
            "fallback": True,
            "limitations": ["Reduced result count", "Limited fields"]
        }
        
    async def _metrics_updater(self) -> None:
        """Background task to update metrics."""
        while self.running:
            try:
                # Update metrics (lower usage than primary)
                self.health_adapter.update_metrics({
                    "cpu_usage": 0.1 + random.random() * 0.1,
                    "memory_usage": (50 + random.random() * 30) * 1024 * 1024,
                    "memory_limit": 256 * 1024 * 1024
                })
            except Exception as e:
                logger.error(f"Error updating metrics: {e}")
                
            # Wait before next update
            await asyncio.sleep(3)
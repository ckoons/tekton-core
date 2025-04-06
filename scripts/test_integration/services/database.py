#!/usr/bin/env python3
"""
Database Service Module

Implements the database service for testing.
"""

import time
import random
import asyncio
import logging
from typing import Dict, List, Any

from tekton.core.component_lifecycle import ComponentRegistry
from ..base import BaseService
from ..simulation import simulate_processing, simulate_db_connections

logger = logging.getLogger("tekton.test_integration.services.database")


class DatabaseService(BaseService):
    """Database service implementation for testing."""
    
    def __init__(self, 
                component_id: str,
                component_name: str,
                registry: ComponentRegistry):
        """
        Initialize database service.
        
        Args:
            component_id: Component ID
            component_name: Human-readable name
            registry: Component registry
        """
        super().__init__(
            component_id=component_id,
            component_name=component_name,
            component_type="database",
            registry=registry
        )
        self.query_counter = 0
        self.connection_counter = 0
        self.error_counter = 0
        
    async def _register_capabilities(self) -> None:
        """Register database capabilities."""
        # Register capabilities
        await self.registry.register_capability(
            component_id=self.component_id,
            capability_name="query",
            capability_level=100,
            description="Query database",
            handler=self.query
        )
        
        await self.registry.register_capability(
            component_id=self.component_id,
            capability_name="store",
            capability_level=100,
            description="Store data in database",
            handler=self.store
        )
        
    async def start(self) -> bool:
        """
        Start the service.
        
        Returns:
            True if started successfully
        """
        success = await super().start()
        
        if success:
            # Start additional background tasks
            self.health_adapter.run_task(self._connection_simulator)
            
        return success
        
    async def query(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """
        Query the database.
        
        Args:
            query: Query parameters
            
        Returns:
            Query results
        """
        self.query_counter += 1
        
        # Simulate query
        success = await simulate_processing(0.05, 0.25, 0.05)
        
        if not success:
            self.error_counter += 1
            raise Exception(f"Database query failed: random failure")
            
        # Generate results
        count = query.get("count", 5)
        results = []
        
        for i in range(count):
            results.append({
                "id": f"db-{i+1}",
                "value": f"Database record {i+1}",
                "created_at": time.time() - random.random() * 3600
            })
            
        return {
            "query": query,
            "count": len(results),
            "results": results,
            "query_time": random.random() * 0.2
        }
        
    async def store(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Store data in the database.
        
        Args:
            data: Data to store
            
        Returns:
            Store result
        """
        # Simulate storage
        success = await simulate_processing(0.1, 0.4, 0.03)
        
        if not success:
            self.error_counter += 1
            raise Exception(f"Database storage failed: random failure")
            
        return {
            "success": True,
            "id": f"db-{random.randint(1000, 9999)}",
            "timestamp": time.time()
        }
        
    async def _metrics_updater(self) -> None:
        """Background task to update metrics."""
        while self.running:
            try:
                # Update metrics
                self.health_adapter.update_metrics({
                    "cpu_usage": 0.3 + random.random() * 0.2,
                    "memory_usage": (200 + random.random() * 100) * 1024 * 1024,
                    "memory_limit": 1024 * 1024 * 1024,
                    "query_count": self.query_counter,
                    "connection_count": self.connection_counter,
                    "error_count": self.error_counter
                })
            except Exception as e:
                logger.error(f"Error updating metrics: {e}")
                
            # Wait before next update
            await asyncio.sleep(2)
            
    async def _connection_simulator(self) -> None:
        """Background task to simulate database connections."""
        while self.running:
            try:
                # Simulate connections
                self.connection_counter, self.query_counter, self.error_counter = (
                    await simulate_db_connections(
                        self.connection_counter,
                        self.query_counter,
                        self.error_counter
                    )
                )
                
            except Exception as e:
                logger.error(f"Error in connection simulator: {e}")
                
            # Wait before next simulation
            await asyncio.sleep(random.random() * 0.5)
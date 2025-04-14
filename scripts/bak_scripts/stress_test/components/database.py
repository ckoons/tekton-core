#!/usr/bin/env python3
"""
Database Component Module

Implements the database component for stress testing.
"""

import time
import random
import asyncio
import logging
from typing import Dict, Any

from tekton.core.component_lifecycle import ComponentRegistry

from ..config import DB_ERROR_RATE, NUM_DATABASES
from .base import BaseComponent

logger = logging.getLogger("tekton.stress_test.components.database")


class StressTestDatabase(BaseComponent):
    """Database implementation for stress testing."""
    
    def __init__(self, 
                component_id: str,
                component_name: str,
                registry: ComponentRegistry,
                database_index: int):
        """
        Initialize stress test database.
        
        Args:
            component_id: Component ID
            component_name: Human-readable name
            registry: Component registry
            database_index: Database index for metrics
        """
        super().__init__(
            component_id=component_id,
            component_name=component_name,
            component_type="database",
            registry=registry
        )
        self.database_index = database_index
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
        
    async def query(self, query: str) -> Dict[str, Any]:
        """
        Query the database.
        
        Args:
            query: Query string
            
        Returns:
            Query results
        """
        self.query_counter += 1
        
        # Simulate query
        await asyncio.sleep(0.005 + random.random() * 0.01)
        
        # Randomly fail with configured probability
        if random.random() < DB_ERROR_RATE:
            self.error_counter += 1
            raise Exception(f"Database query failed: {query}")
            
        # Generate results
        return {
            "query": query,
            "timestamp": time.time(),
            "database": self.component_id,
            "results": random.randint(1, 5)
        }
        
    async def _metrics_updater(self) -> None:
        """Background task to update metrics."""
        while self.running:
            try:
                # Update connection counter randomly
                if random.random() < 0.3:
                    self.connection_counter += random.randint(1, 3)
                if random.random() < 0.2 and self.connection_counter > 0:
                    self.connection_counter -= random.randint(1, 2)
                    
                # Calculate CPU and memory based on database index and query rate
                base_cpu = 0.2 + (self.database_index / NUM_DATABASES) * 0.1
                query_factor = min(1.0, self.query_counter / 10000) * 0.5
                
                cpu_usage = base_cpu + query_factor + (random.random() * 0.1)
                memory_usage = (200 + (self.database_index * 50) + (self.query_counter / 100)) * 1024 * 1024
                
                # Update metrics
                self.health_adapter.update_metrics({
                    "cpu_usage": min(1.0, cpu_usage),
                    "memory_usage": memory_usage,
                    "memory_limit": 1024 * 1024 * 1024,
                    "query_count": self.query_counter,
                    "connection_count": self.connection_counter,
                    "error_count": self.error_counter,
                    "error_rate": self.error_counter / max(1, self.query_counter),
                    "database_index": self.database_index
                })
            except Exception as e:
                logger.error(f"Error updating metrics: {e}")
                
            # Wait before next update
            await asyncio.sleep(1)
#!/usr/bin/env python3
"""
Service Component Module

Implements the service component for stress testing.
"""

import time
import random
import asyncio
import logging
from typing import Dict, List, Any

from tekton.core.lifecycle import ComponentState
from tekton.core.component_lifecycle import ComponentRegistry

from ..config import FAILURE_PROBABILITY, RECOVERY_PROBABILITY
from .base import BaseComponent

logger = logging.getLogger("tekton.stress_test.components.service")


class StressTestService(BaseComponent):
    """Service implementation for stress testing."""
    
    def __init__(self, 
                component_id: str,
                component_name: str,
                registry: ComponentRegistry,
                service_index: int,
                database_dependency: str):
        """
        Initialize stress test service.
        
        Args:
            component_id: Component ID
            component_name: Human-readable name
            registry: Component registry
            service_index: Service index for metrics
            database_dependency: Database component to depend on
        """
        super().__init__(
            component_id=component_id,
            component_name=component_name,
            component_type="service",
            registry=registry
        )
        self.service_index = service_index
        self.database_dependency = database_dependency
        self.request_counter = 0
        self.error_counter = 0
        self.last_failure = 0
        self.failure_duration = 0
        self.in_failure_mode = False
        self.circuit_breaker = None
        
    async def start(self) -> bool:
        """
        Start the service.
        
        Returns:
            True if started successfully
        """
        success = await super().start()
        
        if success:
            # Register dependencies
            self.health_adapter.add_dependency(self.database_dependency)
            
            # Create circuit breaker
            self.circuit_breaker = self.health_adapter.create_circuit_breaker(
                name="database_access",
                failure_threshold=3,
                recovery_timeout=5.0
            )
            
            # Start additional background tasks
            self.health_adapter.run_task(self._failure_simulator)
            
        return success
        
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
        
    async def process_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process data with full functionality.
        
        Args:
            data: Data to process
            
        Returns:
            Processed data
        """
        # Check if in failure mode
        if self.in_failure_mode:
            self.error_counter += 1
            raise Exception(f"Service in failure mode")
            
        self.request_counter += 1
        
        # Simulate processing
        await asyncio.sleep(0.01 + random.random() * 0.05)
        
        try:
            # Try to access database using circuit breaker
            db_result = await self.circuit_breaker.execute(
                self._access_database,
                data.get("query", "default")
            )
            
            # Process data
            result = {
                "id": data.get("id", str(random.randint(1000, 9999))),
                "processed": True,
                "timestamp": time.time(),
                "result": f"Processed by {self.component_id}: {data.get('value', 'unknown')}",
                "db_result": db_result,
                "processor": self.component_name,
                "processing_time": random.random() * 0.1
            }
            
            return result
            
        except Exception as e:
            self.error_counter += 1
            raise Exception(f"Failed to process data: {e}")
            
    async def _access_database(self, query: str) -> Dict[str, Any]:
        """
        Access database with circuit breaker protection.
        
        Args:
            query: Database query
            
        Returns:
            Database result
        """
        # Simulate database access
        await asyncio.sleep(0.01 + random.random() * 0.03)
        
        # Randomly fail with 10% probability
        if random.random() < 0.1:
            raise Exception(f"Database access failed")
            
        return {
            "query": query,
            "timestamp": time.time(),
            "records": random.randint(1, 10)
        }
        
    async def _metrics_updater(self) -> None:
        """Background task to update metrics."""
        while self.running:
            try:
                # Calculate CPU and memory based on service index and request rate
                base_cpu = 0.1 + (self.service_index / 10) * 0.1
                request_factor = min(1.0, self.request_counter / 1000) * 0.3
                error_factor = min(1.0, self.error_counter / max(1, self.request_counter)) * 0.3
                
                cpu_usage = base_cpu + request_factor + error_factor + (random.random() * 0.1)
                memory_usage = (100 + (self.service_index * 20) + (self.request_counter / 10)) * 1024 * 1024
                
                # Update metrics
                self.health_adapter.update_metrics({
                    "cpu_usage": min(1.0, cpu_usage),
                    "memory_usage": memory_usage,
                    "memory_limit": 512 * 1024 * 1024,
                    "request_count": self.request_counter,
                    "error_count": self.error_counter,
                    "error_rate": self.error_counter / max(1, self.request_counter),
                    "service_index": self.service_index
                })
            except Exception as e:
                logger.error(f"Error updating metrics: {e}")
                
            # Wait before next update
            await asyncio.sleep(1)
            
    async def _failure_simulator(self) -> None:
        """Background task to simulate service failures and recovery."""
        # Wait a bit before starting to simulate failures
        await asyncio.sleep(10)
        
        while self.running:
            try:
                current_time = time.time()
                
                # If not in failure mode, check if should enter failure mode
                if not self.in_failure_mode:
                    if random.random() < (FAILURE_PROBABILITY / 10):  # Distribute probability over time
                        self.in_failure_mode = True
                        self.last_failure = current_time
                        self.failure_duration = random.randint(5, 15)  # Fail for 5-15 seconds
                        
                        logger.warning(f"Service {self.component_id} entering failure mode for {self.failure_duration}s")
                        
                        # Update state to degraded or error
                        if random.random() < 0.5:
                            self.health_adapter.update_state(
                                ComponentState.DEGRADED.value,
                                reason="test.failure_simulation",
                                details=f"Simulated failure for {self.failure_duration}s"
                            )
                        else:
                            self.health_adapter.update_state(
                                ComponentState.ERROR.value,
                                reason="test.failure_simulation",
                                details=f"Simulated error for {self.failure_duration}s"
                            )
                
                # If in failure mode, check if should recover
                elif current_time - self.last_failure > self.failure_duration:
                    if random.random() < RECOVERY_PROBABILITY:
                        self.in_failure_mode = False
                        
                        logger.info(f"Service {self.component_id} recovering from failure mode")
                        
                        # Update state to ready
                        self.health_adapter.update_state(
                            ComponentState.READY.value,
                            reason="test.failure_recovery",
                            details="Recovered from simulated failure"
                        )
                    else:
                        # Extend failure duration
                        self.failure_duration += random.randint(3, 8)
                        logger.warning(f"Service {self.component_id} extending failure mode for {self.failure_duration}s")
                        
            except Exception as e:
                logger.error(f"Error in failure simulator: {e}")
                
            # Wait before next check
            await asyncio.sleep(1)
#!/usr/bin/env python3
"""
Test Client Module

Implements the client for stress testing.
"""

import time
import random
import asyncio
import logging
from typing import Dict, List, Any

from tekton.core.component_lifecycle import ComponentRegistry
from tekton.core.graceful_degradation import NoFallbackAvailableError

from ..utils import calculate_statistics

logger = logging.getLogger("tekton.stress_test.clients.test_client")


class StressTestClient:
    """Client implementation for stress testing."""
    
    def __init__(self, 
                client_id: str,
                registry: ComponentRegistry,
                service_ids: List[str],
                request_rate: float = 10.0):
        """
        Initialize stress test client.
        
        Args:
            client_id: Client ID
            registry: Component registry
            service_ids: List of service component IDs
            request_rate: Requests per second
        """
        self.client_id = client_id
        self.registry = registry
        self.service_ids = service_ids
        self.request_rate = request_rate
        self.running = False
        self.request_count = 0
        self.success_count = 0
        self.error_count = 0
        self.latencies = []
        self.start_time = 0.0
        
    async def start(self) -> None:
        """Start the client."""
        self.running = True
        self.start_time = time.time()
        
        # Start client task
        self.task = asyncio.create_task(self._client_loop())
        
        logger.info(f"Started test client {self.client_id} (rate: {self.request_rate} req/s)")
        
    async def stop(self) -> None:
        """Stop the client."""
        if not self.running:
            return
            
        self.running = False
        
        # Cancel task
        if hasattr(self, "task"):
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
            
        logger.info(f"Stopped test client {self.client_id}")
        
    async def _client_loop(self) -> None:
        """Main client loop."""
        # Calculate sleep time between requests
        sleep_time = 1.0 / self.request_rate
        
        while self.running:
            try:
                # Choose a random service
                service_id = random.choice(self.service_ids)
                
                # Create request data
                data = {
                    "id": f"{self.client_id}-{self.request_count}",
                    "value": f"Test value {random.randint(1, 100)}",
                    "timestamp": time.time(),
                    "query": f"query-{random.randint(1, 10)}"
                }
                
                # Process data
                await self._send_request(service_id, data)
                
            except Exception as e:
                logger.error(f"Error in client loop: {e}")
                
            # Wait before next request (adjust for varying load)
            jitter = random.random() * 0.2 * sleep_time
            await asyncio.sleep(sleep_time + jitter)
            
    async def _send_request(self, service_id: str, data: Dict[str, Any]) -> None:
        """
        Send a request to a service.
        
        Args:
            service_id: Service ID
            data: Request data
        """
        self.request_count += 1
        start_time = time.time()
        
        try:
            # Call service
            result = await self.registry.execute_with_fallback(
                component_id=service_id,
                capability_name="process_data",
                data=data
            )
            
            duration = time.time() - start_time
            self.latencies.append(duration)
            self.success_count += 1
            
        except NoFallbackAvailableError:
            duration = time.time() - start_time
            self.latencies.append(duration)
            self.error_count += 1
        except Exception as e:
            duration = time.time() - start_time
            self.latencies.append(duration)
            self.error_count += 1
            
    def get_stats(self) -> Dict[str, Any]:
        """
        Get client statistics.
        
        Returns:
            Statistics dictionary
        """
        # Calculate latency statistics
        latency_stats = calculate_statistics(self.latencies)
        
        # Calculate effective request rate
        duration = time.time() - self.start_time if self.start_time > 0 else 1
        effective_rate = self.request_count / duration if duration > 0 else 0
        
        return {
            "client_id": self.client_id,
            "target_rate": self.request_rate,
            "effective_rate": effective_rate,
            "request_count": self.request_count,
            "success_count": self.success_count,
            "error_count": self.error_count,
            "success_rate": self.success_count / max(1, self.request_count),
            "error_rate": self.error_count / max(1, self.request_count),
            "latency": latency_stats
        }
#!/usr/bin/env python3
"""
Test Client Module

Implements client for testing services.
"""

import time
import json
import random
import asyncio
import logging
from typing import Dict, List, Any

from tekton.core.component_lifecycle import ComponentRegistry
from tekton.core.graceful_degradation import NoFallbackAvailableError

logger = logging.getLogger("tekton.test_integration.client")


class TestClient:
    """Test client for the services."""
    
    def __init__(self, 
                client_id: str,
                registry: ComponentRegistry,
                primary_service_id: str):
        """
        Initialize test client.
        
        Args:
            client_id: Client ID
            registry: Component registry
            primary_service_id: ID of primary service to use
        """
        self.client_id = client_id
        self.registry = registry
        self.primary_service_id = primary_service_id
        self.running = False
        self.request_count = 0
        self.success_count = 0
        self.error_count = 0
        self.fallback_count = 0
        
    async def start(self) -> None:
        """Start the client."""
        self.running = True
        
        # Start client task
        self.task = asyncio.create_task(self._client_loop())
        
        logger.info(f"Started test client {self.client_id}")
        
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
        while self.running:
            try:
                # Choose an operation
                operation = random.choice(["process_data", "query_data"])
                
                # Create request data
                if operation == "process_data":
                    data = {
                        "id": f"req-{random.randint(1000, 9999)}",
                        "value": f"Test value {random.randint(1, 100)}",
                        "timestamp": time.time()
                    }
                    
                    # Process data
                    await self._process_data(data)
                    
                else:  # query_data
                    query = {
                        "id": f"query-{random.randint(1000, 9999)}",
                        "filter": f"test-{random.randint(1, 10)}",
                        "count": random.randint(1, 5)
                    }
                    
                    # Query data
                    await self._query_data(query)
                    
            except Exception as e:
                logger.error(f"Error in client loop: {e}")
                
            # Wait before next request
            await asyncio.sleep(random.random() * 0.5 + 0.5)
            
    async def _process_data(self, data: Dict[str, Any]) -> None:
        """
        Process data using the primary service.
        
        Args:
            data: Data to process
        """
        self.request_count += 1
        start_time = time.time()
        
        try:
            # Call service with fallback
            result = await self.registry.execute_with_fallback(
                component_id=self.primary_service_id,
                capability_name="process_data",
                data=data
            )
            
            duration = time.time() - start_time
            
            # Check if fallback was used
            if result.get("fallback"):
                self.fallback_count += 1
                logger.info(f"Used fallback for process_data: {duration:.3f}s")
            else:
                self.success_count += 1
                logger.info(f"Successfully processed data: {duration:.3f}s")
                
        except NoFallbackAvailableError:
            duration = time.time() - start_time
            self.error_count += 1
            logger.warning(f"All fallbacks failed for process_data: {duration:.3f}s")
        except Exception as e:
            duration = time.time() - start_time
            self.error_count += 1
            logger.error(f"Error processing data: {e} ({duration:.3f}s)")
            
    async def _query_data(self, query: Dict[str, Any]) -> None:
        """
        Query data using the primary service.
        
        Args:
            query: Query parameters
        """
        self.request_count += 1
        start_time = time.time()
        
        try:
            # Call service with fallback
            result = await self.registry.execute_with_fallback(
                component_id=self.primary_service_id,
                capability_name="query_data",
                query=query
            )
            
            duration = time.time() - start_time
            
            # Check if fallback was used
            if result.get("fallback"):
                self.fallback_count += 1
                logger.info(f"Used fallback for query_data: {duration:.3f}s")
            else:
                self.success_count += 1
                logger.info(f"Successfully queried data: {duration:.3f}s")
                
        except NoFallbackAvailableError:
            duration = time.time() - start_time
            self.error_count += 1
            logger.warning(f"All fallbacks failed for query_data: {duration:.3f}s")
        except Exception as e:
            duration = time.time() - start_time
            self.error_count += 1
            logger.error(f"Error querying data: {e} ({duration:.3f}s)")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get client statistics.
        
        Returns:
            Statistics dictionary
        """
        return {
            "client_id": self.client_id,
            "request_count": self.request_count,
            "success_count": self.success_count,
            "error_count": self.error_count,
            "fallback_count": self.fallback_count,
            "success_rate": self.success_count / max(1, self.request_count),
            "error_rate": self.error_count / max(1, self.request_count),
            "fallback_rate": self.fallback_count / max(1, self.request_count)
        }
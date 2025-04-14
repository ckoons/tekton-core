#!/usr/bin/env python3
"""
Simulation Utilities

Utilities for simulating requests, connections, and metrics.
"""

import time
import random
import asyncio
import logging
from typing import Dict, Any, Optional, Callable


logger = logging.getLogger("tekton.test_integration.simulation")


async def simulate_processing(min_time: float = 0.05, max_time: float = 0.15, 
                           error_rate: float = 0.1) -> bool:
    """
    Simulate processing with random latency and errors.
    
    Args:
        min_time: Minimum processing time
        max_time: Maximum processing time
        error_rate: Probability of error
        
    Returns:
        True if successful, False if should raise error
    """
    # Simulate processing time
    await asyncio.sleep(min_time + random.random() * (max_time - min_time))
    
    # Check for random error
    return random.random() >= error_rate


async def simulate_request_activity(health_adapter, api_endpoint: str, 
                                  request_counter: int, error_counter: int):
    """
    Simulate API request activity for metrics.
    
    Args:
        health_adapter: Component health adapter
        api_endpoint: API endpoint to simulate
        request_counter: Current request counter
        error_counter: Current error counter
    """
    # Simulate incoming request
    method = random.choice(["GET", "POST"])
    path = f"{api_endpoint}/{random.choice(['query', 'process'])}"
    
    # Random latency
    latency = 0.01 + random.random() * 0.1
    
    # Random status code with 90% success
    status_code = random.choice([200] * 9 + [500])
    
    # Log request
    health_adapter.log_request(
        endpoint=path,
        method=method,
        status_code=status_code,
        duration=latency,
        request_id=f"req-{random.randint(1000, 9999)}",
        context={"simulated": True}
    )
    
    return status_code


async def simulate_db_connections(connection_counter: int, query_counter: int, 
                                error_counter: int) -> tuple:
    """
    Simulate database connection activity.
    
    Args:
        connection_counter: Current connection counter
        query_counter: Current query counter
        error_counter: Current error counter
        
    Returns:
        Updated (connection_counter, query_counter, error_counter)
    """
    # Randomly add or remove connections
    if random.random() < 0.7:
        # Add connection
        connection_counter += 1
    elif connection_counter > 0:
        # Remove connection
        connection_counter -= 1
        
    # Randomly add queries
    if random.random() < 0.8:
        # Add queries
        query_count = random.randint(1, 5)
        query_counter += query_count
        
        # Randomly add errors
        if random.random() < 0.05:
            error_counter += 1
            
    return connection_counter, query_counter, error_counter

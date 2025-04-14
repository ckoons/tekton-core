#!/usr/bin/env python3
"""
Test Client Module

Provides a test client for component capabilities with fallback.
"""

import logging
from typing import Dict, Any, List

from tekton.core.component_lifecycle import ComponentRegistry
from tekton.core.graceful_degradation import NoFallbackAvailableError

logger = logging.getLogger("tekton.test_lifecycle.client")


async def client_test(registry: ComponentRegistry, target_component_id: str) -> None:
    """
    Test client for component capabilities with fallback.
    
    Args:
        registry: Component registry
        target_component_id: ID of target component
    """
    logger.info(f"Starting client test for {target_component_id}")
    
    # Test data
    test_data = [
        {"id": "1", "value": "First value"},
        {"id": "2", "value": "Second value"},
        {"id": "3", "value": "Third value"},
        {"id": "4", "value": "Fourth value"},
        {"id": "5", "value": "Fifth value"}
    ]
    
    # Process data with fallback
    logger.info("Testing data processing capability with fallback:")
    for data in test_data:
        try:
            result = await registry.execute_with_fallback(
                component_id=target_component_id,
                capability_name="process_data",
                data=data
            )
            logger.info(f"Processing result: {result}")
        except NoFallbackAvailableError as e:
            logger.error(f"Failed to process data {data['id']}: {e}")
    
    # Retrieve data with fallback
    logger.info("Testing data retrieval capability with fallback:")
    for data in test_data:
        try:
            result = await registry.execute_with_fallback(
                component_id=target_component_id,
                capability_name="retrieve_data",
                id=data["id"]
            )
            logger.info(f"Retrieval result: {result}")
        except NoFallbackAvailableError as e:
            logger.error(f"Failed to retrieve data {data['id']}: {e}")
    
    # Get fallback status
    status = await registry.get_fallback_status(target_component_id)
    logger.info(f"Fallback status: {status}")

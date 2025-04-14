#!/usr/bin/env python3
"""
Test Runner Module

Provides a runner for component lifecycle tests.
"""

import os
import asyncio
import logging
from typing import Dict, Any, Optional

from tekton.core.component_lifecycle import ComponentRegistry

from .components import TestComponent, FallbackComponent, EmergencyFallbackComponent
from .client import client_test

logger = logging.getLogger("tekton.test_lifecycle.runner")


async def run_lifecycle_test() -> None:
    """Run the component lifecycle test."""
    # Create temporary data directory
    data_dir = "/tmp/tekton_test_lifecycle"
    os.makedirs(data_dir, exist_ok=True)
    
    # Create component registry
    registry = ComponentRegistry(data_dir=data_dir)
    
    # Create main component
    main_component = TestComponent(
        component_id="test.main",
        component_name="Test Main Component",
        component_type="service",
        registry=registry
    )
    
    # Create fallback component
    fallback_component = FallbackComponent(
        component_id="test.fallback",
        component_name="Test Fallback Component",
        registry=registry,
        target_component_id="test.main"
    )
    
    # Create emergency fallback component
    emergency_component = EmergencyFallbackComponent(
        component_id="test.emergency",
        component_name="Test Emergency Fallback",
        registry=registry,
        target_component_id="test.main"
    )
    
    try:
        # Start monitoring
        monitor_task = asyncio.create_task(registry.monitor_components(heartbeat_timeout=10))
        
        # Start components
        await main_component.start()
        await fallback_component.start()
        await emergency_component.start()
        
        # Wait for components to be fully ready
        await asyncio.sleep(2)
        
        # Run client tests
        await client_test(registry, "test.main")
        
        # Wait a bit for fallback statistics to accumulate
        await asyncio.sleep(2)
        
        # Get fallback status
        status = await registry.get_fallback_status()
        logger.info(f"Final fallback status: {status}")
        
    finally:
        # Stop components
        await main_component.stop()
        
        # Cancel monitoring
        monitor_task.cancel()
        
        logger.info("Test complete")

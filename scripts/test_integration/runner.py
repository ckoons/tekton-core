#!/usr/bin/env python3
"""
Test Runner Module

Coordinates running the integration test.
"""

import os
import json
import time
import asyncio
import logging
from typing import Dict, Any

from tekton.core.lifecycle import ComponentState
from tekton.core.component_lifecycle import ComponentRegistry

from .services import PrimaryService, BackupService, DatabaseService
from .client import TestClient

logger = logging.getLogger("tekton.test_integration.runner")


async def run_test() -> None:
    """Run the end-to-end integration test."""
    # Create data directory
    data_dir = "/tmp/tekton_integration_test"
    os.makedirs(data_dir, exist_ok=True)
    
    # Create component registry
    registry = ComponentRegistry(data_dir=data_dir)
    
    # Create components
    primary_service = PrimaryService(
        component_id="test.primary",
        component_name="Test Primary Service",
        registry=registry
    )
    
    backup_service = BackupService(
        component_id="test.backup",
        component_name="Test Backup Service",
        registry=registry,
        primary_service_id="test.primary"
    )
    
    database_service = DatabaseService(
        component_id="test.database",
        component_name="Test Database",
        registry=registry
    )
    
    # Create test client
    test_client = TestClient(
        client_id="test.client",
        registry=registry,
        primary_service_id="test.primary"
    )
    
    try:
        # Start monitoring task
        monitor_task = asyncio.create_task(registry.monitor_components(heartbeat_timeout=10))
        
        # Start components
        logger.info("Starting components...")
        await database_service.start()
        await primary_service.start()
        await backup_service.start()
        
        # Start test client
        await test_client.start()
        
        # Wait for test to run
        logger.info("Test running, press Ctrl+C to stop...")
        for i in range(6):
            if i == 3:
                # Simulate degraded state in primary service
                logger.info("Simulating degraded state in primary service...")
                primary_service.health_adapter.update_state(
                    ComponentState.DEGRADED.value,
                    reason="test.simulation",
                    details="Simulating degraded state for testing"
                )
            
            await asyncio.sleep(5)
            
            # Print stats
            client_stats = test_client.get_stats()
            logger.info(f"Client stats: {json.dumps(client_stats)}")
            
        # Reset primary service state
        primary_service.health_adapter.update_state(ComponentState.READY.value, reason="test.simulation.end")
        
        # Wait a bit more
        await asyncio.sleep(5)
        
        # Get final stats
        client_stats = test_client.get_stats()
        logger.info(f"Final client stats: {json.dumps(client_stats)}")
        
    except KeyboardInterrupt:
        logger.info("Test interrupted by user")
    except Exception as e:
        logger.exception(f"Test error: {e}")
    finally:
        # Stop all components
        logger.info("Stopping components...")
        await test_client.stop()
        await primary_service.stop()
        await backup_service.stop()
        await database_service.stop()
        
        # Cancel monitoring
        monitor_task.cancel()
        try:
            await monitor_task
        except asyncio.CancelledError:
            pass
            
        logger.info("Test complete")
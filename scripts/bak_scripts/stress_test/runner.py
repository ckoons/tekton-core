#!/usr/bin/env python3
"""
Stress Test Runner

Coordinates running the stress test.
"""

import os
import json
import time
import random
import asyncio
import logging
from typing import Dict, List, Any

from .utils import calculate_statistics

from tekton.core.component_lifecycle import ComponentRegistry

from .config import (
    NUM_SERVICES, NUM_DATABASES, NUM_CLIENTS, 
    TEST_DURATION, DATA_DIR, BASE_REQUEST_RATE
)
from .components import StressTestService, StressTestDatabase
from .clients import StressTestClient
from .utils import get_elapsed_time, format_stats_summary

logger = logging.getLogger("tekton.stress_test.runner")


async def run_stress_test() -> None:
    """Run the stress test."""
    # Create data directory
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # Create component registry
    registry = ComponentRegistry(data_dir=DATA_DIR)
    
    # Create databases
    databases = []
    database_ids = []
    for i in range(NUM_DATABASES):
        db = StressTestDatabase(
            component_id=f"test.db.{i+1}",
            component_name=f"Test Database {i+1}",
            registry=registry,
            database_index=i
        )
        databases.append(db)
        database_ids.append(db.component_id)
    
    # Create services
    services = []
    service_ids = []
    for i in range(NUM_SERVICES):
        # Assign each service to a random database
        db_id = random.choice(database_ids)
        
        service = StressTestService(
            component_id=f"test.service.{i+1}",
            component_name=f"Test Service {i+1}",
            registry=registry,
            service_index=i,
            database_dependency=db_id
        )
        services.append(service)
        service_ids.append(service.component_id)
    
    # Create clients
    clients = []
    for i in range(NUM_CLIENTS):
        # Vary request rate across clients
        rate_multiplier = 1.0 + (i / NUM_CLIENTS)
        request_rate = BASE_REQUEST_RATE * rate_multiplier
        
        client = StressTestClient(
            client_id=f"test.client.{i+1}",
            registry=registry,
            service_ids=service_ids,
            request_rate=request_rate
        )
        clients.append(client)
    
    try:
        # Start monitoring task
        monitor_task = asyncio.create_task(registry.monitor_components(heartbeat_timeout=5))
        
        # Start databases
        logger.info("Starting databases...")
        for db in databases:
            await db.start()
            
        # Start services
        logger.info("Starting services...")
        for service in services:
            await service.start()
            
        # Start clients
        logger.info("Starting clients...")
        for client in clients:
            await client.start()
            # Stagger client starts
            await asyncio.sleep(0.5)
            
        # Record test start time
        test_start = time.time()
        logger.info(f"Stress test running for {TEST_DURATION} seconds...")
        
        # Run for the specified duration
        progress_interval = min(TEST_DURATION // 5, 10)  # Progress report every 10 seconds or less
        for i in range(0, TEST_DURATION, progress_interval):
            await asyncio.sleep(progress_interval)
            
            # Print status
            elapsed, formatted = get_elapsed_time(test_start)
            total_requests = sum(client.request_count for client in clients)
            total_errors = sum(client.error_count for client in clients)
            error_rate = total_errors / max(1, total_requests)
            
            logger.info(f"Status at {formatted}: {total_requests} requests, "
                       f"{total_errors} errors ({error_rate:.1%} error rate)")
            
        # Wait for any remaining time
        remaining = TEST_DURATION - (time.time() - test_start)
        if remaining > 0:
            await asyncio.sleep(remaining)
            
        # Print final statistics
        logger.info("Test completed. Final statistics:")
        
        # Aggregate client stats
        total_requests = sum(client.request_count for client in clients)
        total_successes = sum(client.success_count for client in clients)
        total_errors = sum(client.error_count for client in clients)
        all_latencies = []
        for client in clients:
            all_latencies.extend(client.latencies)
        
        # Calculate overall stats
        test_duration = time.time() - test_start
        overall_stats = {
            "duration": test_duration,
            "total_requests": total_requests,
            "total_successes": total_successes,
            "total_errors": total_errors,
            "success_rate": total_successes / max(1, total_requests),
            "error_rate": total_errors / max(1, total_requests),
            "requests_per_second": total_requests / test_duration,
            "latency": calculate_statistics(all_latencies)
        }
        
        logger.info(f"Overall: {format_stats_summary(overall_stats)}")
        
        # Print client stats
        for client in clients:
            stats = client.get_stats()
            logger.info(f"Client {client.client_id}: {json.dumps(stats, indent=2)}")
            
    except KeyboardInterrupt:
        logger.info("Test interrupted by user")
    except Exception as e:
        logger.exception(f"Test error: {e}")
    finally:
        # Stop all components
        logger.info("Stopping components...")
        
        # Stop clients
        for client in clients:
            await client.stop()
            
        # Stop services
        for service in services:
            await service.stop()
            
        # Stop databases
        for db in databases:
            await db.stop()
            
        # Cancel monitoring
        monitor_task.cancel()
        try:
            await monitor_task
        except asyncio.CancelledError:
            pass
            
        logger.info("Test complete")
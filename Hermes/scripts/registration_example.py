#!/usr/bin/env python3
"""
Unified Registration Protocol Example - Demonstrates component registration.

This script demonstrates how Tekton components can register with the Hermes
registration system using the Unified Registration Protocol.
"""

import os
import sys
import logging
import asyncio
import time
import argparse
import uuid
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("hermes.registration_example")

# Add project root to Python path if needed
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from hermes.core.message_bus import MessageBus
from hermes.core.service_discovery import ServiceRegistry
from hermes.core.registration import RegistrationManager, RegistrationClient
from hermes.api.client import HermesClient


async def run_registration_server(secret_key: str, host: str = "localhost", port: int = 5555) -> None:
    """
    Run a registration server for demonstration purposes.
    
    This function sets up and runs a registration server using the
    RegistrationManager class.
    
    Args:
        secret_key: Secret key for token generation/validation
        host: Host for the message bus
        port: Port for the message bus
    """
    logger.info("Starting registration server...")
    
    # Create message bus
    message_bus = MessageBus(host=host, port=port)
    message_bus.connect()
    
    # Create service registry
    service_registry = ServiceRegistry()
    service_registry.start()
    
    # Create registration manager
    registration_manager = RegistrationManager(
        service_registry=service_registry,
        message_bus=message_bus,
        secret_key=secret_key
    )
    
    logger.info(f"Registration server running at {host}:{port}")
    
    try:
        # Keep server running
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Shutting down registration server...")
        service_registry.stop()


async def run_client_example(component_type: str, host: str = "localhost", port: int = 5555) -> None:
    """
    Run a client example for demonstration purposes.
    
    This function demonstrates how to use the HermesClient class to
    register a component with the Tekton ecosystem.
    
    Args:
        component_type: Type of component to register
        host: Host for the Hermes server
        port: Port for the Hermes server
    """
    # Create a unique ID for this component
    component_id = f"{component_type}_{str(uuid.uuid4())[:8]}"
    component_name = f"Example {component_type.capitalize()} Component"
    
    logger.info(f"Starting client example for {component_name} ({component_id})...")
    
    # Create Hermes client
    client = HermesClient(
        component_id=component_id,
        component_name=component_name,
        component_type=component_type,
        component_version="1.0.0",
        hermes_endpoint=f"{host}:{port}",
        capabilities=[f"{component_type}.basic", f"{component_type}.advanced"]
    )
    
    # Register component
    logger.info(f"Registering component {component_id}...")
    registration_success = await client.register()
    
    if registration_success:
        logger.info(f"Component {component_id} registered successfully")
        
        # Publish some example messages
        for i in range(3):
            topic = f"example.{component_type}.event"
            message = {
                "event_id": i,
                "timestamp": time.time(),
                "data": f"Example data from {component_id}"
            }
            
            client.publish_message(
                topic=topic,
                message=message,
                headers={"event_type": "example_event"}
            )
            
            logger.info(f"Published message to topic {topic}")
            await asyncio.sleep(1)
        
        # Stay registered for a while
        await asyncio.sleep(5)
        
        # Unregister component
        logger.info(f"Unregistering component {component_id}...")
        unregistration_success = await client.unregister()
        
        if unregistration_success:
            logger.info(f"Component {component_id} unregistered successfully")
        else:
            logger.error(f"Failed to unregister component {component_id}")
            
    else:
        logger.error(f"Failed to register component {component_id}")
    
    # Close client
    await client.close()


async def main() -> None:
    """Main function to parse arguments and run examples."""
    parser = argparse.ArgumentParser(description="Unified Registration Protocol Example")
    
    parser.add_argument(
        "--mode",
        type=str,
        choices=["server", "client", "both"],
        default="both",
        help="Mode to run in (server, client, or both)"
    )
    
    parser.add_argument(
        "--host",
        type=str,
        default="localhost",
        help="Host for the Hermes server"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=5555,
        help="Port for the Hermes server"
    )
    
    parser.add_argument(
        "--component-type",
        type=str,
        default="example",
        help="Type of component to register (for client mode)"
    )
    
    parser.add_argument(
        "--secret-key",
        type=str,
        default="tekton_secret_key",
        help="Secret key for token generation/validation"
    )
    
    args = parser.parse_args()
    
    if args.mode == "server" or args.mode == "both":
        # Start server in a separate task
        server_task = asyncio.create_task(
            run_registration_server(
                secret_key=args.secret_key,
                host=args.host,
                port=args.port
            )
        )
        
        # Give server time to start
        if args.mode == "both":
            await asyncio.sleep(2)
    
    if args.mode == "client" or args.mode == "both":
        # Run client example
        await run_client_example(
            component_type=args.component_type,
            host=args.host,
            port=args.port
        )
    
    if args.mode == "server" or args.mode == "both":
        try:
            # Wait for server to complete (will run until interrupted)
            await server_task
        except asyncio.CancelledError:
            pass


if __name__ == "__main__":
    asyncio.run(main())
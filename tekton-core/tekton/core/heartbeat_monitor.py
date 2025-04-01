#!/usr/bin/env python3
"""
Heartbeat Monitor - Hermes connection monitoring and reconnection.

This module provides functionality to monitor the connection to Hermes
and automatically re-register components if Hermes restarts.
"""

import asyncio
import logging
import os
import signal
import sys
import time
from typing import Dict, List, Any, Optional, Callable, Set

from tekton.core.component_registration import ComponentRegistration

# Configure logging
logger = logging.getLogger(__name__)


class HeartbeatMonitor:
    """
    Monitors the connection to Hermes and handles reconnection.
    
    This class maintains heartbeats to Hermes and automatically
    re-registers components if Hermes restarts or becomes unavailable.
    """
    
    def __init__(self, 
                hermes_url: Optional[str] = None,
                retry_interval: int = 5,
                max_retries: int = -1):  # -1 means infinite retries
        """
        Initialize the heartbeat monitor.
        
        Args:
            hermes_url: URL of the Hermes API
            retry_interval: Interval between retries in seconds
            max_retries: Maximum number of retries (-1 for infinite)
        """
        self.hermes_url = hermes_url or os.environ.get("HERMES_URL", "http://localhost:5000/api")
        self.retry_interval = retry_interval
        self.max_retries = max_retries
        self.registrations: Dict[str, ComponentRegistration] = {}
        self.heartbeat_tasks: Dict[str, asyncio.Task] = {}
        self.running = False
        self.active_task = None
        
    def register_component(self, registration: ComponentRegistration) -> None:
        """
        Register a component with the monitor.
        
        Args:
            registration: ComponentRegistration instance
        """
        component_id = registration.component_id
        self.registrations[component_id] = registration
        logger.info(f"Added component {component_id} to heartbeat monitor")
        
        # Start heartbeat task if monitor is running
        if self.running and component_id not in self.heartbeat_tasks:
            self.heartbeat_tasks[component_id] = asyncio.create_task(
                self._component_heartbeat_loop(component_id)
            )
    
    def unregister_component(self, component_id: str) -> None:
        """
        Unregister a component from the monitor.
        
        Args:
            component_id: ID of the component to unregister
        """
        if component_id in self.registrations:
            del self.registrations[component_id]
            
            # Cancel heartbeat task if it exists
            if component_id in self.heartbeat_tasks:
                self.heartbeat_tasks[component_id].cancel()
                del self.heartbeat_tasks[component_id]
                
            logger.info(f"Removed component {component_id} from heartbeat monitor")
    
    async def start(self) -> None:
        """Start the heartbeat monitor."""
        if self.running:
            logger.warning("Heartbeat monitor already running")
            return
            
        self.running = True
        logger.info("Starting heartbeat monitor")
        
        # Start heartbeat tasks for registered components
        for component_id in self.registrations:
            if component_id not in self.heartbeat_tasks:
                self.heartbeat_tasks[component_id] = asyncio.create_task(
                    self._component_heartbeat_loop(component_id)
                )
        
        # Start the main monitoring task
        self.active_task = asyncio.create_task(self._monitor_loop())
        
    async def stop(self) -> None:
        """Stop the heartbeat monitor."""
        if not self.running:
            return
            
        self.running = False
        logger.info("Stopping heartbeat monitor")
        
        # Cancel all heartbeat tasks
        for component_id, task in self.heartbeat_tasks.items():
            task.cancel()
            
        self.heartbeat_tasks.clear()
        
        # Cancel the main monitoring task
        if self.active_task:
            self.active_task.cancel()
            self.active_task = None
    
    async def _monitor_loop(self) -> None:
        """Main monitoring loop."""
        try:
            while self.running:
                try:
                    # Check if Hermes is available
                    hermes_available = await self._check_hermes_availability()
                    
                    if not hermes_available:
                        logger.warning("Hermes appears to be unavailable, will attempt to reconnect components")
                        await self._reconnect_all_components()
                    
                    # Wait before next check
                    await asyncio.sleep(self.retry_interval * 2)
                    
                except asyncio.CancelledError:
                    raise
                except Exception as e:
                    logger.error(f"Error in monitor loop: {e}")
                    await asyncio.sleep(self.retry_interval)
                    
        except asyncio.CancelledError:
            logger.info("Monitor loop cancelled")
    
    async def _component_heartbeat_loop(self, component_id: str) -> None:
        """
        Heartbeat loop for a specific component.
        
        Args:
            component_id: ID of the component
        """
        retries = 0
        consecutive_failures = 0
        
        try:
            while self.running and (self.max_retries < 0 or retries < self.max_retries):
                if component_id not in self.registrations:
                    logger.warning(f"Component {component_id} no longer registered, stopping heartbeat")
                    return
                    
                registration = self.registrations[component_id]
                
                try:
                    # Send heartbeat
                    import aiohttp
                    
                    async with aiohttp.ClientSession() as session:
                        async with session.post(
                            f"{self.hermes_url}/registration/heartbeat",
                            json={
                                "component": component_id,
                                "status": "active",
                                "timestamp": time.time()
                            }
                        ) as response:
                            if response.status == 200:
                                logger.debug(f"Sent heartbeat for {component_id}")
                                consecutive_failures = 0
                            else:
                                error = await response.text()
                                logger.warning(f"Failed to send heartbeat for {component_id}: {error}")
                                consecutive_failures += 1
                                
                                # If multiple consecutive failures, try to re-register
                                if consecutive_failures >= 3:
                                    logger.warning(f"Multiple heartbeat failures for {component_id}, attempting to re-register")
                                    await self._reconnect_component(component_id)
                                    consecutive_failures = 0
                
                except asyncio.CancelledError:
                    raise
                except Exception as e:
                    logger.warning(f"Error sending heartbeat for {component_id}: {e}")
                    consecutive_failures += 1
                    
                    # If multiple consecutive failures, try to re-register
                    if consecutive_failures >= 3:
                        logger.warning(f"Multiple heartbeat failures for {component_id}, attempting to re-register")
                        await self._reconnect_component(component_id)
                        consecutive_failures = 0
                
                # Wait before next heartbeat
                await asyncio.sleep(self.retry_interval)
                
                retries += 1
        
        except asyncio.CancelledError:
            logger.info(f"Heartbeat loop for {component_id} cancelled")
    
    async def _check_hermes_availability(self) -> bool:
        """
        Check if Hermes is available.
        
        Returns:
            True if Hermes is available
        """
        try:
            import aiohttp
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.hermes_url}/health",
                    timeout=3
                ) as response:
                    return response.status == 200
        
        except Exception:
            return False
    
    async def _reconnect_component(self, component_id: str) -> bool:
        """
        Reconnect a specific component to Hermes.
        
        Args:
            component_id: ID of the component to reconnect
            
        Returns:
            True if reconnection was successful
        """
        if component_id not in self.registrations:
            logger.warning(f"Component {component_id} not registered, cannot reconnect")
            return False
            
        registration = self.registrations[component_id]
        
        try:
            # Re-register with Hermes
            result = await registration.register()
            
            if result:
                logger.info(f"Successfully reconnected {component_id} to Hermes")
                return True
            else:
                logger.error(f"Failed to reconnect {component_id} to Hermes")
                return False
                
        except Exception as e:
            logger.error(f"Error reconnecting {component_id} to Hermes: {e}")
            return False
    
    async def _reconnect_all_components(self) -> Dict[str, bool]:
        """
        Reconnect all registered components to Hermes.
        
        Returns:
            Dictionary mapping component IDs to reconnection status
        """
        results = {}
        
        for component_id in self.registrations:
            results[component_id] = await self._reconnect_component(component_id)
            
            # Wait briefly between reconnections to avoid overwhelming Hermes
            await asyncio.sleep(0.5)
        
        # Log summary
        success_count = sum(1 for status in results.values() if status)
        logger.info(f"Reconnected {success_count}/{len(results)} components to Hermes")
        
        return results


class ComponentHeartbeat:
    """
    Simplified interface for component heartbeat management.
    
    This class provides a simplified interface for components to manage
    their connection to Hermes, including automatic reconnection.
    """
    
    def __init__(self, 
                component_id: str,
                component_name: str,
                hermes_url: Optional[str] = None,
                capabilities: Optional[List[Dict[str, Any]]] = None,
                metadata: Optional[Dict[str, Any]] = None):
        """
        Initialize the component heartbeat.
        
        Args:
            component_id: ID of the component
            component_name: Name of the component
            hermes_url: URL of the Hermes API
            capabilities: Component capabilities
            metadata: Component metadata
        """
        self.component_id = component_id
        self.component_name = component_name
        self.hermes_url = hermes_url or os.environ.get("HERMES_URL", "http://localhost:5000/api")
        self.capabilities = capabilities or []
        self.metadata = metadata or {}
        self.monitor = None
        self.registration = None
        
    async def start(self) -> bool:
        """
        Start the heartbeat monitor.
        
        Returns:
            True if successful
        """
        try:
            # Create registration
            self.registration = ComponentRegistration(
                component_id=self.component_id,
                component_name=self.component_name,
                hermes_url=self.hermes_url,
                capabilities=self.capabilities,
                metadata=self.metadata
            )
            
            # Register with Hermes
            result = await self.registration.register()
            
            if not result:
                logger.error(f"Failed to register {self.component_id} with Hermes")
                return False
            
            # Create and start monitor
            self.monitor = HeartbeatMonitor(hermes_url=self.hermes_url)
            self.monitor.register_component(self.registration)
            await self.monitor.start()
            
            # Set up signal handlers for graceful shutdown
            self._setup_signal_handlers()
            
            logger.info(f"Started heartbeat monitoring for {self.component_id}")
            return True
            
        except Exception as e:
            logger.exception(f"Error starting heartbeat for {self.component_id}: {e}")
            return False
    
    async def stop(self) -> None:
        """Stop the heartbeat monitor."""
        if self.monitor:
            await self.monitor.stop()
            self.monitor = None
            
        if self.registration:
            await self.registration.unregister()
            self.registration = None
            
        logger.info(f"Stopped heartbeat monitoring for {self.component_id}")
    
    def _setup_signal_handlers(self) -> None:
        """Set up signal handlers for graceful shutdown."""
        loop = asyncio.get_event_loop()
        
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(
                sig,
                lambda s=sig: asyncio.create_task(self._shutdown(s))
            )
    
    async def _shutdown(self, sig: signal.Signals) -> None:
        """
        Handle shutdown signal.
        
        Args:
            sig: Signal that triggered shutdown
        """
        logger.info(f"Received signal {sig.name}, shutting down")
        await self.stop()
        
        # Exit after a short delay to allow clean shutdown
        loop = asyncio.get_event_loop()
        loop.stop()


# Example usage
async def example():
    """Example usage of heartbeat monitor."""
    # Create component heartbeat
    heartbeat = ComponentHeartbeat(
        component_id="example.component",
        component_name="Example Component",
        capabilities=[
            {
                "name": "example_capability",
                "description": "Example capability",
                "parameters": {
                    "param1": "string",
                    "param2": "number"
                }
            }
        ],
        metadata={
            "description": "Example component for testing",
            "version": "0.1.0"
        }
    )
    
    # Start heartbeat
    await heartbeat.start()
    
    try:
        # Run for a while
        logger.info("Running heartbeat monitor...")
        await asyncio.sleep(60)
    finally:
        # Stop heartbeat
        await heartbeat.stop()


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Run the example
    asyncio.run(example())
"""
Hermes Client Library - Simplified interface for Tekton components.

This module provides a simple client library that Tekton components can use to
interact with Hermes services, including registration, messaging, and database access.
"""

import os
import logging
import asyncio
import time
import uuid
from typing import Dict, List, Any, Optional, Union, Callable

# Configure logger
logger = logging.getLogger(__name__)


class HermesClient:
    """
    Client for interacting with Hermes services.
    
    This class provides a simplified interface for Tekton components to
    register with the Tekton ecosystem and access Hermes services.
    """
    
    def __init__(self,
                component_id: str = None,
                component_name: str = None,
                component_type: str = None,
                component_version: str = "1.0.0",
                hermes_endpoint: str = "localhost:5555",
                capabilities: List[str] = None):
        """
        Initialize the Hermes client.
        
        Args:
            component_id: Unique identifier for this component (auto-generated if None)
            component_name: Human-readable name for this component (defaults to component_id)
            component_type: Type of component (e.g., "engram", "ergon", "athena")
            component_version: Component version
            hermes_endpoint: Endpoint for Hermes services
            capabilities: List of component capabilities
        """
        # Generate component ID if not provided
        self.component_id = component_id or f"{component_type}_{str(uuid.uuid4())[:8]}"
        self.component_name = component_name or self.component_id
        self.component_type = component_type
        self.component_version = component_version
        self.hermes_endpoint = hermes_endpoint
        self.capabilities = capabilities or []
        
        # Internal state
        self._is_registered = False
        self._token = None
        self._message_bus = None
        self._registration_client = None
        
        # Initialize message bus connection
        self._initialize_connection()
        
        logger.info(f"Hermes client initialized for component {self.component_id}")
    
    def _initialize_connection(self) -> None:
        """Initialize connection to Hermes services."""
        # Import here to avoid circular imports
        from hermes.core.message_bus import MessageBus
        from hermes.core.registration import RegistrationClient
        
        # Extract host and port from endpoint
        if ":" in self.hermes_endpoint:
            host, port_str = self.hermes_endpoint.split(":")
            port = int(port_str)
        else:
            host = self.hermes_endpoint
            port = 5555
        
        # Create message bus instance
        self._message_bus = MessageBus(
            host=host,
            port=port
        )
        
        # Connect to message bus
        self._message_bus.connect()
        
        # Create registration client
        self._registration_client = RegistrationClient(
            component_id=self.component_id,
            name=self.component_name,
            version=self.component_version,
            component_type=self.component_type,
            endpoint=f"{host}:{port}/{self.component_id}",
            capabilities=self.capabilities,
            message_bus=self._message_bus
        )
    
    async def register(self) -> bool:
        """
        Register this component with the Tekton ecosystem.
        
        Returns:
            True if registration successful
        """
        if self._is_registered:
            logger.warning(f"Component {self.component_id} already registered")
            return True
        
        success = await self._registration_client.register()
        
        if success:
            self._is_registered = True
            logger.info(f"Component {self.component_id} registered successfully")
        else:
            logger.error(f"Failed to register component {self.component_id}")
        
        return success
    
    async def unregister(self) -> bool:
        """
        Unregister this component from the Tekton ecosystem.
        
        Returns:
            True if unregistration successful
        """
        if not self._is_registered:
            logger.warning(f"Component {self.component_id} not registered")
            return True
        
        success = await self._registration_client.unregister()
        
        if success:
            self._is_registered = False
            logger.info(f"Component {self.component_id} unregistered successfully")
        else:
            logger.error(f"Failed to unregister component {self.component_id}")
        
        return success
    
    def publish_message(self,
                      topic: str,
                      message: Any,
                      headers: Optional[Dict[str, Any]] = None) -> bool:
        """
        Publish a message to a topic.
        
        Args:
            topic: Topic to publish to
            message: Message to publish
            headers: Optional message headers
            
        Returns:
            True if publication successful
        """
        if not self._is_registered:
            logger.warning("Component not registered, cannot publish messages")
            return False
        
        # Add component information to headers
        headers = headers or {}
        headers["component_id"] = self.component_id
        headers["component_type"] = self.component_type
        
        return self._message_bus.publish(
            topic=topic,
            message=message,
            headers=headers
        )
    
    def subscribe_to_topic(self,
                        topic: str,
                        callback: Callable[[Dict[str, Any]], None]) -> bool:
        """
        Subscribe to a topic.
        
        Args:
            topic: Topic to subscribe to
            callback: Function to call when a message is received
            
        Returns:
            True if subscription successful
        """
        return self._message_bus.subscribe(
            topic=topic,
            callback=callback
        )
    
    def unsubscribe_from_topic(self,
                            topic: str,
                            callback: Callable[[Dict[str, Any]], None]) -> bool:
        """
        Unsubscribe from a topic.
        
        Args:
            topic: Topic to unsubscribe from
            callback: Callback function to remove
            
        Returns:
            True if unsubscription successful
        """
        return self._message_bus.unsubscribe(
            topic=topic,
            callback=callback
        )
    
    # This method will be expanded in the future to include database access
    def get_database_client(self, 
                          db_type: str,
                          namespace: str = None) -> Any:
        """
        Get a client for a specific database type.
        
        Args:
            db_type: Type of database (e.g., "vector", "graph", "key-value")
            namespace: Optional namespace for data isolation
            
        Returns:
            Database client (currently a placeholder)
        """
        if not self._is_registered:
            logger.warning("Component not registered, cannot access databases")
            return None
        
        # This is a placeholder for future implementation
        logger.info(f"Database client requested for {db_type} in namespace {namespace or 'default'}")
        return None
    
    async def close(self) -> None:
        """
        Close the connection to Hermes services.
        
        This method should be called when the component is shutting down
        to properly unregister and clean up resources.
        """
        if self._is_registered:
            await self.unregister()
        
        # Close message bus connection
        if self._message_bus:
            self._message_bus.close()
"""
Unified Registration Protocol - Central registration for all Tekton components.

This module implements the Unified Registration Protocol (URP) for Tekton components,
providing a single entry point for component registration, authentication, and
propagation of registration information to other Tekton systems.
"""

import logging
import time
import uuid
import hmac
import hashlib
import json
import threading
import asyncio
from typing import Dict, List, Any, Optional, Set, Callable, Tuple, Union

from hermes.core.service_discovery import ServiceRegistry
from hermes.core.message_bus import MessageBus

# Configure logger
logger = logging.getLogger(__name__)


class RegistrationToken:
    """
    Security token for authenticating components with the registration system.
    
    Tokens are used to validate component identity and authorize registration
    with the Tekton ecosystem.
    """
    
    def __init__(self, component_id: str, secret_key: str, expiration: int = 3600):
        """
        Initialize a registration token.
        
        Args:
            component_id: Unique identifier for the component
            secret_key: Secret key for signing the token
            expiration: Token validity period in seconds (default: 1 hour)
        """
        self.component_id = component_id
        self.secret_key = secret_key
        self.issued_at = int(time.time())
        self.expires_at = self.issued_at + expiration
        self.token_id = str(uuid.uuid4())
    
    def generate(self) -> str:
        """
        Generate a signed token string.
        
        Returns:
            Signed token as a string
        """
        payload = {
            "component_id": self.component_id,
            "token_id": self.token_id,
            "iat": self.issued_at,
            "exp": self.expires_at
        }
        
        # Create JSON string of payload
        payload_str = json.dumps(payload, sort_keys=True)
        
        # Create signature using HMAC-SHA256
        signature = hmac.new(
            self.secret_key.encode(),
            payload_str.encode(),
            hashlib.sha256
        ).hexdigest()
        
        # Combine payload and signature
        token = {
            "payload": payload,
            "signature": signature
        }
        
        return json.dumps(token)
    
    @staticmethod
    def validate(token_str: str, secret_key: str) -> Optional[Dict[str, Any]]:
        """
        Validate a token string.
        
        Args:
            token_str: Token string to validate
            secret_key: Secret key for verification
            
        Returns:
            Token payload if valid, None otherwise
        """
        try:
            # Parse token
            token = json.loads(token_str)
            payload = token["payload"]
            signature = token["signature"]
            
            # Check expiration
            current_time = int(time.time())
            if current_time > payload["exp"]:
                logger.warning("Token expired")
                return None
            
            # Verify signature
            payload_str = json.dumps(payload, sort_keys=True)
            expected_signature = hmac.new(
                secret_key.encode(),
                payload_str.encode(),
                hashlib.sha256
            ).hexdigest()
            
            if signature != expected_signature:
                logger.warning("Invalid token signature")
                return None
            
            return payload
            
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Error validating token: {e}")
            return None


class RegistrationManager:
    """
    Central manager for component registration across the Tekton ecosystem.
    
    This class manages component registration, authentication, and propagation
    of registration information between Tekton components.
    """
    
    def __init__(self, 
                service_registry: ServiceRegistry,
                message_bus: MessageBus,
                secret_key: str,
                token_expiration: int = 3600):
        """
        Initialize the registration manager.
        
        Args:
            service_registry: Service registry for component tracking
            message_bus: Message bus for event propagation
            secret_key: Secret key for token generation/validation
            token_expiration: Token validity period in seconds
        """
        self.service_registry = service_registry
        self.message_bus = message_bus
        self.secret_key = secret_key
        self.token_expiration = token_expiration
        
        # Dictionary to store active tokens
        self.active_tokens: Dict[str, Dict[str, Any]] = {}
        
        # Set up message bus subscriptions for registration events
        self._setup_subscriptions()
        
        logger.info("Registration manager initialized")
    
    def _setup_subscriptions(self) -> None:
        """Set up message bus subscriptions for registration events."""
        self.message_bus.subscribe("tekton.registration.request", self._handle_registration_request)
        self.message_bus.subscribe("tekton.registration.revoke", self._handle_revocation_request)
        self.message_bus.subscribe("tekton.registration.heartbeat", self._handle_heartbeat)
        logger.info("Registration event subscriptions established")
    
    def register_component(self, 
                         component_id: str,
                         name: str,
                         version: str,
                         component_type: str,
                         endpoint: str,
                         capabilities: List[str],
                         health_check: Optional[Callable[[], bool]] = None,
                         metadata: Optional[Dict[str, Any]] = None) -> Tuple[bool, Optional[str]]:
        """
        Register a component with the Tekton ecosystem.
        
        Args:
            component_id: Unique identifier for the component
            name: Human-readable name
            version: Component version
            component_type: Type of component (e.g., "engram", "ergon", "athena")
            endpoint: Component endpoint (URL or connection string)
            capabilities: List of component capabilities
            health_check: Optional function to check component health
            metadata: Additional component metadata
            
        Returns:
            Tuple of (success, token_string)
        """
        # Register with service registry
        registry_success = self.service_registry.register(
            service_id=component_id,
            name=name,
            version=version,
            endpoint=endpoint,
            capabilities=capabilities,
            health_check=health_check,
            metadata={
                "type": component_type,
                **(metadata or {})
            }
        )
        
        if not registry_success:
            logger.error(f"Failed to register component {component_id} with service registry")
            return False, None
        
        # Generate registration token
        token = RegistrationToken(
            component_id=component_id,
            secret_key=self.secret_key,
            expiration=self.token_expiration
        )
        token_str = token.generate()
        
        # Store token information
        self.active_tokens[token.token_id] = {
            "component_id": component_id,
            "issued_at": token.issued_at,
            "expires_at": token.expires_at
        }
        
        # Publish registration event
        self.message_bus.publish(
            topic="tekton.registration.completed",
            message={
                "component_id": component_id,
                "name": name,
                "type": component_type,
                "version": version,
                "capabilities": capabilities,
                "registered_at": time.time()
            },
            headers={
                "event_type": "component_registration",
                "component_id": component_id
            }
        )
        
        logger.info(f"Component {component_id} ({name}) registered successfully")
        return True, token_str
    
    def unregister_component(self, 
                           component_id: str,
                           token_str: str) -> bool:
        """
        Unregister a component from the Tekton ecosystem.
        
        Args:
            component_id: Component ID to unregister
            token_str: Registration token for authentication
            
        Returns:
            True if unregistration successful
        """
        # Validate token
        token_payload = RegistrationToken.validate(token_str, self.secret_key)
        if not token_payload or token_payload["component_id"] != component_id:
            logger.warning(f"Invalid token for component {component_id}")
            return False
        
        # Unregister from service registry
        registry_success = self.service_registry.unregister(component_id)
        
        if not registry_success:
            logger.error(f"Failed to unregister component {component_id} from service registry")
            return False
        
        # Remove token from active tokens
        token_id = token_payload["token_id"]
        if token_id in self.active_tokens:
            del self.active_tokens[token_id]
        
        # Publish unregistration event
        self.message_bus.publish(
            topic="tekton.registration.revoked",
            message={
                "component_id": component_id,
                "revoked_at": time.time()
            },
            headers={
                "event_type": "component_unregistration",
                "component_id": component_id
            }
        )
        
        logger.info(f"Component {component_id} unregistered successfully")
        return True
    
    def validate_component(self, 
                         component_id: str,
                         token_str: str) -> bool:
        """
        Validate a component's registration.
        
        Args:
            component_id: Component ID to validate
            token_str: Registration token for authentication
            
        Returns:
            True if component is validly registered
        """
        # Validate token
        token_payload = RegistrationToken.validate(token_str, self.secret_key)
        if not token_payload or token_payload["component_id"] != component_id:
            logger.warning(f"Invalid token for component {component_id}")
            return False
        
        # Check if component is registered
        service = self.service_registry.get_service(component_id)
        if not service:
            logger.warning(f"Component {component_id} not found in registry")
            return False
        
        logger.info(f"Component {component_id} validation successful")
        return True
    
    def send_heartbeat(self,
                     component_id: str,
                     token_str: str,
                     status: Dict[str, Any] = None) -> bool:
        """
        Send a heartbeat for a component to indicate it's still active.
        
        Args:
            component_id: Component ID
            token_str: Registration token for authentication
            status: Optional status information
            
        Returns:
            True if heartbeat was processed successfully
        """
        # Validate token
        token_payload = RegistrationToken.validate(token_str, self.secret_key)
        if not token_payload or token_payload["component_id"] != component_id:
            logger.warning(f"Invalid token for component {component_id} heartbeat")
            return False
        
        # Publish heartbeat event
        self.message_bus.publish(
            topic="tekton.registration.heartbeat",
            message={
                "component_id": component_id,
                "timestamp": time.time(),
                "status": status or {}
            },
            headers={
                "event_type": "component_heartbeat",
                "component_id": component_id
            }
        )
        
        logger.debug(f"Heartbeat received for component {component_id}")
        return True
    
    def _handle_registration_request(self, message: Dict[str, Any]) -> None:
        """
        Handle a registration request message.
        
        Args:
            message: Registration request message
        """
        try:
            payload = message["payload"]
            component_id = payload.get("component_id")
            name = payload.get("name")
            version = payload.get("version")
            component_type = payload.get("type")
            endpoint = payload.get("endpoint")
            capabilities = payload.get("capabilities", [])
            metadata = payload.get("metadata", {})
            
            if not all([component_id, name, version, component_type, endpoint]):
                logger.error("Missing required fields in registration request")
                return
            
            success, token_str = self.register_component(
                component_id=component_id,
                name=name,
                version=version,
                component_type=component_type,
                endpoint=endpoint,
                capabilities=capabilities,
                metadata=metadata
            )
            
            # Publish response
            if success and token_str:
                self.message_bus.publish(
                    topic=f"tekton.registration.response.{component_id}",
                    message={
                        "success": True,
                        "token": token_str
                    }
                )
            else:
                self.message_bus.publish(
                    topic=f"tekton.registration.response.{component_id}",
                    message={
                        "success": False,
                        "error": "Registration failed"
                    }
                )
                
        except Exception as e:
            logger.error(f"Error handling registration request: {e}")
    
    def _handle_revocation_request(self, message: Dict[str, Any]) -> None:
        """
        Handle a revocation request message.
        
        Args:
            message: Revocation request message
        """
        try:
            payload = message["payload"]
            component_id = payload.get("component_id")
            token_str = payload.get("token")
            
            if not all([component_id, token_str]):
                logger.error("Missing required fields in revocation request")
                return
            
            success = self.unregister_component(
                component_id=component_id,
                token_str=token_str
            )
            
            # Publish response
            self.message_bus.publish(
                topic=f"tekton.registration.response.{component_id}",
                message={
                    "success": success,
                    "operation": "revocation"
                }
            )
                
        except Exception as e:
            logger.error(f"Error handling revocation request: {e}")
    
    def _handle_heartbeat(self, message: Dict[str, Any]) -> None:
        """
        Handle a heartbeat message.
        
        Args:
            message: Heartbeat message
        """
        try:
            payload = message["payload"]
            component_id = payload.get("component_id")
            
            # Update last seen timestamp in service registry
            service = self.service_registry.get_service(component_id)
            if service:
                service["last_heartbeat"] = time.time()
                
        except Exception as e:
            logger.error(f"Error handling heartbeat: {e}")


class RegistrationClient:
    """
    Client for interacting with the Tekton registration system.
    
    This class provides methods for components to register, unregister,
    and maintain their presence in the Tekton ecosystem.
    """
    
    def __init__(self,
                component_id: str,
                name: str,
                version: str,
                component_type: str,
                endpoint: str,
                capabilities: List[str],
                message_bus: MessageBus,
                metadata: Optional[Dict[str, Any]] = None,
                heartbeat_interval: int = 60):
        """
        Initialize the registration client.
        
        Args:
            component_id: Unique identifier for this component
            name: Human-readable name
            version: Component version
            component_type: Type of component (e.g., "engram", "ergon", "athena")
            endpoint: Component endpoint (URL or connection string)
            capabilities: List of component capabilities
            message_bus: Message bus for communication
            metadata: Additional component metadata
            heartbeat_interval: Interval in seconds for sending heartbeats
        """
        self.component_id = component_id
        self.name = name
        self.version = version
        self.component_type = component_type
        self.endpoint = endpoint
        self.capabilities = capabilities
        self.message_bus = message_bus
        self.metadata = metadata or {}
        self.heartbeat_interval = heartbeat_interval
        
        # Registration token
        self.token = None
        
        # Heartbeat thread
        self.heartbeat_thread = None
        self.running = False
        
        # Set up message bus subscriptions
        self._setup_subscriptions()
        
        logger.info(f"Registration client initialized for component {component_id}")
    
    def _setup_subscriptions(self) -> None:
        """Set up message bus subscriptions for registration events."""
        self.message_bus.subscribe(
            f"tekton.registration.response.{self.component_id}",
            self._handle_registration_response
        )
    
    async def register(self) -> bool:
        """
        Register this component with the Tekton ecosystem.
        
        Returns:
            True if registration successful
        """
        # Create registration request
        request = {
            "component_id": self.component_id,
            "name": self.name,
            "version": self.version,
            "type": self.component_type,
            "endpoint": self.endpoint,
            "capabilities": self.capabilities,
            "metadata": self.metadata
        }
        
        # Publish registration request
        request_success = self.message_bus.publish(
            topic="tekton.registration.request",
            message=request,
            headers={
                "event_type": "registration_request",
                "component_id": self.component_id
            }
        )
        
        if not request_success:
            logger.error("Failed to send registration request")
            return False
        
        # Wait for response (in a real implementation, this would use async/await)
        # For now, we'll simulate with a simple loop
        max_wait = 10  # seconds
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            if self.token:
                self._start_heartbeat()
                return True
            time.sleep(0.1)
        
        logger.error("Timed out waiting for registration response")
        return False
    
    async def unregister(self) -> bool:
        """
        Unregister this component from the Tekton ecosystem.
        
        Returns:
            True if unregistration successful
        """
        if not self.token:
            logger.warning("Component not registered")
            return False
        
        # Stop heartbeat thread
        self._stop_heartbeat()
        
        # Create revocation request
        request = {
            "component_id": self.component_id,
            "token": self.token
        }
        
        # Publish revocation request
        request_success = self.message_bus.publish(
            topic="tekton.registration.revoke",
            message=request,
            headers={
                "event_type": "revocation_request",
                "component_id": self.component_id
            }
        )
        
        if not request_success:
            logger.error("Failed to send revocation request")
            return False
        
        # Clear token
        self.token = None
        
        logger.info(f"Component {self.component_id} unregistered")
        return True
    
    def _handle_registration_response(self, message: Dict[str, Any]) -> None:
        """
        Handle a registration response message.
        
        Args:
            message: Registration response message
        """
        try:
            payload = message["payload"]
            success = payload.get("success", False)
            
            if success:
                self.token = payload.get("token")
                logger.info(f"Component {self.component_id} registered successfully")
            else:
                error = payload.get("error", "Unknown error")
                logger.error(f"Registration failed: {error}")
                
        except Exception as e:
            logger.error(f"Error handling registration response: {e}")
    
    def _start_heartbeat(self) -> None:
        """Start the heartbeat thread."""
        if self.running:
            return
            
        self.running = True
        self.heartbeat_thread = threading.Thread(target=self._heartbeat_loop)
        self.heartbeat_thread.daemon = True
        self.heartbeat_thread.start()
        logger.info("Heartbeat thread started")
    
    def _stop_heartbeat(self) -> None:
        """Stop the heartbeat thread."""
        self.running = False
        if self.heartbeat_thread and self.heartbeat_thread.is_alive():
            self.heartbeat_thread.join(timeout=5)
        logger.info("Heartbeat thread stopped")
    
    def _heartbeat_loop(self) -> None:
        """
        Main loop for sending heartbeats.
        
        This runs in a separate thread and periodically sends heartbeats
        to indicate the component is still active.
        """
        while self.running and self.token:
            try:
                # Create heartbeat message
                heartbeat = {
                    "component_id": self.component_id,
                    "token": self.token,
                    "timestamp": time.time(),
                    "status": {
                        "healthy": True  # Can be extended with more status info
                    }
                }
                
                # Publish heartbeat
                self.message_bus.publish(
                    topic="tekton.registration.heartbeat",
                    message=heartbeat,
                    headers={
                        "event_type": "component_heartbeat",
                        "component_id": self.component_id
                    }
                )
                
            except Exception as e:
                logger.error(f"Error sending heartbeat: {e}")
                
            # Sleep until next heartbeat
            time.sleep(self.heartbeat_interval)
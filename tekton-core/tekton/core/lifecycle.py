#!/usr/bin/env python3
"""
Component Lifecycle Definitions Module

This module provides core component lifecycle class definitions for the Tekton
component lifecycle management system.
"""

import uuid
import time
import asyncio
import logging
from enum import Enum
from typing import Dict, List, Any, Optional, Set, Callable, Awaitable

logger = logging.getLogger("tekton.lifecycle")

class ComponentState(Enum):
    """
    Enhanced component state enum with fine-grained lifecycle states.
    
    Provides clear distinction between different operational states to avoid deadlocks
    and enable better dependency management.
    """
    UNKNOWN = "unknown"            # State not known or not tracked
    INITIALIZING = "initializing"  # Starting up but not ready for operations
    READY = "ready"                # Fully operational and accepting requests
    DEGRADED = "degraded"          # Running with limited functionality
    FAILED = "failed"              # Failed to start or crashed
    STOPPING = "stopping"          # Graceful shutdown in progress
    RESTARTING = "restarting"      # Temporary unavailable during restart
    
    @classmethod
    def is_active(cls, state):
        """Check if the state is considered active (can serve requests)."""
        return state in [cls.READY.value, cls.DEGRADED.value]
    
    @classmethod
    def is_terminal(cls, state):
        """Check if the state is a terminal state."""
        return state in [cls.FAILED.value]
    
    @classmethod
    def is_transitioning(cls, state):
        """Check if the state is a transitional state."""
        return state in [cls.INITIALIZING.value, cls.STOPPING.value, cls.RESTARTING.value]
    
    @classmethod
    def validate_transition(cls, from_state, to_state):
        """
        Validate if a state transition is allowed.
        
        Args:
            from_state: Current state
            to_state: Target state
            
        Returns:
            True if transition is valid, False otherwise
        """
        # Define valid transitions
        valid_transitions = {
            cls.UNKNOWN.value: [
                cls.INITIALIZING.value, cls.READY.value, cls.DEGRADED.value, 
                cls.FAILED.value, cls.STOPPING.value
            ],
            cls.INITIALIZING.value: [
                cls.READY.value, cls.DEGRADED.value, cls.FAILED.value, 
                cls.STOPPING.value, cls.RESTARTING.value
            ],
            cls.READY.value: [
                cls.DEGRADED.value, cls.FAILED.value, cls.STOPPING.value, 
                cls.RESTARTING.value
            ],
            cls.DEGRADED.value: [
                cls.READY.value, cls.FAILED.value, cls.STOPPING.value, 
                cls.RESTARTING.value
            ],
            cls.FAILED.value: [
                cls.INITIALIZING.value, cls.RESTARTING.value
            ],
            cls.STOPPING.value: [
                cls.UNKNOWN.value, cls.FAILED.value
            ],
            cls.RESTARTING.value: [
                cls.INITIALIZING.value, cls.READY.value, cls.DEGRADED.value, 
                cls.FAILED.value
            ]
        }
        
        return to_state in valid_transitions.get(from_state, [])


class ReadinessCondition:
    """
    A condition that must be satisfied for a component to be considered ready.
    
    Enables fine-grained tracking of component startup progress and dependency
    satisfaction.
    """
    
    def __init__(self, 
                name: str, 
                check_func: Callable[[], Awaitable[bool]], 
                description: Optional[str] = None,
                timeout: Optional[float] = 60.0):
        """
        Initialize a readiness condition.
        
        Args:
            name: Condition name
            check_func: Async function that returns True if condition is satisfied
            description: Optional description
            timeout: Optional timeout in seconds
        """
        self.name = name
        self.check_func = check_func
        self.description = description or f"Condition: {name}"
        self.timeout = timeout
        self.satisfied = False
        self.last_check_time = 0
        self.last_error = None
    
    async def check(self) -> bool:
        """
        Check if the condition is satisfied.
        
        Returns:
            True if satisfied
        """
        try:
            self.last_check_time = time.time()
            self.satisfied = await self.check_func()
            self.last_error = None
            return self.satisfied
        except Exception as e:
            self.satisfied = False
            self.last_error = str(e)
            logger.error(f"Error checking readiness condition {self.name}: {e}")
            return False


class ComponentRegistration:
    """
    Enhanced component registration with unique instance tracking.
    
    Provides unique identity for component instances across restarts to prevent
    duplicate instances and track component lifecycle.
    """
    
    def __init__(self, 
                component_id: str,
                component_name: str,
                component_type: str,
                instance_uuid: Optional[str] = None,
                version: str = "0.1.0",
                capabilities: Optional[List[Dict[str, Any]]] = None,
                metadata: Optional[Dict[str, Any]] = None):
        """
        Initialize component registration.
        
        Args:
            component_id: Unique component identifier
            component_name: Human-readable name
            component_type: Type of component
            instance_uuid: Optional instance UUID (generated if None)
            version: Component version
            capabilities: Optional component capabilities
            metadata: Optional metadata
        """
        self.component_id = component_id
        self.component_name = component_name
        self.component_type = component_type
        self.instance_uuid = instance_uuid or str(uuid.uuid4())
        self.version = version
        self.capabilities = capabilities or []
        self.metadata = metadata or {}
        self.start_time = time.time()
        self.state = ComponentState.INITIALIZING.value
        self.readiness_conditions = {}
        self.heartbeat_sequence = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "component_id": self.component_id,
            "component_name": self.component_name,
            "component_type": self.component_type,
            "instance_uuid": self.instance_uuid,
            "version": self.version,
            "capabilities": self.capabilities,
            "metadata": self.metadata,
            "start_time": self.start_time,
            "state": self.state
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ComponentRegistration':
        """Create from dictionary."""
        instance = cls(
            component_id=data.get("component_id"),
            component_name=data.get("component_name"),
            component_type=data.get("component_type"),
            instance_uuid=data.get("instance_uuid"),
            version=data.get("version", "0.1.0"),
            capabilities=data.get("capabilities", []),
            metadata=data.get("metadata", {})
        )
        instance.start_time = data.get("start_time", time.time())
        instance.state = data.get("state", ComponentState.INITIALIZING.value)
        return instance


class PersistentMessageQueue:
    """
    Message queue with history for reliable message delivery.
    
    Ensures components don't miss messages during startup or restart by
    maintaining message history and tracking delivered messages.
    """
    
    def __init__(self, topic: str = "default", max_history: int = 100):
        """
        Initialize a persistent message queue.
        
        Args:
            topic: Topic name
            max_history: Maximum number of messages to keep
        """
        self.topic = topic
        self.messages = []
        self.max_history = max_history
        self.subscribers = {}  # Map of subscriber_id to last_msg_id processed
        self.lock = asyncio.Lock()
    
    async def add_message(self, message: Any, sender_id: Optional[str] = None) -> str:
        """
        Add a message to the queue.
        
        Args:
            message: Message content
            sender_id: Optional sender ID
            
        Returns:
            Message ID
        """
        async with self.lock:
            msg_id = str(uuid.uuid4())
            self.messages.append({
                "id": msg_id,
                "sender_id": sender_id,
                "timestamp": time.time(),
                "content": message
            })
            
            # Trim history if needed
            if len(self.messages) > self.max_history:
                self.messages = self.messages[-self.max_history:]
                
            return msg_id
    
    async def get_messages_since(self, subscriber_id: str, last_msg_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get messages since the last processed message for a subscriber.
        
        Args:
            subscriber_id: Subscriber ID
            last_msg_id: Optional last message ID processed
            
        Returns:
            List of messages
        """
        async with self.lock:
            # If no last message ID, use the one stored for the subscriber
            if not last_msg_id and subscriber_id in self.subscribers:
                last_msg_id = self.subscribers.get(subscriber_id)
                
            # If still no last message ID, return all messages
            if not last_msg_id:
                return self.messages
                
            # Find index of last received message
            for i, msg in enumerate(self.messages):
                if msg["id"] == last_msg_id:
                    # Update subscriber's last message ID
                    if self.messages:
                        self.subscribers[subscriber_id] = self.messages[-1]["id"]
                    return self.messages[i+1:]
                    
            # If message not found, return all (may have been pruned)
            # Update subscriber's last message ID
            if self.messages:
                self.subscribers[subscriber_id] = self.messages[-1]["id"]
            return self.messages
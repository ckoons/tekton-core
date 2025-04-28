"""
A2A Message - Core message format for agent-to-agent communication.

This module defines the standardized message format and validation for
agent-to-agent communication in the Tekton ecosystem.
"""

import json
import uuid
import time
import logging
from enum import Enum
from typing import Dict, List, Any, Optional, Union, Type, cast

logger = logging.getLogger(__name__)

class A2AMessageType(str, Enum):
    """Types of A2A messages."""
    REQUEST = "request"          # Request from agent to another agent
    RESPONSE = "response"        # Response to a request
    COMMAND = "command"          # Command to an agent
    EVENT = "event"              # Event notification
    TASK = "task"                # Task assignment
    TASK_STATUS = "task_status"  # Task status update
    HEARTBEAT = "heartbeat"      # Agent heartbeat
    BROADCAST = "broadcast"      # Broadcast message


class A2AMessageStatus(str, Enum):
    """Status codes for A2A messages."""
    SUCCESS = "success"
    ERROR = "error"
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REJECTED = "rejected"
    TIMEOUT = "timeout"


class A2AMessage:
    """
    Standard message format for agent-to-agent communication.
    
    This class represents a message in the A2A protocol, providing
    methods for construction, serialization, and validation.
    """
    
    def __init__(
        self,
        sender: Dict[str, Any],
        recipients: List[Dict[str, Any]],
        message_type: Union[A2AMessageType, str],
        content: Dict[str, Any],
        message_id: Optional[str] = None,
        conversation_id: Optional[str] = None,
        reply_to: Optional[str] = None,
        intent: Optional[str] = None,
        priority: str = "normal",
        metadata: Optional[Dict[str, Any]] = None,
        security: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize an A2A message.
        
        Args:
            sender: Information about the message sender
            recipients: List of message recipients
            message_type: Type of message
            content: Message content
            message_id: Unique message identifier (generated if not provided)
            conversation_id: Conversation this message belongs to
            reply_to: ID of message this is a reply to
            intent: Purpose or intent of the message
            priority: Message priority (low, normal, high, urgent)
            metadata: Additional message metadata
            security: Security information (encryption, signature, etc.)
        """
        self.id = message_id or f"msg-{uuid.uuid4()}"
        self.timestamp = time.time()
        self.sender = sender
        self.recipients = recipients
        self.type = message_type if isinstance(message_type, str) else message_type.value
        self.content = content
        self.conversation_id = conversation_id
        self.reply_to = reply_to
        self.intent = intent
        self.priority = priority
        self.metadata = metadata or {}
        self.security = security or {"encryption": "none"}
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the message to a dictionary.
        
        Returns:
            Dictionary representation of the message
        """
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "sender": self.sender,
            "recipients": self.recipients,
            "type": self.type,
            "content": self.content,
            "conversation_id": self.conversation_id,
            "reply_to": self.reply_to,
            "intent": self.intent,
            "priority": self.priority,
            "metadata": self.metadata,
            "security": self.security
        }
    
    def to_json(self) -> str:
        """
        Convert the message to a JSON string.
        
        Returns:
            JSON representation of the message
        """
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "A2AMessage":
        """
        Create a message from a dictionary.
        
        Args:
            data: Dictionary representation of a message
            
        Returns:
            A2AMessage instance
        """
        return cls(
            message_id=data.get("id"),
            sender=data.get("sender", {}),
            recipients=data.get("recipients", []),
            message_type=data.get("type", "request"),
            content=data.get("content", {}),
            conversation_id=data.get("conversation_id"),
            reply_to=data.get("reply_to"),
            intent=data.get("intent"),
            priority=data.get("priority", "normal"),
            metadata=data.get("metadata"),
            security=data.get("security")
        )
    
    @classmethod
    def from_json(cls, json_str: str) -> "A2AMessage":
        """
        Create a message from a JSON string.
        
        Args:
            json_str: JSON representation of a message
            
        Returns:
            A2AMessage instance
        """
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def create_response(
        self,
        content: Dict[str, Any],
        status: Union[A2AMessageStatus, str] = A2AMessageStatus.SUCCESS,
        metadata: Optional[Dict[str, Any]] = None
    ) -> "A2AMessage":
        """
        Create a response to this message.
        
        Args:
            content: Response content
            status: Response status
            metadata: Additional metadata
            
        Returns:
            Response message
        """
        status_str = status if isinstance(status, str) else status.value
        
        # Set status in content
        response_content = content.copy()
        response_content["status"] = status_str
        
        # Create recipient from original sender
        recipient = {
            "id": self.sender.get("id"),
            "type": "direct"
        }
        
        # Combine metadata
        combined_metadata = self.metadata.copy()
        if metadata:
            combined_metadata.update(metadata)
        
        return A2AMessage(
            sender={
                "id": self.recipients[0].get("id") if self.recipients else "unknown",
                "name": "Responding Agent",
                "version": "1.0.0"
            },
            recipients=[recipient],
            message_type=A2AMessageType.RESPONSE,
            content=response_content,
            conversation_id=self.conversation_id,
            reply_to=self.id,
            intent=self.intent,
            priority=self.priority,
            metadata=combined_metadata,
            security=self.security
        )


def validate_message(message: Dict[str, Any]) -> bool:
    """
    Validate an A2A message against the protocol schema.
    
    Args:
        message: Message dictionary to validate
        
    Returns:
        True if valid, False otherwise
    """
    # Check required fields
    required_fields = ["id", "sender", "recipients", "type", "content"]
    for field in required_fields:
        if field not in message:
            logger.error(f"Missing required field in A2A message: {field}")
            return False
            
    # Check sender format
    sender = message.get("sender", {})
    if not isinstance(sender, dict) or "id" not in sender:
        logger.error("Invalid sender format in A2A message")
        return False
        
    # Check recipients format
    recipients = message.get("recipients", [])
    if not isinstance(recipients, list) or not recipients:
        logger.error("Invalid recipients format in A2A message")
        return False
        
    for recipient in recipients:
        if not isinstance(recipient, dict) or "id" not in recipient:
            logger.error("Invalid recipient entry in A2A message")
            return False
            
    # Check message type
    message_type = message.get("type", "")
    valid_types = [t.value for t in A2AMessageType]
    if message_type not in valid_types:
        logger.error(f"Invalid message type in A2A message: {message_type}")
        return False
        
    # Check content format
    content = message.get("content", {})
    if not isinstance(content, dict):
        logger.error("Invalid content format in A2A message")
        return False
        
    return True
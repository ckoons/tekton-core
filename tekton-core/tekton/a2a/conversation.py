"""
Conversation Manager - System for managing multi-message conversations.

This module provides a conversation management system for A2A agents,
allowing them to track messages within ongoing conversations.
"""

import time
import uuid
import logging
from typing import Dict, List, Any, Optional, Callable, Union

from tekton.a2a.message import A2AMessage

logger = logging.getLogger(__name__)

class ConversationMetadata:
    """
    Metadata for A2A conversations.
    
    This class represents metadata about a conversation between agents,
    including participants, topic, and context.
    """
    
    def __init__(
        self,
        conversation_id: Optional[str] = None,
        participants: Optional[List[str]] = None,
        topic: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize conversation metadata.
        
        Args:
            conversation_id: Unique identifier for the conversation
            participants: List of participant agent IDs
            topic: Conversation topic or purpose
            context: Shared conversation context
            metadata: Additional metadata
        """
        self.conversation_id = conversation_id or f"conv-{uuid.uuid4()}"
        self.participants = participants or []
        self.topic = topic or "General conversation"
        self.context = context or {}
        self.metadata = metadata or {}
        self.created_at = time.time()
        self.last_message_at = time.time()
        self.message_count = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the metadata to a dictionary.
        
        Returns:
            Dictionary representation of the metadata
        """
        return {
            "conversation_id": self.conversation_id,
            "participants": self.participants,
            "topic": self.topic,
            "context": self.context,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "last_message_at": self.last_message_at,
            "message_count": self.message_count
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ConversationMetadata":
        """
        Create metadata from a dictionary.
        
        Args:
            data: Dictionary representation of metadata
            
        Returns:
            ConversationMetadata instance
        """
        metadata = cls(
            conversation_id=data.get("conversation_id"),
            participants=data.get("participants"),
            topic=data.get("topic"),
            context=data.get("context"),
            metadata=data.get("metadata")
        )
        
        # Set timestamps if provided
        if "created_at" in data:
            metadata.created_at = data["created_at"]
        if "last_message_at" in data:
            metadata.last_message_at = data["last_message_at"]
        if "message_count" in data:
            metadata.message_count = data["message_count"]
            
        return metadata
    
    def update_last_message(self):
        """Update last message timestamp and count."""
        self.last_message_at = time.time()
        self.message_count += 1


class ConversationManager:
    """
    Manager for A2A conversations.
    
    This class provides methods for starting and managing conversations
    between A2A agents.
    """
    
    def __init__(self):
        """Initialize the conversation manager."""
        self.conversations: Dict[str, ConversationMetadata] = {}
        self.messages: Dict[str, List[Dict[str, Any]]] = {}
        self._callbacks: Dict[str, List[Callable[[str, Dict[str, Any]], None]]] = {
            "conversation_started": [],
            "message_added": []
        }
        
        logger.info("Conversation manager initialized")
    
    async def start_conversation(
        self,
        participants: List[str],
        topic: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        conversation_id: Optional[str] = None
    ) -> str:
        """
        Start a new conversation.
        
        Args:
            participants: List of participant agent IDs
            topic: Conversation topic or purpose
            context: Shared conversation context
            metadata: Additional metadata
            conversation_id: Optional ID for the conversation
            
        Returns:
            Conversation ID
        """
        # Create conversation metadata
        conv_metadata = ConversationMetadata(
            conversation_id=conversation_id,
            participants=participants,
            topic=topic,
            context=context,
            metadata=metadata
        )
        
        # Store conversation
        self.conversations[conv_metadata.conversation_id] = conv_metadata
        self.messages[conv_metadata.conversation_id] = []
        
        logger.info(f"Started conversation: {conv_metadata.topic} ({conv_metadata.conversation_id})")
        
        # Trigger conversation started callbacks
        for callback in self._callbacks["conversation_started"]:
            try:
                callback(conv_metadata.conversation_id, conv_metadata.to_dict())
            except Exception as e:
                logger.error(f"Error in conversation started callback: {e}")
        
        return conv_metadata.conversation_id
    
    async def add_message(
        self,
        conversation_id: str,
        message: Union[A2AMessage, Dict[str, Any]]
    ) -> bool:
        """
        Add a message to a conversation.
        
        Args:
            conversation_id: ID of the conversation
            message: Message to add
            
        Returns:
            True if message added successfully
        """
        if conversation_id not in self.conversations:
            logger.warning(f"Conversation not found: {conversation_id}")
            return False
            
        # Convert message to dictionary if needed
        if isinstance(message, A2AMessage):
            message_dict = message.to_dict()
        else:
            message_dict = message
            
        # Add message
        self.messages[conversation_id].append(message_dict)
        
        # Update conversation metadata
        self.conversations[conversation_id].update_last_message()
        
        logger.debug(f"Added message to conversation {conversation_id}")
        
        # Trigger message added callbacks
        for callback in self._callbacks["message_added"]:
            try:
                callback(conversation_id, message_dict)
            except Exception as e:
                logger.error(f"Error in message added callback: {e}")
                
        return True
    
    async def get_conversation(self, conversation_id: str) -> Optional[ConversationMetadata]:
        """
        Get conversation metadata.
        
        Args:
            conversation_id: ID of the conversation
            
        Returns:
            ConversationMetadata or None if not found
        """
        return self.conversations.get(conversation_id)
    
    async def get_messages(
        self,
        conversation_id: str,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get messages from a conversation.
        
        Args:
            conversation_id: ID of the conversation
            limit: Maximum number of messages to return
            offset: Number of messages to skip
            
        Returns:
            List of messages
        """
        if conversation_id not in self.messages:
            logger.warning(f"Conversation not found: {conversation_id}")
            return []
            
        messages = self.messages[conversation_id]
        
        # Apply offset and limit
        if offset:
            messages = messages[offset:]
        if limit:
            messages = messages[:limit]
            
        return messages
    
    async def get_agent_conversations(
        self,
        agent_id: str
    ) -> List[ConversationMetadata]:
        """
        Get all conversations an agent is participating in.
        
        Args:
            agent_id: Agent ID to get conversations for
            
        Returns:
            List of conversations the agent is participating in
        """
        return [
            conv for conv in self.conversations.values()
            if agent_id in conv.participants
        ]
    
    async def update_context(
        self,
        conversation_id: str,
        context: Dict[str, Any]
    ) -> bool:
        """
        Update a conversation's context.
        
        Args:
            conversation_id: ID of the conversation
            context: New or updated context information
            
        Returns:
            True if update successful
        """
        if conversation_id not in self.conversations:
            logger.warning(f"Conversation not found: {conversation_id}")
            return False
            
        # Update context
        self.conversations[conversation_id].context.update(context)
        
        return True
    
    def on_conversation_started(self, callback: Callable[[str, Dict[str, Any]], None]):
        """
        Register a callback for conversation started events.
        
        Args:
            callback: Function to call when a conversation is started
        """
        self._callbacks["conversation_started"].append(callback)
    
    def on_message_added(self, callback: Callable[[str, Dict[str, Any]], None]):
        """
        Register a callback for message added events.
        
        Args:
            callback: Function to call when a message is added
        """
        self._callbacks["message_added"].append(callback)


# Global conversation manager instance for convenience functions
_global_conversation_manager: Optional[ConversationManager] = None

def get_conversation_manager() -> ConversationManager:
    """
    Get the global conversation manager, creating it if needed.
    
    Returns:
        Global ConversationManager instance
    """
    global _global_conversation_manager
    if _global_conversation_manager is None:
        _global_conversation_manager = ConversationManager()
    return _global_conversation_manager

async def start_conversation(
    participants: List[str],
    topic: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> str:
    """
    Start a new conversation using the global conversation manager.
    
    Args:
        participants: List of participant agent IDs
        topic: Conversation topic or purpose
        context: Shared conversation context
        metadata: Additional metadata
        
    Returns:
        Conversation ID
    """
    manager = get_conversation_manager()
    return await manager.start_conversation(
        participants=participants,
        topic=topic,
        context=context,
        metadata=metadata
    )

async def add_to_conversation(
    conversation_id: str,
    message: Union[A2AMessage, Dict[str, Any]]
) -> bool:
    """
    Add a message to a conversation using the global conversation manager.
    
    Args:
        conversation_id: ID of the conversation
        message: Message to add
        
    Returns:
        True if message added successfully
    """
    manager = get_conversation_manager()
    return await manager.add_message(conversation_id, message)

async def get_conversation_history(
    conversation_id: str,
    limit: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Get conversation history using the global conversation manager.
    
    Args:
        conversation_id: ID of the conversation
        limit: Maximum number of messages to return
        
    Returns:
        List of messages
    """
    manager = get_conversation_manager()
    return await manager.get_messages(conversation_id, limit)
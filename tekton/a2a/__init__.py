"""
Agent-to-Agent (A2A) Communication Framework

This package provides the core components for agent-to-agent communication,
enabling autonomous agent collaboration within the Tekton ecosystem.
"""

from tekton.a2a.message import (
    A2AMessage, 
    A2AMessageType, 
    A2AMessageStatus,
    validate_message
)
from tekton.a2a.agent_registry import (
    AgentRegistry,
    AgentCard,
    register_agent,
    unregister_agent,
    find_agents_by_capability
)
from tekton.a2a.task_manager import (
    TaskManager,
    TaskSpec,
    TaskStatus,
    create_task,
    assign_task,
    complete_task,
    get_task_status
)
from tekton.a2a.conversation import (
    ConversationManager,
    ConversationMetadata,
    start_conversation,
    add_to_conversation,
    get_conversation_history
)
from tekton.a2a.discovery import (
    DiscoveryService,
    find_agent_by_id,
    find_agents_by_type,
    discover_agents
)

__all__ = [
    # Message module
    "A2AMessage", "A2AMessageType", "A2AMessageStatus", "validate_message",
    
    # Agent registry module
    "AgentRegistry", "AgentCard", "register_agent", "unregister_agent", 
    "find_agents_by_capability",
    
    # Task manager module
    "TaskManager", "TaskSpec", "TaskStatus", "create_task", "assign_task",
    "complete_task", "get_task_status",
    
    # Conversation manager module
    "ConversationManager", "ConversationMetadata", "start_conversation",
    "add_to_conversation", "get_conversation_history",
    
    # Discovery service module
    "DiscoveryService", "find_agent_by_id", "find_agents_by_type", "discover_agents"
]
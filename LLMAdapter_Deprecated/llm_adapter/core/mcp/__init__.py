"""
MCP Module for LLM Adapter

This module provides Model Context Protocol (MCP) support 
for the LLM Adapter service using FastMCP.
"""

# Import capabilities
from .capabilities import (
    ModelManagementCapability,
    ConversationCapability,
    StreamingCapability,
    IntegrationCapability
)

# Import tools
from .tools import (
    # Model management
    list_available_models,
    get_model_info,
    set_default_model,
    validate_model_config,
    
    # Conversation tools
    send_message,
    create_conversation,
    get_conversation_history,
    clear_conversation,
    
    # Streaming tools
    start_streaming_conversation,
    send_streaming_message,
    
    # Integration tools
    register_with_hermes,
    health_check,
    get_adapter_status,
    
    # Registration functions
    get_all_tools,
    get_all_capabilities
)

__all__ = [
    # Capabilities
    "ModelManagementCapability",
    "ConversationCapability",
    "StreamingCapability", 
    "IntegrationCapability",
    
    # Tools
    "list_available_models",
    "get_model_info",
    "set_default_model",
    "validate_model_config",
    "send_message",
    "create_conversation",
    "get_conversation_history",
    "clear_conversation",
    "start_streaming_conversation",
    "send_streaming_message",
    "register_with_hermes",
    "health_check",
    "get_adapter_status",
    
    # Registration functions
    "get_all_tools",
    "get_all_capabilities"
]
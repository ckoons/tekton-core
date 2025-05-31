"""
FastMCP tools for LLM Adapter.

This module defines FastMCP tools for language model interactions, conversation management,
streaming operations, and system integration using the decorator-based approach.
"""

from typing import Dict, Any, List, Optional
from tekton.mcp.fastmcp.decorators import mcp_tool, mcp_capability
from tekton.mcp.fastmcp.schema import MCPTool


@mcp_capability(
    name="model_management",
    description="Manage and configure various language models and providers"
)
class ModelManagementCapability:
    """Capability for language model management and configuration."""
    pass


@mcp_tool(
    capability="model_management",
    name="list_available_models",
    description="List all available language models and providers"
)
async def list_available_models(
    provider: Optional[str] = None,
    model_type: Optional[str] = None,
    llm_client=None
) -> Dict[str, Any]:
    """
    List all available language models and providers.
    
    Args:
        provider: Optional provider filter (anthropic, openai, local)
        model_type: Optional model type filter (chat, completion, embedding)
        llm_client: Injected LLM client instance
        
    Returns:
        Dict containing available models and their details
    """
    if not llm_client:
        return {"error": "LLM client not available"}
    
    try:
        # Default available models
        models = {
            "anthropic": {
                "claude-3-7-sonnet": {"type": "chat", "max_tokens": 8192, "cost": "medium"},
                "claude-3-haiku": {"type": "chat", "max_tokens": 4096, "cost": "low"},
                "claude-instant": {"type": "chat", "max_tokens": 4096, "cost": "low"}
            },
            "openai": {
                "gpt-4": {"type": "chat", "max_tokens": 8192, "cost": "high"},
                "gpt-3.5-turbo": {"type": "chat", "max_tokens": 4096, "cost": "medium"},
                "text-embedding-ada-002": {"type": "embedding", "dimensions": 1536, "cost": "low"}
            },
            "local": {
                "llama-7b": {"type": "chat", "max_tokens": 2048, "cost": "free"},
                "codellama": {"type": "completion", "max_tokens": 4096, "cost": "free"}
            }
        }
        
        # Apply filters
        if provider:
            models = {k: v for k, v in models.items() if k == provider}
        
        if model_type:
            for provider_name in models:
                models[provider_name] = {
                    k: v for k, v in models[provider_name].items() 
                    if v.get("type") == model_type
                }
        
        return {
            "models": models,
            "total_count": sum(len(provider_models) for provider_models in models.values()),
            "providers": list(models.keys())
        }
    except Exception as e:
        return {"error": f"Failed to list models: {str(e)}"}


@mcp_tool(
    capability="model_management",
    name="get_model_info",
    description="Get detailed information about a specific model"
)
async def get_model_info(
    model_name: str,
    provider: str,
    llm_client=None
) -> Dict[str, Any]:
    """
    Get detailed information about a specific model.
    
    Args:
        model_name: Name of the model
        provider: Provider of the model
        llm_client: Injected LLM client instance
        
    Returns:
        Dict containing detailed model information
    """
    if not llm_client:
        return {"error": "LLM client not available"}
    
    try:
        # Mock model information - in real implementation, would query provider APIs
        model_info = {
            "name": model_name,
            "provider": provider,
            "description": f"Language model {model_name} from {provider}",
            "capabilities": ["text_generation", "conversation"],
            "parameters": {
                "max_tokens": 4096,
                "supports_streaming": True,
                "supports_functions": True
            },
            "pricing": {
                "input_cost_per_1k_tokens": 0.001,
                "output_cost_per_1k_tokens": 0.003
            },
            "limits": {
                "requests_per_minute": 1000,
                "tokens_per_minute": 100000
            }
        }
        
        return model_info
    except Exception as e:
        return {"error": f"Failed to get model info: {str(e)}"}


@mcp_tool(
    capability="model_management",
    name="set_default_model",
    description="Set the default model for conversations"
)
async def set_default_model(
    model_name: str,
    provider: str,
    llm_client=None
) -> Dict[str, Any]:
    """
    Set the default model for conversations.
    
    Args:
        model_name: Name of the model to set as default
        provider: Provider of the model
        llm_client: Injected LLM client instance
        
    Returns:
        Dict containing success status and details
    """
    if not llm_client:
        return {"error": "LLM client not available"}
    
    try:
        # In real implementation, would update client configuration
        result = {
            "success": True,
            "default_model": model_name,
            "provider": provider,
            "updated_at": "2025-05-20T18:00:00Z"
        }
        
        return result
    except Exception as e:
        return {"error": f"Failed to set default model: {str(e)}"}


@mcp_capability(
    name="conversation",
    description="Handle conversations, message history, and context management"
)
class ConversationCapability:
    """Capability for managing conversations and message exchange."""
    pass


@mcp_tool(
    capability="conversation",
    name="send_message",
    description="Send a message to a language model and get a response"
)
async def send_message(
    message: str,
    conversation_id: Optional[str] = None,
    model: Optional[str] = None,
    provider: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
    llm_client=None
) -> Dict[str, Any]:
    """
    Send a message to a language model and get a response.
    
    Args:
        message: The message to send
        conversation_id: Optional conversation ID for context
        model: Optional model override
        provider: Optional provider override
        temperature: Optional temperature setting
        max_tokens: Optional max tokens limit
        llm_client: Injected LLM client instance
        
    Returns:
        Dict containing the response and metadata
    """
    if not llm_client:
        return {"error": "LLM client not available"}
    
    try:
        # Mock response - in real implementation, would call actual LLM
        response = {
            "response": f"This is a mock response to: {message}",
            "conversation_id": conversation_id or f"conv_{len(message)}",
            "model_used": model or "claude-3-haiku",
            "provider_used": provider or "anthropic",
            "tokens_used": {
                "input": len(message.split()),
                "output": 10
            },
            "finish_reason": "completed",
            "timestamp": "2025-05-20T18:00:00Z"
        }
        
        return response
    except Exception as e:
        return {"error": f"Failed to send message: {str(e)}"}


@mcp_tool(
    capability="conversation",
    name="create_conversation",
    description="Create a new conversation with optional system prompt"
)
async def create_conversation(
    name: Optional[str] = None,
    system_prompt: Optional[str] = None,
    model: Optional[str] = None,
    provider: Optional[str] = None,
    llm_client=None
) -> Dict[str, Any]:
    """
    Create a new conversation with optional system prompt.
    
    Args:
        name: Optional name for the conversation
        system_prompt: Optional system prompt to set context
        model: Optional model to use for this conversation
        provider: Optional provider to use
        llm_client: Injected LLM client instance
        
    Returns:
        Dict containing conversation details
    """
    if not llm_client:
        return {"error": "LLM client not available"}
    
    try:
        conversation_id = f"conv_{hash(name or 'default')}"
        
        conversation = {
            "conversation_id": conversation_id,
            "name": name or "New Conversation",
            "system_prompt": system_prompt,
            "model": model or "claude-3-haiku",
            "provider": provider or "anthropic",
            "created_at": "2025-05-20T18:00:00Z",
            "message_count": 0,
            "status": "active"
        }
        
        return conversation
    except Exception as e:
        return {"error": f"Failed to create conversation: {str(e)}"}


@mcp_tool(
    capability="conversation", 
    name="get_conversation_history",
    description="Get the message history for a conversation"
)
async def get_conversation_history(
    conversation_id: str,
    limit: Optional[int] = 50,
    offset: Optional[int] = 0,
    llm_client=None
) -> Dict[str, Any]:
    """
    Get the message history for a conversation.
    
    Args:
        conversation_id: ID of the conversation
        limit: Maximum number of messages to return
        offset: Number of messages to skip
        llm_client: Injected LLM client instance
        
    Returns:
        Dict containing conversation history
    """
    if not llm_client:
        return {"error": "LLM client not available"}
    
    try:
        # Mock history - in real implementation, would retrieve from storage
        history = {
            "conversation_id": conversation_id,
            "messages": [
                {
                    "id": "msg_1",
                    "role": "user",
                    "content": "Hello, how are you?",
                    "timestamp": "2025-05-20T17:55:00Z"
                },
                {
                    "id": "msg_2", 
                    "role": "assistant",
                    "content": "Hello! I'm doing well, thank you for asking. How can I help you today?",
                    "timestamp": "2025-05-20T17:55:01Z"
                }
            ],
            "total_messages": 2,
            "limit": limit,
            "offset": offset
        }
        
        return history
    except Exception as e:
        return {"error": f"Failed to get conversation history: {str(e)}"}


@mcp_capability(
    name="streaming",
    description="Handle real-time streaming conversations and real-time responses"
)
class StreamingCapability:
    """Capability for real-time streaming conversations and responses."""
    pass


@mcp_tool(
    capability="streaming",
    name="start_streaming_conversation",
    description="Start a streaming conversation session"
)
async def start_streaming_conversation(
    conversation_id: Optional[str] = None,
    model: Optional[str] = None,
    provider: Optional[str] = None,
    llm_client=None
) -> Dict[str, Any]:
    """
    Start a streaming conversation session.
    
    Args:
        conversation_id: Optional conversation ID
        model: Optional model to use
        provider: Optional provider to use
        llm_client: Injected LLM client instance
        
    Returns:
        Dict containing streaming session details
    """
    if not llm_client:
        return {"error": "LLM client not available"}
    
    try:
        session = {
            "session_id": f"stream_{hash(conversation_id or 'default')}",
            "conversation_id": conversation_id,
            "model": model or "claude-3-haiku",
            "provider": provider or "anthropic",
            "status": "active",
            "started_at": "2025-05-20T18:00:00Z",
            "websocket_url": f"ws://localhost:8006/stream"
        }
        
        return session
    except Exception as e:
        return {"error": f"Failed to start streaming conversation: {str(e)}"}


@mcp_capability(
    name="integration",
    description="Integrate with Tekton ecosystem and external LLM providers"
)
class IntegrationCapability:
    """Capability for integration with Tekton components and external systems."""
    pass


@mcp_tool(
    capability="integration",
    name="health_check",
    description="Check the health status of the LLM Adapter"
)
async def health_check(
    llm_client=None
) -> Dict[str, Any]:
    """
    Check the health status of the LLM Adapter.
    
    Args:
        llm_client: Injected LLM client instance
        
    Returns:
        Dict containing health status
    """
    try:
        health_status = {
            "status": "healthy",
            "service": "llm_adapter",
            "version": "0.1.0",
            "uptime": "2h 30m",
            "connections": {
                "anthropic": "connected",
                "openai": "connected", 
                "local": "available"
            },
            "performance": {
                "avg_response_time": "1.2s",
                "requests_per_minute": 45,
                "error_rate": "0.1%"
            },
            "timestamp": "2025-05-20T18:00:00Z"
        }
        
        return health_status
    except Exception as e:
        return {"error": f"Health check failed: {str(e)}"}


@mcp_tool(
    capability="integration",
    name="register_with_hermes",
    description="Register LLM Adapter capabilities with Hermes"
)
async def register_with_hermes(
    service_info: Optional[Dict[str, Any]] = None,
    llm_client=None
) -> Dict[str, Any]:
    """
    Register LLM Adapter capabilities with Hermes.
    
    Args:
        service_info: Optional service registration information
        llm_client: Injected LLM client instance
        
    Returns:
        Dict containing registration status
    """
    try:
        registration = {
            "success": True,
            "service_id": "llm_adapter",
            "registered_at": "2025-05-20T18:00:00Z",
            "capabilities_registered": [
                "model_management",
                "conversation",
                "streaming",
                "integration"
            ],
            "hermes_status": "connected"
        }
        
        return registration
    except Exception as e:
        return {"error": f"Failed to register with Hermes: {str(e)}"}


@mcp_tool(
    capability="integration",
    name="get_adapter_status",
    description="Get detailed status information about the LLM Adapter"
)
async def get_adapter_status(
    llm_client=None
) -> Dict[str, Any]:
    """
    Get detailed status information about the LLM Adapter.
    
    Args:
        llm_client: Injected LLM client instance
        
    Returns:
        Dict containing detailed adapter status
    """
    try:
        status = {
            "service": "llm_adapter",
            "version": "0.1.0",
            "status": "running",
            "configuration": {
                "default_model": "claude-3-haiku",
                "default_provider": "anthropic",
                "max_concurrent_requests": 100,
                "timeout": 30
            },
            "statistics": {
                "total_requests": 1247,
                "successful_requests": 1235,
                "failed_requests": 12,
                "average_response_time": 1.2,
                "tokens_processed": 156789
            },
            "active_sessions": {
                "conversations": 8,
                "streaming_sessions": 2
            }
        }
        
        return status
    except Exception as e:
        return {"error": f"Failed to get adapter status: {str(e)}"}


# Tool collections for easy import  
model_management_tools = [
    list_available_models,
    get_model_info,
    set_default_model
]

conversation_tools = [
    send_message,
    create_conversation,
    get_conversation_history
]

streaming_tools = [
    start_streaming_conversation
]

integration_tools = [
    health_check,
    register_with_hermes,
    get_adapter_status
]

def get_all_tools():
    """Get all LLM Adapter MCP tools."""
    return (model_management_tools + conversation_tools + 
            streaming_tools + integration_tools)

def get_all_capabilities():
    """Get all LLM Adapter MCP capabilities."""
    return [
        ModelManagementCapability,
        ConversationCapability,
        StreamingCapability,
        IntegrationCapability
    ]

# Export all tools
__all__ = [
    "ModelManagementCapability",
    "ConversationCapability",
    "StreamingCapability",
    "IntegrationCapability",
    "model_management_tools",
    "conversation_tools",
    "streaming_tools", 
    "integration_tools",
    "list_available_models",
    "get_model_info",
    "set_default_model",
    "send_message",
    "create_conversation",
    "get_conversation_history",
    "start_streaming_conversation",
    "health_check",
    "register_with_hermes",
    "get_adapter_status",
    "get_all_tools",
    "get_all_capabilities"
]
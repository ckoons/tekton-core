"""
MCP capabilities for LLM Adapter Service.

This module defines the Model Context Protocol capabilities that LLM Adapter provides
for language model interactions, conversation management, and streaming operations.
"""

from typing import Dict, Any, List
from tekton.mcp.fastmcp.schema import MCPCapability


class ModelManagementCapability(MCPCapability):
    """Capability for language model management and configuration."""
    
    name = "model_management"
    description = "Manage and configure various language models and providers"
    version = "1.0.0"
    
    @classmethod
    def get_supported_operations(cls) -> List[str]:
        """Get list of supported operations."""
        return [
            "list_available_models",
            "get_model_info",
            "set_default_model",
            "validate_model_config",
            "update_model_settings",
            "get_model_capabilities",
            "test_model_connection",
            "get_model_pricing",
            "compare_models"
        ]
    
    @classmethod
    def get_capability_metadata(cls) -> Dict[str, Any]:
        """Get capability metadata."""
        return {
            "category": "model_orchestration",
            "provider": "llm_adapter",
            "requires_auth": False,
            "rate_limited": True,
            "supported_providers": ["anthropic", "openai", "local", "huggingface", "cohere"],
            "model_types": ["text_generation", "chat", "completion", "embedding"],
            "configuration_options": ["temperature", "max_tokens", "top_p", "frequency_penalty"],
            "authentication_methods": ["api_key", "oauth", "none"],
            "pricing_models": ["per_token", "per_request", "subscription", "free"]
        }


class ConversationCapability(MCPCapability):
    """Capability for managing conversations and message exchange."""
    
    name = "conversation"
    description = "Handle conversations, message history, and context management"
    version = "1.0.0"
    
    @classmethod
    def get_supported_operations(cls) -> List[str]:
        """Get list of supported operations."""
        return [
            "send_message",
            "create_conversation",
            "get_conversation_history",
            "clear_conversation",
            "delete_conversation",
            "update_conversation_settings",
            "export_conversation",
            "import_conversation",
            "search_conversations"
        ]
    
    @classmethod
    def get_capability_metadata(cls) -> Dict[str, Any]:
        """Get capability metadata."""
        return {
            "category": "conversation_management",
            "provider": "llm_adapter",
            "requires_auth": False,
            "conversation_features": ["history", "context", "metadata", "branching"],
            "message_types": ["user", "assistant", "system", "function"],
            "context_management": ["automatic", "manual", "sliding_window", "summarization"],
            "export_formats": ["json", "markdown", "plain_text", "csv"],
            "search_capabilities": ["content", "metadata", "date_range", "participant"]
        }


class StreamingCapability(MCPCapability):
    """Capability for real-time streaming conversations and responses."""
    
    name = "streaming"
    description = "Handle real-time streaming conversations and real-time responses"
    version = "1.0.0"
    
    @classmethod
    def get_supported_operations(cls) -> List[str]:
        """Get list of supported operations."""
        return [
            "start_streaming_conversation",
            "send_streaming_message",
            "stop_streaming_conversation",
            "get_streaming_status",
            "configure_streaming_options",
            "handle_stream_interruption",
            "resume_streaming",
            "get_partial_response"
        ]
    
    @classmethod
    def get_capability_metadata(cls) -> Dict[str, Any]:
        """Get capability metadata."""
        return {
            "category": "real_time_communication",
            "provider": "llm_adapter",
            "requires_auth": False,
            "streaming_protocols": ["websocket", "sse", "http_streaming"],
            "chunk_types": ["word", "sentence", "token", "custom"],
            "streaming_features": ["real_time", "buffered", "throttled", "adaptive"],
            "interruption_handling": ["graceful", "immediate", "queued"],
            "quality_control": ["backpressure", "flow_control", "error_recovery"]
        }


class IntegrationCapability(MCPCapability):
    """Capability for integration with Tekton components and external systems."""
    
    name = "integration"
    description = "Integrate with Tekton ecosystem and external LLM providers"
    version = "1.0.0"
    
    @classmethod
    def get_supported_operations(cls) -> List[str]:
        """Get list of supported operations."""
        return [
            "register_with_hermes",
            "sync_with_engram",
            "health_check",
            "get_adapter_status",
            "configure_webhook",
            "setup_api_proxy",
            "monitor_usage",
            "generate_usage_report"
        ]
    
    @classmethod
    def get_capability_metadata(cls) -> Dict[str, Any]:
        """Get capability metadata."""
        return {
            "category": "system_integration",
            "provider": "llm_adapter",
            "requires_auth": False,
            "integration_types": ["component", "api_proxy", "webhook", "middleware"],
            "monitoring_metrics": ["requests", "latency", "errors", "usage", "costs"],
            "health_indicators": ["connectivity", "response_time", "error_rate", "capacity"],
            "reporting_formats": ["json", "csv", "dashboard", "alerts"],
            "proxy_features": ["caching", "rate_limiting", "load_balancing", "failover"]
        }


# Export all capabilities
__all__ = [
    "ModelManagementCapability",
    "ConversationCapability",
    "StreamingCapability",
    "IntegrationCapability"
]
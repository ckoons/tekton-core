"""
Multimodal Cognitive Protocol (MCP)

This package provides the core components for multimodal information processing,
enabling standardized handling of text, code, images, and structured data.
"""

from tekton.mcp.message import (
    MCPMessage, 
    MCPResponse,
    MCPContentItem,
    MCPContentType,
    validate_message
)
from tekton.mcp.context import (
    ContextManager,
    ContextMetadata,
    create_context,
    merge_contexts,
    enhance_context
)
from tekton.mcp.processor import (
    MessageProcessor,
    process_message,
    extract_content
)
from tekton.mcp.modality import (
    ModalityProcessor,
    TextProcessor,
    CodeProcessor,
    ImageProcessor,
    StructuredDataProcessor
)
from tekton.mcp.tool_registry import (
    ToolRegistry,
    register_tool,
    find_tools_by_capability,
    execute_tool
)

__all__ = [
    # Message module
    "MCPMessage", "MCPResponse", "MCPContentItem", "MCPContentType", "validate_message",
    
    # Context module
    "ContextManager", "ContextMetadata", "create_context", "merge_contexts", "enhance_context",
    
    # Processor module
    "MessageProcessor", "process_message", "extract_content",
    
    # Modality module
    "ModalityProcessor", "TextProcessor", "CodeProcessor", "ImageProcessor", "StructuredDataProcessor",
    
    # Tool registry module
    "ToolRegistry", "register_tool", "find_tools_by_capability", "execute_tool"
]
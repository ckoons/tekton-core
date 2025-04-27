"""
Data models for the Tekton LLM Client.
"""

from enum import Enum
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field, validator


class MessageRole(str, Enum):
    """Message role in a conversation."""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    FUNCTION = "function"


class Message(BaseModel):
    """A message in a conversation."""
    role: MessageRole
    content: str
    name: Optional[str] = None
    
    @validator('role', pre=True)
    def validate_role(cls, v):
        """Validates the role and converts string to enum."""
        if isinstance(v, str):
            try:
                return MessageRole(v.lower())
            except ValueError:
                raise ValueError(f"Invalid role: {v}")
        return v


class CompletionOptions(BaseModel):
    """Options for text completion requests."""
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    stop_sequences: Optional[List[str]] = None
    top_p: Optional[float] = None
    top_k: Optional[int] = None
    presence_penalty: Optional[float] = None
    frequency_penalty: Optional[float] = None
    fallback_provider: Optional[str] = None
    fallback_model: Optional[str] = None
    timeout: int = 120
    retry_count: int = 3
    retry_delay: int = 1000  # milliseconds


class CompletionResponse(BaseModel):
    """Response from a text completion request."""
    content: str
    model: str
    provider: str
    finish_reason: Optional[str] = None
    usage: Optional[Dict[str, int]] = None
    context_id: str
    fallback: bool = False
    timestamp: str
    latency: Optional[float] = None
    error: Optional[str] = None
    
    @property
    def success(self) -> bool:
        """Returns whether the request was successful."""
        return self.error is None


class StreamingChunk(BaseModel):
    """A chunk of a streaming response."""
    chunk: str
    context_id: str
    model: str
    provider: str
    timestamp: str
    done: bool = False
    fallback: bool = False
    error: Optional[str] = None


class ProviderModel(BaseModel):
    """Information about an LLM model."""
    id: str
    name: str
    context_length: Optional[int] = None
    description: Optional[str] = None
    pricing: Optional[Dict[str, float]] = None
    capabilities: Optional[List[str]] = None


class Provider(BaseModel):
    """Information about an LLM provider."""
    name: str
    available: bool
    models: List[ProviderModel]
    description: Optional[str] = None


class AvailableProviders(BaseModel):
    """Information about all available LLM providers."""
    providers: Dict[str, Provider]
    default_provider: str
    default_model: str
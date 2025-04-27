"""
Tekton LLM Client - A unified client library for LLM integration in Tekton components.

This package provides a standardized way to interact with LLMs through the Rhetor component.
"""

from .client import TektonLLMClient
from .ws_client import TektonLLMWebSocketClient
from .exceptions import TektonLLMError, ConnectionError, TimeoutError, AuthenticationError

__version__ = '0.1.0'
__all__ = ['TektonLLMClient', 'TektonLLMWebSocketClient', 'TektonLLMError', 
           'ConnectionError', 'TimeoutError', 'AuthenticationError']
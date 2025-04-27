"""
Adapters for different LLM providers.
"""

from .base import BaseAdapter
from .rhetor import RhetorAdapter
from .fallback import LocalFallbackAdapter

__all__ = ['BaseAdapter', 'RhetorAdapter', 'LocalFallbackAdapter']
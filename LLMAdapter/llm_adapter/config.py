"""
Configuration for the LLM Adapter
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

# API configuration
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
DEFAULT_MODEL = os.environ.get("DEFAULT_MODEL", "claude-3-sonnet-20240229")

# Server configuration
HOST = os.environ.get("HOST", "localhost")
HTTP_PORT = int(os.environ.get("HTTP_PORT", 8300))
WS_PORT = int(os.environ.get("WS_PORT", 8301))

# Context-specific system prompts
SYSTEM_PROMPTS = {
    "ergon": (
        "You are the Ergon AI assistant, specialized in agent creation, automation, "
        "and tool configuration for the Tekton system. Be concise and helpful."
    ),
    "awt-team": (
        "You are the Advanced Workflow Team assistant for Tekton. You specialize in "
        "workflow automation, process design, and team collaboration. Be concise and helpful."
    ),
    "agora": (
        "You are Agora, a multi-component AI assistant for Tekton. You coordinate between "
        "different AI systems to solve complex problems. Be concise and helpful."
    ),
    "default": "You are a helpful assistant in the Tekton system.",
}

# Default LLM options
DEFAULT_MAX_TOKENS = 4000
DEFAULT_TEMPERATURE = 0.7
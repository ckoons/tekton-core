"""
Entry point for running the LLM Adapter as a module
"""

from llm_adapter.server import start_servers

if __name__ == "__main__":
    start_servers()
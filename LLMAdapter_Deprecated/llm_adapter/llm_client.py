"""
Client interface for LLM APIs (currently focused on Claude)
"""

import logging
import asyncio
from typing import Dict, Any, AsyncGenerator, Optional
from datetime import datetime

import anthropic

from .config import ANTHROPIC_API_KEY, DEFAULT_MODEL, SYSTEM_PROMPTS, DEFAULT_MAX_TOKENS, DEFAULT_TEMPERATURE

logger = logging.getLogger(__name__)

class LLMClient:
    """Client for interacting with LLM APIs"""
    
    def __init__(self):
        """Initialize the LLM client"""
        self.has_claude = bool(ANTHROPIC_API_KEY)
        self.claude_client = None
        
        if self.has_claude:
            try:
                self.claude_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
                logger.info(f"Claude client initialized with default model {DEFAULT_MODEL}")
            except Exception as e:
                logger.error(f"Error initializing Claude client: {e}")
                self.has_claude = False
        else:
            logger.warning("No Anthropic API key provided. Claude integration is disabled.")
    
    def get_system_prompt(self, context_id: str) -> str:
        """Get system prompt for the given context"""
        return SYSTEM_PROMPTS.get(context_id, SYSTEM_PROMPTS["default"])
    
    def get_available_providers(self) -> Dict[str, Any]:
        """Get available LLM providers and models"""
        providers = {}
        
        # Add Claude provider if available
        if self.has_claude:
            providers["anthropic"] = {
                "name": "Anthropic Claude",
                "available": True,
                "models": [
                    {"id": "claude-3-sonnet-20240229", "name": "Claude 3 Sonnet"},
                    {"id": "claude-3-opus-20240229", "name": "Claude 3 Opus"},
                    {"id": "claude-3-haiku-20240307", "name": "Claude 3 Haiku"}
                ]
            }
        else:
            # Add Claude as unavailable
            providers["anthropic"] = {
                "name": "Anthropic Claude",
                "available": False,
                "models": [
                    {"id": "claude-3-sonnet-20240229", "name": "Claude 3 Sonnet"},
                    {"id": "claude-3-opus-20240229", "name": "Claude 3 Opus"},
                    {"id": "claude-3-haiku-20240307", "name": "Claude 3 Haiku"}
                ]
            }
        
        # Add simulated provider (always available)
        providers["simulated"] = {
            "name": "Simulated LLM",
            "available": True,
            "models": [
                {"id": "simulated-fast", "name": "Fast Simulation"},
                {"id": "simulated-standard", "name": "Standard Simulation"}
            ]
        }
        
        return providers
    
    async def complete(
        self, 
        message: str, 
        context_id: str, 
        streaming: bool = False, 
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Complete a message with the LLM
        
        Args:
            message: User message text
            context_id: Context ID (ergon, awt-team, agora)
            streaming: Whether to stream the response
            options: Additional options for the LLM
            
        Returns:
            Dictionary with response data
        """
        options = options or {}
        
        # If we don't have Claude, return a simulated response
        if not self.has_claude or not self.claude_client:
            return await self._simulate_response(message, context_id, streaming)
        
        system_prompt = self.get_system_prompt(context_id)
        
        try:
            # Non-streaming response
            if not streaming:
                response = await asyncio.to_thread(
                    self.claude_client.messages.create,
                    model=options.get("model", DEFAULT_MODEL),
                    max_tokens=options.get("max_tokens", DEFAULT_MAX_TOKENS),
                    temperature=options.get("temperature", DEFAULT_TEMPERATURE),
                    system=system_prompt,
                    messages=[{"role": "user", "content": message}]
                )
                
                return {
                    "message": response.content[0].text,
                    "context": context_id,
                    "model": options.get("model", DEFAULT_MODEL),
                    "finished": True,
                    "timestamp": datetime.now().isoformat()
                }
            # For streaming, just return immediately - actual streaming happens in stream_completion
            else:
                return {
                    "message": "",
                    "context": context_id,
                    "model": options.get("model", DEFAULT_MODEL),
                    "streaming": True,
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error completing message with Claude: {e}")
            return {
                "error": str(e),
                "context": context_id,
                "timestamp": datetime.now().isoformat()
            }
    
    async def stream_completion(
        self, 
        message: str, 
        context_id: str, 
        options: Optional[Dict[str, Any]] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Stream a completion from the LLM
        
        Args:
            message: User message text
            context_id: Context ID (ergon, awt-team, agora)
            options: Additional options for the LLM
            
        Yields:
            Dictionaries with response chunks
        """
        options = options or {}
        
        # If we don't have Claude, return a simulated streaming response
        if not self.has_claude or not self.claude_client:
            async for chunk in self._simulate_streaming(message, context_id):
                yield chunk
            return
        
        system_prompt = self.get_system_prompt(context_id)
        
        try:
            # Create a streaming request to Claude
            stream = self.claude_client.messages.stream(
                model=options.get("model", DEFAULT_MODEL),
                max_tokens=options.get("max_tokens", DEFAULT_MAX_TOKENS),
                temperature=options.get("temperature", DEFAULT_TEMPERATURE),
                system=system_prompt,
                messages=[{"role": "user", "content": message}]
            )
            
            # Use a context manager to ensure proper cleanup
            async with asyncio.timeout(600):  # 10-minute timeout
                # This is a bit unusual - we're using async for on a sync generator
                # but we wrap each iteration in asyncio.to_thread to make it non-blocking
                async def process_stream():
                    with stream as s:
                        for text in s.text_stream:
                            yield {
                                "chunk": text,
                                "context": context_id,
                                "timestamp": datetime.now().isoformat(),
                                "done": False
                            }
                        
                        # Final message indicating completion
                        yield {
                            "chunk": "",
                            "context": context_id,
                            "timestamp": datetime.now().isoformat(),
                            "done": True
                        }
                
                async for chunk in process_stream():
                    yield chunk
                    
        except Exception as e:
            logger.error(f"Error streaming completion from Claude: {e}")
            yield {
                "error": str(e),
                "context": context_id,
                "timestamp": datetime.now().isoformat(),
                "done": True
            }
    
    async def _simulate_response(self, message: str, context_id: str, streaming: bool) -> Dict[str, Any]:
        """
        Simulate an LLM response when Claude is not available
        
        Args:
            message: User message
            context_id: Context ID
            streaming: Whether streaming was requested
            
        Returns:
            Simulated response data
        """
        # Wait a bit to simulate processing time
        await asyncio.sleep(1.0)
        
        # Create a simulated response
        simulated_response = f"I received your message: \"{message}\". This is a simulated response as I'm not connected to an LLM. To use a real LLM, you should configure the adapter with a valid ANTHROPIC_API_KEY."
        
        # Add context-specific information
        if context_id == "ergon":
            simulated_response += "\n\nThis is a simulated response from the Ergon AI assistant. In a real implementation, I would help with agent creation, automation, and tool configuration."
        elif context_id == "awt-team":
            simulated_response += "\n\nThis is a simulated response from the AWT Team assistant. In a real implementation, I would help with workflow automation and process design."
        elif context_id == "agora":
            simulated_response += "\n\nThis is a simulated response from the Agora multi-component assistant. In a real implementation, I would coordinate between different AI systems."
        
        return {
            "message": simulated_response,
            "context": context_id,
            "model": "simulated",
            "finished": True,
            "simulated": True,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _simulate_streaming(self, message: str, context_id: str) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Simulate a streaming LLM response when Claude is not available
        
        Args:
            message: User message
            context_id: Context ID
            
        Yields:
            Simulated streaming chunks
        """
        # Create a simulated response (same as non-streaming)
        simulated_response = f"I received your message: \"{message}\". This is a simulated response as I'm not connected to an LLM. To use a real LLM, you should configure the adapter with a valid ANTHROPIC_API_KEY."
        
        # Add context-specific information
        if context_id == "ergon":
            simulated_response += "\n\nThis is a simulated response from the Ergon AI assistant. In a real implementation, I would help with agent creation, automation, and tool configuration."
        elif context_id == "awt-team":
            simulated_response += "\n\nThis is a simulated response from the AWT Team assistant. In a real implementation, I would help with workflow automation and process design."
        elif context_id == "agora":
            simulated_response += "\n\nThis is a simulated response from the Agora multi-component assistant. In a real implementation, I would coordinate between different AI systems."
        
        # Break into small chunks and yield with delays
        chunk_size = 5  # Characters per chunk
        for i in range(0, len(simulated_response), chunk_size):
            chunk = simulated_response[i:i+chunk_size]
            
            # Yield the chunk
            yield {
                "chunk": chunk,
                "context": context_id,
                "timestamp": datetime.now().isoformat(),
                "done": False,
                "simulated": True
            }
            
            # Add short delay between chunks for a more realistic effect
            await asyncio.sleep(0.05)
        
        # Final message indicating completion
        yield {
            "chunk": "",
            "context": context_id,
            "timestamp": datetime.now().isoformat(),
            "done": True,
            "simulated": True
        }
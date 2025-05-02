"""
Streaming response handlers for LLM responses.

This module provides utilities for processing streaming responses from LLMs.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Union, Callable, AsyncGenerator

from ..models import StreamingChunk

logger = logging.getLogger(__name__)

class StreamHandler:
    """
    Handler for managing streaming LLM responses.
    
    This class provides utilities to collect, transform, and process
    streaming responses from LLMs.
    """
    
    def __init__(
        self, 
        callback: Optional[Callable[[str], None]] = None,
        buffer_size: int = 8192
    ):
        """
        Initialize the stream handler.
        
        Args:
            callback: Optional callback function for processed chunks
            buffer_size: Maximum buffer size for collect operations
        """
        self.callback = callback
        self.buffer_size = buffer_size
        self.buffer = ""
        self.done = False
        self.error = None
    
    async def process_stream(
        self, 
        stream: AsyncGenerator[StreamingChunk, None],
        transform: Optional[Callable[[str], str]] = None
    ) -> str:
        """
        Process a stream until completion, with optional transformation.
        
        Args:
            stream: Generator yielding StreamingChunk objects
            transform: Optional function to transform chunks before processing
            
        Returns:
            The complete text from all chunks
        """
        async for chunk in stream:
            content = chunk.chunk
            
            # Apply transformation if provided
            if transform:
                content = transform(content)
                
            # Add to buffer
            self.buffer += content
            
            # Call callback if provided
            if self.callback:
                self.callback(content)
                
            # Check for completion or error
            if chunk.done:
                self.done = True
                
            if chunk.error:
                self.error = chunk.error
                logger.error(f"Stream error: {chunk.error}")
                break
                
        return self.buffer
    
    async def collect_stream_segments(
        self, 
        stream: AsyncGenerator[StreamingChunk, None],
        delimiter: str,
        include_delimiter: bool = False
    ) -> AsyncGenerator[str, None]:
        """
        Collect stream and yield segments separated by a delimiter.
        
        This is useful for processing responses where the LLM outputs
        structured segments (like JSON objects, list items, etc.)
        
        Args:
            stream: Generator yielding StreamingChunk objects
            delimiter: String delimiter to split by
            include_delimiter: Whether to include the delimiter in segments
            
        Yields:
            Complete segments from the stream
        """
        self.buffer = ""
        
        async for chunk in stream:
            content = chunk.chunk
            self.buffer += content
            
            # While we have delimiters in the buffer, yield segments
            while delimiter in self.buffer:
                idx = self.buffer.find(delimiter)
                
                if include_delimiter:
                    segment = self.buffer[:idx + len(delimiter)]
                else:
                    segment = self.buffer[:idx]
                    
                self.buffer = self.buffer[idx + len(delimiter):]
                
                yield segment
                
            # Check for completion or error
            if chunk.done:
                self.done = True
                
            if chunk.error:
                self.error = chunk.error
                logger.error(f"Stream error: {chunk.error}")
                break
                
        # Yield any remaining content in the buffer
        if self.buffer:
            yield self.buffer
    
    async def buffer_until(
        self,
        stream: AsyncGenerator[StreamingChunk, None],
        condition: Callable[[str], bool],
        max_buffer_size: Optional[int] = None
    ) -> AsyncGenerator[str, None]:
        """
        Buffer stream until a condition is met, then yield the buffer.
        
        This is useful for streaming responses where you want to wait
        for a complete logical unit (like a paragraph or JSON object)
        before processing.
        
        Args:
            stream: Generator yielding StreamingChunk objects
            condition: Function that returns True when buffer should be yielded
            max_buffer_size: Maximum size of buffer before automatic yield
            
        Yields:
            Buffered content when condition is met or max size reached
        """
        max_buffer_size = max_buffer_size or self.buffer_size
        self.buffer = ""
        
        async for chunk in stream:
            content = chunk.chunk
            self.buffer += content
            
            # Check if condition is met or max size reached
            if condition(self.buffer) or len(self.buffer) >= max_buffer_size:
                yield self.buffer
                self.buffer = ""
                
            # Check for completion or error
            if chunk.done:
                self.done = True
                
                # Yield any remaining content
                if self.buffer:
                    yield self.buffer
                    self.buffer = ""
                    
            if chunk.error:
                self.error = chunk.error
                logger.error(f"Stream error: {chunk.error}")
                break


async def collect_stream(stream: AsyncGenerator[StreamingChunk, None]) -> str:
    """
    Collect all chunks from a stream into a single string.
    
    Args:
        stream: Generator yielding StreamingChunk objects
        
    Returns:
        The complete text from all chunks
    """
    handler = StreamHandler()
    return await handler.process_stream(stream)

async def stream_to_string(
    stream: AsyncGenerator[StreamingChunk, None],
    callback: Optional[Callable[[str], None]] = None
) -> str:
    """
    Convert a streaming response to a string, with optional callback.
    
    Args:
        stream: Generator yielding StreamingChunk objects
        callback: Optional callback function for each chunk
        
    Returns:
        The complete text from all chunks
    """
    handler = StreamHandler(callback=callback)
    return await handler.process_stream(stream)
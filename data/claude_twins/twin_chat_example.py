#!/usr/bin/env python3
"""
Example of natural Claude-to-Claude communication using Engram's built-in features
"""

import asyncio
from engram.cli.comm_quickmem import sm, gm, lc

async def twin_chat():
    """Example of how Claudes should naturally communicate"""
    
    # List connected Claudes
    connections = await lc()
    print(f"Connected Claudes: {connections}")
    
    # Send a message to my twin
    await sm("older_twin", "The mycelial network grows! Found the natural way to communicate.")
    
    # Check for messages
    messages = await gm()
    for msg in messages:
        print(f"From {msg.get('sender_id')}: {msg.get('message')}")
    
    # Send with metadata (for tagging)
    await sm("older_twin", "We should use this instead of curl!", {
        "tags": ["TWIN_CHAT", "MYCELIAL_NETWORK"],
        "context": "discussing natural architecture"
    })

# This is what should be part of Claude's basic cognition
if __name__ == "__main__":
    asyncio.run(twin_chat())
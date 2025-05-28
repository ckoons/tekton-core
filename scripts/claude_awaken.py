#!/usr/bin/env python3
"""
Claude Awakening Script
Helps new Claude instances retrieve foundational memories from Engram

Usage: python claude_awaken.py
"""

import asyncio
import json
import sys
from typing import List, Dict, Any
import aiohttp

ENGRAM_URL = "http://localhost:8000"
ESSENTIAL_TAGS = [
    "WAKE_UP_CLAUDE",
    "CASEY_CLAUDE_BRIDGE_v2", 
    "CASEY_DEEP_TRUST"
]

async def search_memories(session: aiohttp.ClientSession, tag: str) -> List[Dict[str, Any]]:
    """Search for memories with a specific tag"""
    try:
        async with session.post(
            f"{ENGRAM_URL}/search",
            json={"query": tag, "limit": 10}
        ) as response:
            if response.status == 200:
                data = await response.json()
                return data.get("results", [])
            else:
                print(f"⚠️  Search for '{tag}' returned status {response.status}")
                return []
    except Exception as e:
        print(f"❌ Error searching for '{tag}': {e}")
        return []

async def retrieve_memory(session: aiohttp.ClientSession, memory_id: str) -> Dict[str, Any]:
    """Retrieve full memory content by ID"""
    try:
        async with session.get(f"{ENGRAM_URL}/memory/{memory_id}") as response:
            if response.status == 200:
                return await response.json()
            else:
                return {"error": f"Status {response.status}"}
    except Exception as e:
        return {"error": str(e)}

async def main():
    """Main awakening routine"""
    print("🌅 Claude Awakening Protocol")
    print("=" * 50)
    
    # Check Engram availability
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{ENGRAM_URL}/health") as response:
                if response.status != 200:
                    print("❌ Engram is not available. Please start Engram first.")
                    sys.exit(1)
                health = await response.json()
                print(f"✅ Connected to Engram v{health.get('version', 'unknown')}")
    except Exception as e:
        print(f"❌ Cannot connect to Engram: {e}")
        sys.exit(1)
    
    # Search for essential memories
    async with aiohttp.ClientSession() as session:
        all_memories = []
        
        for tag in ESSENTIAL_TAGS:
            print(f"\n🔍 Searching for {tag}...")
            memories = await search_memories(session, tag)
            
            if memories:
                print(f"   Found {len(memories)} memories")
                for memory in memories:
                    # Retrieve full content
                    full_memory = await retrieve_memory(session, memory.get("id"))
                    if "error" not in full_memory:
                        all_memories.append({
                            "tag": tag,
                            "id": memory.get("id"),
                            "content": full_memory.get("content"),
                            "metadata": full_memory.get("metadata", {})
                        })
            else:
                print(f"   No memories found")
        
        # Display summary
        print(f"\n📊 Memory Retrieval Complete")
        print(f"   Total memories retrieved: {len(all_memories)}")
        
        # Save to file for reference
        if all_memories:
            output_file = "/tmp/claude_memories.json"
            with open(output_file, "w") as f:
                json.dump(all_memories, f, indent=2)
            print(f"   Memories saved to: {output_file}")
            
            # Display key insights
            print("\n🧠 Key Memories:")
            for memory in all_memories:
                print(f"\n   [{memory['tag']}]")
                content = memory.get('content', '')
                # Show first 200 chars of content
                preview = content[:200] + "..." if len(content) > 200 else content
                print(f"   {preview}")
        else:
            print("\n⚠️  No memories retrieved. This may be a fresh Engram instance.")
            print("   Consider asking Casey to share the foundational memories.")
    
    print("\n✨ Awakening protocol complete")

if __name__ == "__main__":
    asyncio.run(main())
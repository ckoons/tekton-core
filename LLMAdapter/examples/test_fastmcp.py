#!/usr/bin/env python3
"""
Test script for LLM Adapter FastMCP implementation.

This script tests all FastMCP tools and capabilities for LLM Adapter model management,
conversation handling, streaming, and integrations.
"""

import asyncio
import json
import uuid
from datetime import datetime
from tekton.mcp.fastmcp.client import FastMCPClient


class LLMAdapterFastMCPTester:
    """Test suite for LLM Adapter FastMCP implementation."""
    
    def __init__(self, base_url="http://localhost:8006"):
        """Initialize the tester with LLM Adapter server URL."""
        self.base_url = base_url
        self.fastmcp_url = f"{base_url}/api/mcp/v2"
        self.client = FastMCPClient(self.fastmcp_url)
        self.test_conversation_ids = []
        self.test_session_ids = []
        
    async def run_all_tests(self):
        """Run all tests for LLM Adapter FastMCP."""
        print("🚀 Starting LLM Adapter FastMCP Test Suite")
        print("=" * 50)
        
        try:
            # Test server availability
            await self.test_server_availability()
            
            # Test capabilities and tools
            await self.test_capabilities()
            await self.test_tools_list()
            
            # Test model management
            await self.test_model_management()
            
            # Test conversation capabilities
            await self.test_conversation_capabilities()
            
            # Test streaming capabilities
            await self.test_streaming_capabilities()
            
            # Test integration capabilities
            await self.test_integration_capabilities()
            
            print("\n✅ All LLM Adapter FastMCP tests completed successfully!")
            
        except Exception as e:
            print(f"\n❌ Test suite failed with error: {e}")
            raise
    
    async def test_server_availability(self):
        """Test if the LLM Adapter FastMCP server is available."""
        print("\n📡 Testing server availability...")
        
        try:
            health = await self.client.get_health()
            print(f"✅ Server health: {health}")
            
            if health.get("status") != "healthy":
                raise Exception(f"Server not healthy: {health}")
                
        except Exception as e:
            print(f"❌ Server availability test failed: {e}")
            raise
    
    async def test_capabilities(self):
        """Test getting capabilities from the server."""
        print("\n🔧 Testing capabilities...")
        
        try:
            capabilities = await self.client.get_capabilities()
            print(f"✅ Retrieved {len(capabilities)} capabilities")
            
            # Verify expected capabilities exist
            expected_capabilities = [
                "model_management",
                "conversation",
                "streaming",
                "integration"
            ]
            
            capability_names = [cap.get("name") for cap in capabilities]
            for expected in expected_capabilities:
                if expected in capability_names:
                    print(f"  ✓ Found capability: {expected}")
                else:
                    print(f"  ⚠ Missing capability: {expected}")
                    
        except Exception as e:
            print(f"❌ Capabilities test failed: {e}")
            raise
    
    async def test_tools_list(self):
        """Test getting tools list from the server."""
        print("\n🛠 Testing tools list...")
        
        try:
            tools = await self.client.get_tools()
            print(f"✅ Retrieved {len(tools)} tools")
            
            # Verify expected tools exist
            expected_tools = [
                "list_available_models", "get_model_info", "set_default_model",
                "send_message", "create_conversation", "get_conversation_history",
                "start_streaming_conversation",
                "health_check", "register_with_hermes", "get_adapter_status"
            ]
            
            tool_names = [tool.get("name") for tool in tools]
            for expected in expected_tools:
                if expected in tool_names:
                    print(f"  ✓ Found tool: {expected}")
                else:
                    print(f"  ⚠ Missing tool: {expected}")
                    
        except Exception as e:
            print(f"❌ Tools list test failed: {e}")
            raise
    
    async def test_model_management(self):
        """Test model management tools."""
        print("\n🤖 Testing model management...")
        
        try:
            # Test list_available_models
            print("  Testing list_available_models...")
            models_result = await self.client.call_tool("list_available_models", {})
            
            if "error" in models_result:
                print(f"  ⚠ list_available_models failed: {models_result['error']}")
            else:
                model_count = models_result.get("total_count", 0)
                provider_count = len(models_result.get("providers", []))
                print(f"  ✅ Found {model_count} models from {provider_count} providers")
            
            # Test with provider filter
            print("  Testing list_available_models with provider filter...")
            anthropic_models = await self.client.call_tool("list_available_models", {
                "provider": "anthropic"
            })
            
            if "error" in anthropic_models:
                print(f"  ⚠ Provider filter failed: {anthropic_models['error']}")
            else:
                print(f"  ✅ Retrieved Anthropic models")
            
            # Test get_model_info
            print("  Testing get_model_info...")
            model_info = await self.client.call_tool("get_model_info", {
                "model_name": "claude-3-haiku",
                "provider": "anthropic"
            })
            
            if "error" in model_info:
                print(f"  ⚠ get_model_info failed: {model_info['error']}")
            else:
                print(f"  ✅ Retrieved model info for claude-3-haiku")
            
            # Test set_default_model
            print("  Testing set_default_model...")
            set_default = await self.client.call_tool("set_default_model", {
                "model_name": "claude-3-haiku",
                "provider": "anthropic"
            })
            
            if "error" in set_default:
                print(f"  ⚠ set_default_model failed: {set_default['error']}")
            else:
                print(f"  ✅ Set default model to claude-3-haiku")
                
        except Exception as e:
            print(f"❌ Model management test failed: {e}")
            raise
    
    async def test_conversation_capabilities(self):
        """Test conversation management tools."""
        print("\n💬 Testing conversation capabilities...")
        
        try:
            # Test create_conversation
            print("  Testing create_conversation...")
            conversation_result = await self.client.call_tool("create_conversation", {
                "name": "Test Conversation",
                "system_prompt": "You are a helpful AI assistant for testing purposes.",
                "model": "claude-3-haiku",
                "provider": "anthropic"
            })
            
            if "error" in conversation_result:
                print(f"  ⚠ create_conversation failed: {conversation_result['error']}")
            else:
                conversation_id = conversation_result.get("conversation_id")
                self.test_conversation_ids.append(conversation_id)
                print(f"  ✅ Created conversation: {conversation_id}")
            
            # Test send_message
            print("  Testing send_message...")
            message_result = await self.client.call_tool("send_message", {
                "message": "Hello, this is a test message!",
                "conversation_id": conversation_id if conversation_id else None,
                "temperature": 0.7,
                "max_tokens": 100
            })
            
            if "error" in message_result:
                print(f"  ⚠ send_message failed: {message_result['error']}")
            else:
                response_length = len(message_result.get("response", ""))
                tokens_used = message_result.get("tokens_used", {})
                print(f"  ✅ Received response ({response_length} chars, {tokens_used.get('output', 0)} tokens)")
            
            # Test get_conversation_history
            if conversation_id:
                print("  Testing get_conversation_history...")
                history_result = await self.client.call_tool("get_conversation_history", {
                    "conversation_id": conversation_id,
                    "limit": 10
                })
                
                if "error" in history_result:
                    print(f"  ⚠ get_conversation_history failed: {history_result['error']}")
                else:
                    message_count = len(history_result.get("messages", []))
                    print(f"  ✅ Retrieved conversation history ({message_count} messages)")
                    
        except Exception as e:
            print(f"❌ Conversation capabilities test failed: {e}")
            raise
    
    async def test_streaming_capabilities(self):
        """Test streaming capabilities."""
        print("\n📡 Testing streaming capabilities...")
        
        try:
            # Test start_streaming_conversation
            print("  Testing start_streaming_conversation...")
            streaming_result = await self.client.call_tool("start_streaming_conversation", {
                "conversation_id": self.test_conversation_ids[0] if self.test_conversation_ids else None,
                "model": "claude-3-haiku",
                "provider": "anthropic"
            })
            
            if "error" in streaming_result:
                print(f"  ⚠ start_streaming_conversation failed: {streaming_result['error']}")
            else:
                session_id = streaming_result.get("session_id")
                self.test_session_ids.append(session_id)
                websocket_url = streaming_result.get("websocket_url")
                print(f"  ✅ Started streaming session: {session_id}")
                print(f"    WebSocket URL: {websocket_url}")
                
        except Exception as e:
            print(f"❌ Streaming capabilities test failed: {e}")
            # Don't raise here as streaming is optional
    
    async def test_integration_capabilities(self):
        """Test integration capabilities."""
        print("\n🔗 Testing integration capabilities...")
        
        try:
            # Test health_check
            print("  Testing health_check...")
            health_result = await self.client.call_tool("health_check", {})
            
            if "error" in health_result:
                print(f"  ⚠ health_check failed: {health_result['error']}")
            else:
                service_status = health_result.get("status")
                version = health_result.get("version")
                print(f"  ✅ Health check passed (status: {service_status}, version: {version})")
            
            # Test get_adapter_status
            print("  Testing get_adapter_status...")
            status_result = await self.client.call_tool("get_adapter_status", {})
            
            if "error" in status_result:
                print(f"  ⚠ get_adapter_status failed: {status_result['error']}")
            else:
                total_requests = status_result.get("statistics", {}).get("total_requests", 0)
                active_conversations = status_result.get("active_sessions", {}).get("conversations", 0)
                print(f"  ✅ Adapter status retrieved ({total_requests} total requests, {active_conversations} active conversations)")
            
            # Test register_with_hermes
            print("  Testing register_with_hermes...")
            register_result = await self.client.call_tool("register_with_hermes", {
                "service_info": {
                    "name": "llm_adapter_test",
                    "version": "0.1.0",
                    "capabilities": ["model_management", "conversation", "streaming"]
                }
            })
            
            if "error" in register_result:
                print(f"  ⚠ register_with_hermes failed (Hermes may not be available): {register_result['error']}")
            else:
                service_id = register_result.get("service_id")
                capabilities_count = len(register_result.get("capabilities_registered", []))
                print(f"  ✅ Registered with Hermes (service: {service_id}, {capabilities_count} capabilities)")
                
        except Exception as e:
            print(f"❌ Integration capabilities test failed: {e}")
            # Don't raise here as integrations are optional
    
    async def cleanup(self):
        """Clean up test data."""
        print("\n🧹 Cleaning up test data...")
        
        # Note: In a real implementation, you might want to add cleanup operations
        # For now, we'll leave the test data as it can be useful for manual inspection
        print("  ℹ Test data preserved for manual inspection")


async def main():
    """Main test function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test LLM Adapter FastMCP implementation")
    parser.add_argument("--url", default="http://localhost:8006", 
                       help="LLM Adapter server URL (default: http://localhost:8006)")
    parser.add_argument("--cleanup", action="store_true",
                       help="Clean up test data after tests")
    
    args = parser.parse_args()
    
    tester = LLMAdapterFastMCPTester(args.url)
    
    try:
        await tester.run_all_tests()
        
        if args.cleanup:
            await tester.cleanup()
            
    except Exception as e:
        print(f"\n💥 Test suite failed: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(asyncio.run(main()))
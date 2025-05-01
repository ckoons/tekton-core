# LLMAdapter Technical Documentation

## Architecture Overview

The LLMAdapter is designed as a centralized interface for Large Language Model interactions within the Tekton ecosystem. Its architecture focuses on providing a standardized access layer for various LLM providers while handling authentication, caching, rate limiting, and failover.

### Core Components

1. **HTTP Server**
   - Provides RESTful API endpoints for synchronous interactions
   - Handles authentication and request validation
   - Implements rate limiting and usage tracking
   - Processes API requests and formats responses

2. **WebSocket Server**
   - Manages persistent connections for streaming responses
   - Implements the message protocol for real-time interactions
   - Handles connection lifecycle and error scenarios
   - Provides event-based communication patterns

3. **LLM Client**
   - Abstracts provider-specific API differences
   - Manages authentication with LLM providers
   - Handles request formatting and response parsing
   - Implements retry and timeout logic

4. **Provider Manager**
   - Discovers and registers available LLM providers
   - Maintains provider status and capabilities
   - Handles provider selection and failover
   - Manages provider-specific configuration

5. **Response Cache**
   - Caches responses for improved performance
   - Implements cache invalidation strategies
   - Optimizes for common request patterns
   - Manages memory usage for efficient caching

## Internal System Design

### Request Processing Pipeline

The request processing follows these stages:

1. **Authentication**: Validate API key and permissions
2. **Validation**: Verify request format and parameters
3. **Rate Limiting**: Check usage against rate limits
4. **Provider Selection**: Select appropriate provider based on model and availability
5. **Request Transformation**: Transform to provider-specific format
6. **Execution**: Send request to provider and handle response
7. **Response Transformation**: Transform to standardized format
8. **Logging**: Record usage and performance metrics

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│Authentication│     │  Validation │     │Rate Limiting│     │  Provider   │
│             ├────►│             ├────►│             ├────►│  Selection   │
└─────────────┘     └─────────────┘     └─────────────┘     └──────┬──────┘
                                                                   │
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌──────▼──────┐
│   Logging   │     │  Response   │     │  Execution  │     │   Request   │
│             │◄────┤Transformation◄────┤             │◄────┤Transformation│
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
```

### Provider Architecture

The provider system is designed for extensibility:

```python
class LLMProvider:
    """Base class for LLM providers"""
    
    def __init__(self, config=None):
        self.config = config or {}
        self.name = "base_provider"
        self.models = []
        self.initialized = False
        
    async def initialize(self):
        """Initialize the provider"""
        self.initialized = True
        return True
        
    async def generate_completion(self, model, prompt, parameters=None):
        """Generate a completion for the given prompt"""
        raise NotImplementedError
        
    async def generate_chat_completion(self, model, messages, parameters=None):
        """Generate a chat completion for the given messages"""
        raise NotImplementedError
        
    async def stream_chat_completion(self, model, messages, parameters=None):
        """Stream a chat completion for the given messages"""
        raise NotImplementedError
        
    async def generate_embeddings(self, model, texts):
        """Generate embeddings for the given texts"""
        raise NotImplementedError
        
    def get_available_models(self):
        """Get available models for this provider"""
        return self.models
        
    def is_available(self):
        """Check if the provider is available"""
        return self.initialized
```

Provider implementations:

```python
class OpenAIProvider(LLMProvider):
    """OpenAI provider implementation"""
    
    def __init__(self, config=None):
        super().__init__(config)
        self.name = "openai"
        self.api_key = config.get("api_key")
        self.models = [
            {"id": "gpt-4", "name": "GPT-4", "context_length": 8192},
            {"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo", "context_length": 4096},
            {"id": "text-embedding-ada-002", "name": "Text Embedding Ada 002"}
        ]
        self.client = None
        
    async def initialize(self):
        """Initialize the OpenAI client"""
        try:
            import openai
            self.client = openai.AsyncClient(api_key=self.api_key)
            # Test connection
            await self.client.models.list()
            self.initialized = True
            return True
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI provider: {e}")
            return False
            
    async def generate_chat_completion(self, model, messages, parameters=None):
        """Generate a chat completion using OpenAI API"""
        if not self.initialized:
            raise ProviderNotInitializedError("OpenAI provider not initialized")
            
        params = parameters or {}
        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=[{"role": m["role"], "content": m["content"]} for m in messages],
                temperature=params.get("temperature", 0.7),
                max_tokens=params.get("max_tokens", 1024),
                top_p=params.get("top_p", 1.0),
                frequency_penalty=params.get("frequency_penalty", 0.0),
                presence_penalty=params.get("presence_penalty", 0.0),
                stop=params.get("stop", None)
            )
            
            return {
                "id": response.id,
                "object": "chat.completion",
                "created": int(time.time()),
                "model": model,
                "content": response.choices[0].message.content,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                "finish_reason": response.choices[0].finish_reason
            }
        except Exception as e:
            logger.error(f"OpenAI completion error: {e}")
            raise ProviderError(f"OpenAI error: {str(e)}")
```

### HTTP Server Implementation

The HTTP server is built using FastAPI:

```python
from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from llm_adapter.config import Config
from llm_adapter.provider_manager import ProviderManager

app = FastAPI(title="LLM Adapter API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize configuration and provider manager
config = Config()
provider_manager = ProviderManager(config)

# Authentication dependency
async def verify_api_key(authorization: str = Header(None)):
    if authorization is None:
        raise HTTPException(status_code=401, detail="Missing API key")
        
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization format")
        
    api_key = authorization.replace("Bearer ", "")
    
    if not await config.verify_api_key(api_key):
        raise HTTPException(status_code=401, detail="Invalid API key")
        
    return api_key

# API routes
@app.get("/api/providers")
async def get_providers(api_key: str = Depends(verify_api_key)):
    """Get available providers"""
    providers = await provider_manager.get_providers()
    return {"providers": providers}

@app.post("/api/chat/completions")
async def create_chat_completion(
    request: ChatCompletionRequest,
    api_key: str = Depends(verify_api_key)
):
    """Create a chat completion"""
    try:
        provider = await provider_manager.get_provider_for_model(request.model)
        
        result = await provider.generate_chat_completion(
            model=request.model,
            messages=request.messages,
            parameters=request.parameters
        )
        
        return result
    except ProviderNotFoundError:
        raise HTTPException(status_code=404, detail=f"Provider for model {request.model} not found")
    except ProviderError as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### WebSocket Server Implementation

The WebSocket server handles streaming completions:

```python
from fastapi import WebSocket, WebSocketDisconnect
import json
import asyncio
import logging

logger = logging.getLogger(__name__)

class ConnectionManager:
    """Manage WebSocket connections"""
    
    def __init__(self):
        self.active_connections = {}
        self.request_handlers = {}
        
    async def connect(self, websocket: WebSocket, client_id: str):
        """Accept a new WebSocket connection"""
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logger.info(f"Client {client_id} connected")
        
    def disconnect(self, client_id: str):
        """Remove a disconnected client"""
        if client_id in self.active_connections:
            del self.active_connections[client_id]
        logger.info(f"Client {client_id} disconnected")
        
    async def send_message(self, client_id: str, message_type: str, message_id: str, data: dict):
        """Send a message to a client"""
        if client_id not in self.active_connections:
            logger.warning(f"Attempted to send message to disconnected client: {client_id}")
            return
            
        message = {
            "type": message_type,
            "id": message_id,
            "data": data
        }
        
        try:
            await self.active_connections[client_id].send_text(json.dumps(message))
        except Exception as e:
            logger.error(f"Error sending message to client {client_id}: {e}")
            
    async def broadcast(self, message_type: str, data: dict):
        """Broadcast a message to all connected clients"""
        for client_id in self.active_connections:
            await self.send_message(client_id, message_type, "broadcast", data)
            
    async def register_request_handler(self, request_id: str, handler):
        """Register a request handler for cancellation"""
        self.request_handlers[request_id] = handler
        
    async def cancel_request(self, request_id: str):
        """Cancel an ongoing request"""
        if request_id in self.request_handlers:
            handler = self.request_handlers[request_id]
            await handler.cancel()
            del self.request_handlers[request_id]
            return True
        return False

# WebSocket route
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    client_id = str(uuid.uuid4())
    manager = ConnectionManager()
    
    await manager.connect(websocket, client_id)
    
    try:
        while True:
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                message_type = message.get("type")
                message_id = message.get("id")
                
                if message_type == "chat.completion":
                    # Create a task for handling the completion
                    asyncio.create_task(
                        handle_chat_completion(
                            manager, client_id, message_id, message.get("data", {})
                        )
                    )
                elif message_type == "cancel":
                    # Handle request cancellation
                    request_id = message.get("data", {}).get("request_id")
                    if request_id:
                        success = await manager.cancel_request(request_id)
                        await manager.send_message(
                            client_id, 
                            "cancel.result", 
                            message_id,
                            {
                                "request_id": request_id,
                                "status": "cancelled" if success else "not_found"
                            }
                        )
                    
            except json.JSONDecodeError:
                await manager.send_message(
                    client_id,
                    "error",
                    "system",
                    {"message": "Invalid JSON message"}
                )
            except Exception as e:
                logger.error(f"Error processing message: {e}")
                await manager.send_message(
                    client_id,
                    "error",
                    "system",
                    {"message": "Internal server error"}
                )
    
    except WebSocketDisconnect:
        manager.disconnect(client_id)
```

### Provider Manager Implementation

The provider manager handles provider registration and selection:

```python
class ProviderManager:
    """Manage LLM providers"""
    
    def __init__(self, config):
        self.config = config
        self.providers = {}
        self.model_to_provider = {}
        self.initialized = False
        
    async def initialize(self):
        """Initialize all configured providers"""
        if self.initialized:
            return
            
        # Register providers
        for provider_config in self.config.get_providers():
            provider_name = provider_config["name"]
            provider_type = provider_config["type"]
            
            try:
                provider_class = self._get_provider_class(provider_type)
                provider = provider_class(provider_config)
                
                # Initialize provider
                success = await provider.initialize()
                if success:
                    self.providers[provider_name] = provider
                    
                    # Map models to provider
                    for model in provider.get_available_models():
                        self.model_to_provider[model["id"]] = provider_name
                    
                    logger.info(f"Initialized provider: {provider_name}")
                else:
                    logger.warning(f"Failed to initialize provider: {provider_name}")
            except Exception as e:
                logger.error(f"Error initializing provider {provider_name}: {e}")
                
        self.initialized = True
        
    def _get_provider_class(self, provider_type):
        """Get provider class based on type"""
        if provider_type == "openai":
            return OpenAIProvider
        elif provider_type == "anthropic":
            return AnthropicProvider
        elif provider_type == "local":
            return LocalProvider
        else:
            raise ValueError(f"Unknown provider type: {provider_type}")
            
    async def get_providers(self):
        """Get all available providers with their models"""
        if not self.initialized:
            await self.initialize()
            
        provider_list = []
        for name, provider in self.providers.items():
            provider_info = {
                "id": name,
                "name": provider.name,
                "isAvailable": provider.is_available(),
                "models": provider.get_available_models()
            }
            provider_list.append(provider_info)
            
        return provider_list
        
    async def get_provider(self, provider_name):
        """Get provider by name"""
        if not self.initialized:
            await self.initialize()
            
        if provider_name not in self.providers:
            raise ProviderNotFoundError(f"Provider not found: {provider_name}")
            
        return self.providers[provider_name]
        
    async def get_provider_for_model(self, model_id):
        """Get provider for a specific model"""
        if not self.initialized:
            await self.initialize()
            
        if model_id not in self.model_to_provider:
            raise ProviderNotFoundError(f"Provider for model {model_id} not found")
            
        provider_name = self.model_to_provider[model_id]
        return self.providers[provider_name]
```

## Response Caching System

The caching system optimizes performance for repeated queries:

```python
class ResponseCache:
    """Cache for LLM responses"""
    
    def __init__(self, max_size=1000, ttl_seconds=3600):
        self.cache = {}
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.expiration_times = {}
        self.access_times = {}
        self.lock = asyncio.Lock()
        
    async def get(self, key):
        """Get a value from the cache"""
        async with self.lock:
            if key not in self.cache:
                return None
                
            # Check if expired
            if time.time() > self.expiration_times.get(key, 0):
                await self._remove(key)
                return None
                
            # Update access time
            self.access_times[key] = time.time()
            
            return self.cache[key]
            
    async def set(self, key, value):
        """Set a value in the cache"""
        async with self.lock:
            # Check if cache is full
            if len(self.cache) >= self.max_size and key not in self.cache:
                await self._evict_oldest()
                
            self.cache[key] = value
            self.expiration_times[key] = time.time() + self.ttl_seconds
            self.access_times[key] = time.time()
            
    async def invalidate(self, key):
        """Invalidate a cache entry"""
        async with self.lock:
            await self._remove(key)
            
    async def clear(self):
        """Clear the entire cache"""
        async with self.lock:
            self.cache = {}
            self.expiration_times = {}
            self.access_times = {}
            
    async def _remove(self, key):
        """Remove a key from the cache"""
        if key in self.cache:
            del self.cache[key]
        if key in self.expiration_times:
            del self.expiration_times[key]
        if key in self.access_times:
            del self.access_times[key]
            
    async def _evict_oldest(self):
        """Evict the least recently used item"""
        if not self.access_times:
            return
            
        oldest_key = min(self.access_times, key=self.access_times.get)
        await self._remove(oldest_key)
        
    def generate_key(self, provider, model, messages, parameters):
        """Generate a cache key"""
        # Normalize parameters by sorting keys
        params_str = json.dumps(parameters or {}, sort_keys=True)
        
        # Serialize messages
        messages_str = json.dumps(messages, sort_keys=True)
        
        # Create hash
        key_string = f"{provider}:{model}:{messages_str}:{params_str}"
        return hashlib.md5(key_string.encode()).hexdigest()
```

## Authentication System

The authentication system manages API keys and permissions:

```python
class APIKey:
    """API key with permissions"""
    
    def __init__(self, key_id, key, name, permissions, expires_at=None):
        self.key_id = key_id
        self.key = key
        self.name = name
        self.permissions = permissions
        self.created_at = time.time()
        self.expires_at = expires_at
        
    def is_valid(self):
        """Check if the key is still valid"""
        if self.expires_at is None:
            return True
            
        return time.time() < self.expires_at
        
    def has_permission(self, permission):
        """Check if the key has a specific permission"""
        # Wildcard permission
        if "*" in self.permissions:
            return True
            
        # Check specific permission
        return permission in self.permissions
        
    def to_dict(self, include_key=False):
        """Convert to dictionary representation"""
        result = {
            "key_id": self.key_id,
            "name": self.name,
            "permissions": self.permissions,
            "created_at": self.created_at,
            "expires_at": self.expires_at
        }
        
        if include_key:
            result["key"] = self.key
            
        return result

class AuthManager:
    """Manage API keys and authentication"""
    
    def __init__(self, config):
        self.config = config
        self.api_keys = {}
        self.load_api_keys()
        
    def load_api_keys(self):
        """Load API keys from configuration"""
        keys_config = self.config.get_api_keys()
        
        for key_config in keys_config:
            key_id = key_config["key_id"]
            key = key_config["key"]
            name = key_config.get("name", "Unnamed Key")
            permissions = key_config.get("permissions", [])
            expires_at = key_config.get("expires_at")
            
            api_key = APIKey(key_id, key, name, permissions, expires_at)
            self.api_keys[key] = api_key
            
    def verify_key(self, key):
        """Verify an API key"""
        if key not in self.api_keys:
            return False
            
        api_key = self.api_keys[key]
        return api_key.is_valid()
        
    def check_permission(self, key, permission):
        """Check if a key has a specific permission"""
        if key not in self.api_keys:
            return False
            
        api_key = self.api_keys[key]
        if not api_key.is_valid():
            return False
            
        return api_key.has_permission(permission)
        
    def generate_key(self, name, permissions, expires_at=None):
        """Generate a new API key"""
        key_id = f"key_{uuid.uuid4().hex[:12]}"
        key = f"llma_sk_{uuid.uuid4().hex}"
        
        api_key = APIKey(key_id, key, name, permissions, expires_at)
        self.api_keys[key] = api_key
        
        # Save to configuration
        self.config.add_api_key(api_key.to_dict(include_key=True))
        
        return api_key
        
    def revoke_key(self, key_id):
        """Revoke an API key"""
        for key, api_key in list(self.api_keys.items()):
            if api_key.key_id == key_id:
                del self.api_keys[key]
                self.config.remove_api_key(key_id)
                return True
                
        return False
```

## Rate Limiting System

The rate limiting system controls API usage:

```python
class RateLimiter:
    """Rate limiting for API endpoints"""
    
    def __init__(self, config):
        self.config = config
        self.limits = config.get_rate_limits()
        self.counters = {}
        self.locks = {}
        
    async def check_limit(self, key, endpoint):
        """Check if request is within rate limits"""
        rate_key = f"{key}:{endpoint}"
        
        # Get lock for this key
        if rate_key not in self.locks:
            self.locks[rate_key] = asyncio.Lock()
            
        async with self.locks[rate_key]:
            # Get counter
            if rate_key not in self.counters:
                self.counters[rate_key] = {
                    "minute": {"count": 0, "reset": time.time() + 60},
                    "hour": {"count": 0, "reset": time.time() + 3600},
                    "day": {"count": 0, "reset": time.time() + 86400}
                }
                
            counter = self.counters[rate_key]
            
            # Reset expired counters
            now = time.time()
            for period in counter:
                if now > counter[period]["reset"]:
                    counter[period]["count"] = 0
                    if period == "minute":
                        counter[period]["reset"] = now + 60
                    elif period == "hour":
                        counter[period]["reset"] = now + 3600
                    elif period == "day":
                        counter[period]["reset"] = now + 86400
                        
            # Check against limits
            limit_config = self.limits.get(endpoint, self.limits.get("default", {}))
            
            for period, limit in limit_config.items():
                if counter[period]["count"] >= limit:
                    return {
                        "allowed": False,
                        "limit": limit,
                        "remaining": 0,
                        "reset": counter[period]["reset"]
                    }
                    
            # Increment counters
            for period in counter:
                counter[period]["count"] += 1
                
            # Return limit info
            minute_limit = limit_config.get("minute", 100)
            return {
                "allowed": True,
                "limit": minute_limit,
                "remaining": minute_limit - counter["minute"]["count"],
                "reset": counter["minute"]["reset"]
            }
```

## Failover and Redundancy

The system implements failover mechanisms for provider unavailability:

```python
class FailoverManager:
    """Manage provider failover"""
    
    def __init__(self, provider_manager, config):
        self.provider_manager = provider_manager
        self.config = config
        self.health_status = {}
        self.retries = {}
        self.lock = asyncio.Lock()
        
    async def initialize(self):
        """Initialize health status for all providers"""
        providers = await self.provider_manager.get_providers()
        
        for provider in providers:
            self.health_status[provider["id"]] = {
                "status": "operational",
                "last_check": time.time(),
                "failures": 0,
                "suspended_until": None
            }
            
    async def provider_failed(self, provider_id, error):
        """Record a provider failure"""
        async with self.lock:
            if provider_id not in self.health_status:
                return
                
            status = self.health_status[provider_id]
            status["failures"] += 1
            status["last_check"] = time.time()
            
            # Check failure threshold
            if status["failures"] >= self.config.get_failover_threshold():
                status["status"] = "suspended"
                status["suspended_until"] = time.time() + self.config.get_failover_suspension_time()
                logger.warning(f"Provider {provider_id} suspended due to failures: {error}")
                
    async def provider_succeeded(self, provider_id):
        """Record a provider success"""
        async with self.lock:
            if provider_id not in self.health_status:
                return
                
            status = self.health_status[provider_id]
            status["failures"] = 0
            status["last_check"] = time.time()
            status["status"] = "operational"
            status["suspended_until"] = None
            
    async def is_provider_available(self, provider_id):
        """Check if a provider is available"""
        async with self.lock:
            if provider_id not in self.health_status:
                return False
                
            status = self.health_status[provider_id]
            
            # Check if suspended
            if status["status"] == "suspended":
                # Check if suspension period is over
                if status["suspended_until"] is not None and time.time() > status["suspended_until"]:
                    status["status"] = "operational"
                    status["failures"] = 0
                    return True
                    
                return False
                
            return True
            
    async def get_alternative_provider(self, model_id, original_provider_id):
        """Get alternative provider for model"""
        # Get compatible providers
        compatible_providers = await self._get_compatible_providers(model_id)
        
        # Remove original provider
        compatible_providers = [p for p in compatible_providers if p != original_provider_id]
        
        # Check if any compatible providers are available
        for provider_id in compatible_providers:
            if await self.is_provider_available(provider_id):
                return provider_id
                
        return None
        
    async def _get_compatible_providers(self, model_id):
        """Get compatible providers for model"""
        model_config = self.config.get_model_config(model_id)
        if not model_config:
            return []
            
        return model_config.get("compatible_providers", [])
            
    async def with_failover(self, model_id, operation_func):
        """Execute operation with failover support"""
        try:
            # Get primary provider
            provider = await self.provider_manager.get_provider_for_model(model_id)
            provider_id = provider.name
            
            # Check if provider is available
            if not await self.is_provider_available(provider_id):
                # Find alternative provider
                alt_provider_id = await self.get_alternative_provider(model_id, provider_id)
                if alt_provider_id is None:
                    # No alternatives available
                    raise ProviderNotAvailableError(f"Provider for model {model_id} is unavailable and no alternatives exist")
                    
                # Get alternative provider
                provider = await self.provider_manager.get_provider(alt_provider_id)
                provider_id = provider.name
                logger.info(f"Using alternative provider {provider_id} for model {model_id}")
                
            # Execute operation
            result = await operation_func(provider)
            
            # Record success
            await self.provider_succeeded(provider_id)
            
            return result
            
        except Exception as e:
            if provider_id:
                await self.provider_failed(provider_id, str(e))
                
            # Retry with alternative if possible
            if isinstance(e, ProviderError) and provider_id:
                try:
                    # Find alternative provider
                    alt_provider_id = await self.get_alternative_provider(model_id, provider_id)
                    if alt_provider_id is not None:
                        # Get alternative provider
                        alt_provider = await self.provider_manager.get_provider(alt_provider_id)
                        logger.info(f"Retrying with alternative provider {alt_provider_id} for model {model_id}")
                        
                        # Execute operation with alternative
                        return await operation_func(alt_provider)
                except Exception as retry_error:
                    logger.error(f"Failover retry failed: {retry_error}")
                    
            # Re-raise original exception
            raise
```

## Streaming Implementation

The streaming implementation handles real-time responses:

```python
class StreamHandler:
    """Handle streaming responses"""
    
    def __init__(self, websocket_manager, client_id, request_id):
        self.websocket_manager = websocket_manager
        self.client_id = client_id
        self.request_id = request_id
        self.cancelled = False
        self.lock = asyncio.Lock()
        
    async def handle_stream(self, provider, model, messages, parameters):
        """Handle streaming response from provider"""
        try:
            # Register for cancellation
            await self.websocket_manager.register_request_handler(
                self.request_id, 
                self
            )
            
            # Start streaming
            chunk_index = 0
            total_content = ""
            
            async for chunk in provider.stream_chat_completion(model, messages, parameters):
                # Check if cancelled
                if self.cancelled:
                    logger.info(f"Request {self.request_id} was cancelled")
                    break
                    
                # Send chunk to client
                await self.websocket_manager.send_message(
                    self.client_id,
                    "chat.completion.chunk",
                    self.request_id,
                    {
                        "chunk_id": f"chunk_{chunk_index}",
                        "content": chunk["content"],
                        "index": chunk_index
                    }
                )
                
                # Update state
                chunk_index += 1
                total_content += chunk["content"]
                
            # Send completion message
            if not self.cancelled:
                await self.websocket_manager.send_message(
                    self.client_id,
                    "chat.completion.done",
                    self.request_id,
                    {
                        "completion_id": f"comp_{uuid.uuid4().hex[:12]}",
                        "usage": {
                            "prompt_tokens": chunk.get("usage", {}).get("prompt_tokens", 0),
                            "completion_tokens": len(total_content) // 4 + 1,  # Rough estimate
                            "total_tokens": chunk.get("usage", {}).get("prompt_tokens", 0) + (len(total_content) // 4 + 1)
                        }
                    }
                )
                
        except Exception as e:
            logger.error(f"Streaming error: {e}")
            
            # Send error to client
            await self.websocket_manager.send_message(
                self.client_id,
                "error",
                self.request_id,
                {
                    "code": "streaming_error",
                    "message": str(e)
                }
            )
        finally:
            # Clean up
            try:
                if self.request_id in self.websocket_manager.request_handlers:
                    del self.websocket_manager.request_handlers[self.request_id]
            except:
                pass
                
    async def cancel(self):
        """Cancel streaming"""
        async with self.lock:
            self.cancelled = True
```

## Single Port Architecture

LLMAdapter follows the Tekton Single Port Architecture for consistent component communication. All endpoints are provided through a single port (8004 by default).

### URL Path Structure

```
http://localhost:8004/
  ├── api/                     # HTTP API endpoints
  │   ├── providers            # Provider info
  │   ├── models               # Model info
  │   ├── completions          # Completion endpoints
  │   └── chat/completions     # Chat completion endpoints
  ├── ws/                      # WebSocket endpoint
  └── health                   # Health check endpoint
```

### Implementation

```python
# Server setup
from fastapi import FastAPI
import uvicorn

app = FastAPI(title="LLM Adapter API", version="1.0.0")

# Basic routes
@app.get("/health")
async def health_check():
    return {"status": "ok"}

# API router
from fastapi import APIRouter
api_router = APIRouter(prefix="/api")

# Mount API router
app.include_router(api_router)

# Add WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    # WebSocket implementation...
    pass

# Run server
if __name__ == "__main__":
    uvicorn.run(
        "llm_adapter.server:app",
        host="0.0.0.0",
        port=8004,
        reload=False
    )
```

## Performance Considerations

LLMAdapter is designed for high performance:

1. **Asynchronous Design**: All operations use async/await for non-blocking I/O
2. **Connection Pooling**: HTTP clients use connection pooling for efficiency
3. **Response Caching**: Common queries are cached to reduce API calls
4. **Batch Processing**: Supports batched requests for embedding generation
5. **Resource Limits**: Configurable limits prevent resource exhaustion
6. **Streaming**: Efficient streaming reduces time-to-first-token

## Security Considerations

The system implements several security measures:

1. **API Key Authentication**: All requests require valid API keys
2. **Permission System**: Granular permissions for different operations
3. **Rate Limiting**: Prevents abuse through configurable rate limits
4. **Input Validation**: All inputs are validated before processing
5. **Provider Credentials Security**: Provider API keys are securely stored
6. **Error Handling**: Secure error handling prevents information leakage
7. **CORS Configuration**: Configurable CORS settings for web integration

## Deployment Considerations

When deploying LLMAdapter, consider these recommendations:

1. **Environment Variables**: Store sensitive configuration in environment variables
2. **Scaling**: Deploy multiple instances behind a load balancer for horizontal scaling
3. **Monitoring**: Implement metrics collection for performance monitoring
4. **Logging**: Configure comprehensive logging for troubleshooting
5. **Backup**: Regularly backup configuration and API keys
6. **Resource Allocation**: Allocate sufficient memory for caching and connection pooling
7. **Network Security**: Use TLS for all connections and consider network-level access controls

## Conclusion

This technical documentation provides a comprehensive overview of the LLMAdapter's architecture, implementation details, and design considerations. Developers working with LLMAdapter should reference this document for a deep understanding of the system's internal operation.

For integration guidance, please refer to the [Integration Guide](./INTEGRATION.md) document, which focuses on how to integrate with LLMAdapter rather than its internal implementation.
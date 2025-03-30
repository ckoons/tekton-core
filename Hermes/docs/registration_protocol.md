# Unified Registration Protocol

The Unified Registration Protocol (URP) is a standardized way for Tekton components to register with the ecosystem, discover other components, and communicate with each other.

## Overview

The URP provides the following benefits:

- **Single Registration Point**: Components register once with Hermes
- **Propagation**: Registration information is propagated to all relevant systems
- **Security**: Token-based authentication ensures only authorized components can register
- **Health Monitoring**: Regular heartbeats ensure component health is tracked
- **Capability Discovery**: Components can discover others by their capabilities

## Component Registration Flow

1. Component initializes and connects to Hermes
2. Component sends registration request with its metadata
3. Hermes validates the request and registers the component
4. Hermes provides a security token for future operations
5. Component begins sending regular heartbeats to maintain registration
6. When shutting down, component unregisters from Hermes

## Integration Guide

### Basic Integration

The simplest way to integrate with the URP is to use the `HermesClient` class:

```python
import asyncio
from hermes.api.client import HermesClient

async def main():
    # Create a client
    client = HermesClient(
        component_id="my_component",
        component_name="My Component",
        component_type="custom",
        component_version="1.0.0",
        capabilities=["custom.capability1", "custom.capability2"]
    )
    
    # Register with Hermes
    await client.register()
    
    # Use Hermes services...
    
    # Unregister when done
    await client.unregister()
    await client.close()

if __name__ == "__main__":
    asyncio.run(main())
```

### Using the Registration Helper

For even simpler integration, use the `registration_helper` module:

```python
import asyncio
from hermes.utils.registration_helper import register_component

async def main():
    # Register your component
    registration = await register_component(
        component_id="my_component",
        component_name="My Component",
        component_type="custom",
        component_version="1.0.0",
        capabilities=["custom.capability1", "custom.capability2"]
    )
    
    if registration:
        # Use registration for messaging
        registration.publish_message(
            topic="my.topic",
            message={"data": "Hello World"}
        )
        
        # Unregister when done
        await registration.unregister()
        await registration.close()

if __name__ == "__main__":
    asyncio.run(main())
```

### Integration in an Existing Application

To integrate URP in an existing application:

```python
import asyncio
import signal
import sys
from hermes.utils.registration_helper import ComponentRegistration

# Create component registration
registration = None

async def setup():
    global registration
    
    # Initialize registration
    registration = ComponentRegistration(
        component_id="my_component",
        component_name="My Component",
        component_type="custom",
        component_version="1.0.0",
        capabilities=["custom.capability1", "custom.capability2"]
    )
    
    # Register with Hermes
    success = await registration.register()
    
    if not success:
        print("Failed to register with Hermes")
        return False
    
    return True

async def shutdown():
    if registration:
        await registration.unregister()
        await registration.close()

async def main():
    # Set up signal handlers
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda: asyncio.create_task(shutdown()))
    
    # Set up component
    if not await setup():
        return
    
    # Run your application...
    try:
        while True:
            await asyncio.sleep(1)
    finally:
        await shutdown()

if __name__ == "__main__":
    asyncio.run(main())
```

## Component Requirements

To integrate with the URP, components must:

1. Have a unique component ID
2. Define their capabilities
3. Send regular heartbeats
4. Properly unregister when shutting down

## Security Considerations

- Protect the security token provided by Hermes
- Store the token in memory, not on disk
- Use secure connections when communicating with Hermes
- Validate tokens before trusting component identities
# Standardized Client Interface Protocol for Tekton Components

This document defines the standardized client interface protocol for Tekton components, enabling consistent cross-component communication.

## Overview

The Client Interface Protocol establishes a uniform way for components to:

1. Discover other components in the Tekton ecosystem
2. Invoke capabilities of other components
3. Handle errors consistently
4. Manage authentication and authorization
5. Implement graceful degradation when services are unavailable

## Core Concepts

### Component Discovery

Components discover each other through the Hermes service registry:

- Discovery by component ID
- Discovery by component type
- Discovery by capabilities
- Filtering by status (healthy, etc.)

### Capability Invocation

Components invoke each other's capabilities through a consistent interface:

- Synchronous and asynchronous invocation
- Parameter validation
- Result handling
- Error handling

### Authentication and Authorization

Components handle authentication and authorization consistently:

- Token-based authentication
- Capability-level authorization
- Request signing
- Security context propagation

### Error Handling

Components handle errors in a standardized way:

- Error categorization
- Error codes
- Error messages
- Retry policies

### Graceful Degradation

Components implement graceful degradation when services are unavailable:

- Fallback mechanisms
- Circuit breaking
- Request queuing
- Partial responses

## Client Interface Structure

### Base Client

```python
class ComponentClient:
    """Base client for Tekton components."""
    
    def __init__(self, component_id: str, hermes_url: Optional[str] = None):
        """
        Initialize the component client.
        
        Args:
            component_id: ID of the component to connect to
            hermes_url: URL of the Hermes API
        """
        pass
    
    async def invoke_capability(self, capability: str, parameters: Dict[str, Any]) -> Any:
        """
        Invoke a capability on the component.
        
        Args:
            capability: Name of the capability to invoke
            parameters: Parameters for the capability
            
        Returns:
            Result of the capability invocation
        """
        pass
    
    async def close(self):
        """Close the client and release resources."""
        pass
```

### Capability-Specific Methods

Component clients should expose capability-specific methods for ease of use:

```python
class ExampleComponentClient(ComponentClient):
    """Client for the Example component."""
    
    async def get_data(self, id: str) -> Dict[str, Any]:
        """
        Get data from the component.
        
        Args:
            id: ID of the data to get
            
        Returns:
            Retrieved data
        """
        return await self.invoke_capability("get_data", {"id": id})
    
    async def update_data(self, id: str, data: Dict[str, Any]) -> bool:
        """
        Update data in the component.
        
        Args:
            id: ID of the data to update
            data: New data
            
        Returns:
            True if update was successful
        """
        return await self.invoke_capability("update_data", {"id": id, "data": data})
```

### Error Handling

Clients should handle errors consistently:

```python
class ComponentError(Exception):
    """Base error for component client operations."""
    pass

class ComponentNotFoundError(ComponentError):
    """Error raised when a component is not found."""
    pass

class CapabilityNotFoundError(ComponentError):
    """Error raised when a capability is not found."""
    pass

class CapabilityInvocationError(ComponentError):
    """Error raised when a capability invocation fails."""
    pass

class ComponentUnavailableError(ComponentError):
    """Error raised when a component is unavailable."""
    pass
```

## Implementation Details

### Component Discovery

```python
async def discover_component(component_id: str, hermes_url: Optional[str] = None) -> Dict[str, Any]:
    """
    Discover a component in the Tekton ecosystem.
    
    Args:
        component_id: ID of the component to discover
        hermes_url: URL of the Hermes API
        
    Returns:
        Component information
        
    Raises:
        ComponentNotFoundError: If the component is not found
    """
    pass

async def discover_components_by_type(component_type: str, hermes_url: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Discover components of a specific type in the Tekton ecosystem.
    
    Args:
        component_type: Type of components to discover
        hermes_url: URL of the Hermes API
        
    Returns:
        List of component information
    """
    pass

async def discover_components_by_capability(capability: str, hermes_url: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Discover components that have a specific capability in the Tekton ecosystem.
    
    Args:
        capability: Capability that components must have
        hermes_url: URL of the Hermes API
        
    Returns:
        List of component information
    """
    pass
```

### Capability Invocation

```python
async def invoke_capability(
    component_id: str,
    capability: str,
    parameters: Dict[str, Any],
    hermes_url: Optional[str] = None
) -> Any:
    """
    Invoke a capability on a component.
    
    Args:
        component_id: ID of the component to invoke the capability on
        capability: Name of the capability to invoke
        parameters: Parameters for the capability
        hermes_url: URL of the Hermes API
        
    Returns:
        Result of the capability invocation
        
    Raises:
        ComponentNotFoundError: If the component is not found
        CapabilityNotFoundError: If the capability is not found
        CapabilityInvocationError: If the capability invocation fails
        ComponentUnavailableError: If the component is unavailable
    """
    pass
```

### Client Factory

```python
async def create_client(
    component_id: str,
    client_type: Optional[Type[ComponentClient]] = None,
    hermes_url: Optional[str] = None
) -> ComponentClient:
    """
    Create a client for a component.
    
    Args:
        component_id: ID of the component to create a client for
        client_type: Type of client to create (defaults to ComponentClient)
        hermes_url: URL of the Hermes API
        
    Returns:
        Client for the component
        
    Raises:
        ComponentNotFoundError: If the component is not found
        TypeError: If client_type is not a subclass of ComponentClient
    """
    pass
```

## Authentication and Authorization

```python
class SecurityContext:
    """Security context for capability invocation."""
    
    def __init__(
        self,
        token: Optional[str] = None,
        client_id: Optional[str] = None,
        roles: Optional[List[str]] = None
    ):
        """
        Initialize the security context.
        
        Args:
            token: Authentication token
            client_id: Client ID
            roles: Roles
        """
        pass
```

## Retry Policies

```python
class RetryPolicy:
    """Policy for retrying capability invocations."""
    
    def __init__(
        self,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        retry_multiplier: float = 2.0,
        retry_max_delay: float = 30.0,
        retry_on: Optional[List[Type[Exception]]] = None
    ):
        """
        Initialize the retry policy.
        
        Args:
            max_retries: Maximum number of retries
            retry_delay: Initial delay between retries in seconds
            retry_multiplier: Multiplier for delay after each retry
            retry_max_delay: Maximum delay between retries in seconds
            retry_on: Types of exceptions to retry on (defaults to ComponentUnavailableError)
        """
        pass
```

## Best Practices

1. **Client Setup**: Always use the client factory for creating clients
2. **Error Handling**: Handle component errors appropriately
3. **Resource Management**: Close clients when done with them
4. **Capability Invocation**: Use capability-specific methods when available
5. **Retry Policies**: Configure retry policies based on component SLAs
6. **Graceful Degradation**: Implement fallback mechanisms for critical operations
7. **Security**: Use appropriate security contexts for capability invocation

## Example Usage

```python
# Create a client for the Example component
client = await create_client("example.component", ExampleComponentClient)

try:
    # Invoke a capability-specific method
    data = await client.get_data("123")
    
    # Process the data
    # ...
    
except ComponentNotFoundError:
    # Handle component not found
    print("Component not found")
    
except CapabilityNotFoundError:
    # Handle capability not found
    print("Capability not found")
    
except CapabilityInvocationError as e:
    # Handle capability invocation error
    print(f"Error invoking capability: {e}")
    
except ComponentUnavailableError:
    # Handle component unavailable
    print("Component unavailable")
    
finally:
    # Close the client
    await client.close()
```

## Security Considerations

1. **Authentication**: Use token-based authentication for cross-component communication
2. **Authorization**: Use capability-level authorization to control access
3. **Request Signing**: Sign requests to prevent tampering
4. **Security Context Propagation**: Propagate security contexts across component boundaries
5. **Secure Transport**: Use HTTPS for cross-component communication
6. **Input Validation**: Validate inputs on both client and server sides
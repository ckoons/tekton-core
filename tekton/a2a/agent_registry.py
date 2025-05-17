"""
Agent Registry - Registry for A2A agents and their capabilities.

This module provides a registry for A2A agents, allowing them to
advertise their capabilities and be discovered by other agents.
"""

import time
import uuid
import logging
import asyncio
from typing import Dict, List, Any, Optional, Set, Callable, Union

logger = logging.getLogger(__name__)

class AgentCard:
    """
    Agent card containing agent information and capabilities.
    
    This class represents the standardized format for agent information
    in the A2A protocol, including capabilities and metadata.
    """
    
    def __init__(
        self,
        agent_id: str,
        name: str,
        version: str,
        description: Optional[str] = None,
        capabilities: Optional[Dict[str, Any]] = None,
        limitations: Optional[Dict[str, Any]] = None,
        availability: Optional[Dict[str, Any]] = None,
        endpoint: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize an agent card.
        
        Args:
            agent_id: Unique identifier for the agent
            name: Human-readable name
            version: Agent version
            description: Description of the agent's purpose
            capabilities: Dictionary of agent capabilities
            limitations: Dictionary of agent limitations
            availability: Agent availability information
            endpoint: Agent endpoint for direct communication
            metadata: Additional metadata
        """
        self.agent_id = agent_id
        self.name = name
        self.version = version
        self.description = description or f"{name} agent"
        self.capabilities = capabilities or {}
        self.limitations = limitations or {}
        self.availability = availability or {
            "status": "available",
            "capacity": 1.0,
            "response_time": "medium"
        }
        self.endpoint = endpoint
        self.metadata = metadata or {}
        self.registered_at = time.time()
        self.last_seen = time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the agent card to a dictionary.
        
        Returns:
            Dictionary representation of the agent card
        """
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "capabilities": self.capabilities,
            "limitations": self.limitations,
            "availability": self.availability,
            "endpoint": self.endpoint,
            "metadata": self.metadata,
            "registered_at": self.registered_at,
            "last_seen": self.last_seen
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentCard":
        """
        Create an agent card from a dictionary.
        
        Args:
            data: Dictionary representation of an agent card
            
        Returns:
            AgentCard instance
        """
        agent = cls(
            agent_id=data.get("agent_id", ""),
            name=data.get("name", ""),
            version=data.get("version", "1.0.0"),
            description=data.get("description"),
            capabilities=data.get("capabilities"),
            limitations=data.get("limitations"),
            availability=data.get("availability"),
            endpoint=data.get("endpoint"),
            metadata=data.get("metadata")
        )
        
        # Set timestamps if provided
        if "registered_at" in data:
            agent.registered_at = data["registered_at"]
        if "last_seen" in data:
            agent.last_seen = data["last_seen"]
            
        return agent
    
    def has_capability(self, capability: str) -> bool:
        """
        Check if the agent has a specific capability.
        
        Args:
            capability: Capability to check for
            
        Returns:
            True if agent has the capability
        """
        if not self.capabilities:
            return False
            
        # Handle flat capability list
        if "communication" in self.capabilities:
            # Check structured capabilities
            for category, capabilities in self.capabilities.items():
                if isinstance(capabilities, list) and capability in capabilities:
                    return True
                elif isinstance(capabilities, dict):
                    for domain, domain_capabilities in capabilities.items():
                        if isinstance(domain_capabilities, list) and capability in domain_capabilities:
                            return True
        else:
            # Handle flat capability list (for backward compatibility)
            return capability in self.capabilities
            
        return False
    
    def update_last_seen(self):
        """Update the last seen timestamp."""
        self.last_seen = time.time()
        
        # Update availability status if it was offline
        if self.availability.get("status") == "offline":
            self.availability["status"] = "available"


class AgentRegistry:
    """
    Registry for A2A agents and their capabilities.
    
    This class provides methods for registering agents, discovering
    agents, and maintaining agent health status.
    """
    
    def __init__(self, check_interval: int = 60):
        """
        Initialize the agent registry.
        
        Args:
            check_interval: Interval in seconds for checking agent health
        """
        self.check_interval = check_interval
        self.agents: Dict[str, AgentCard] = {}
        self._health_check_task: Optional[asyncio.Task] = None
        self._running = False
        self._callbacks: Dict[str, List[Callable[[str, Dict[str, Any]], None]]] = {
            "registered": [],
            "unregistered": [],
            "updated": []
        }
        
        logger.info("Agent registry initialized")
    
    async def start(self):
        """Start the health check monitoring."""
        if self._running:
            return
            
        self._running = True
        self._health_check_task = asyncio.create_task(self._health_check_loop())
        logger.info("Agent health check monitoring started")
    
    async def stop(self):
        """Stop the health check monitoring."""
        self._running = False
        if self._health_check_task:
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass
        logger.info("Agent health check monitoring stopped")
    
    async def register(self, agent_card: Union[AgentCard, Dict[str, Any]]) -> str:
        """
        Register an agent with the registry.
        
        Args:
            agent_card: Agent information
            
        Returns:
            Agent ID
        """
        # Convert dictionary to AgentCard if needed
        if isinstance(agent_card, dict):
            card = AgentCard.from_dict(agent_card)
        else:
            card = agent_card
            
        # Generate ID if not provided
        if not card.agent_id:
            card.agent_id = f"agent-{uuid.uuid4()}"
            
        # Store agent information
        self.agents[card.agent_id] = card
        logger.info(f"Registered agent: {card.name} ({card.agent_id})")
        
        # Trigger registered callbacks
        for callback in self._callbacks["registered"]:
            try:
                callback(card.agent_id, card.to_dict())
            except Exception as e:
                logger.error(f"Error in registration callback: {e}")
        
        return card.agent_id
    
    async def unregister(self, agent_id: str) -> bool:
        """
        Unregister an agent from the registry.
        
        Args:
            agent_id: Agent ID to unregister
            
        Returns:
            True if unregistration successful
        """
        if agent_id in self.agents:
            agent = self.agents[agent_id]
            del self.agents[agent_id]
            logger.info(f"Unregistered agent: {agent.name} ({agent_id})")
            
            # Trigger unregistered callbacks
            for callback in self._callbacks["unregistered"]:
                try:
                    callback(agent_id, agent.to_dict())
                except Exception as e:
                    logger.error(f"Error in unregistration callback: {e}")
                    
            return True
            
        logger.warning(f"Agent not found in registry: {agent_id}")
        return False
    
    async def get_agent(self, agent_id: str) -> Optional[AgentCard]:
        """
        Get an agent by ID.
        
        Args:
            agent_id: Agent ID to retrieve
            
        Returns:
            AgentCard or None if not found
        """
        return self.agents.get(agent_id)
    
    async def find_by_capability(self, capability: str) -> List[AgentCard]:
        """
        Find agents with a specific capability.
        
        Args:
            capability: Capability to search for
            
        Returns:
            List of agents with the requested capability
        """
        matching_agents = []
        
        for agent_id, agent in self.agents.items():
            if agent.has_capability(capability):
                matching_agents.append(agent)
                
        return matching_agents
    
    async def find_by_type(self, agent_type: str) -> List[AgentCard]:
        """
        Find agents of a specific type.
        
        Args:
            agent_type: Agent type to search for
            
        Returns:
            List of agents of the requested type
        """
        matching_agents = []
        
        for agent_id, agent in self.agents.items():
            if agent.metadata.get("type") == agent_type:
                matching_agents.append(agent)
                
        return matching_agents
    
    async def update_status(self, agent_id: str, status: Dict[str, Any]) -> bool:
        """
        Update an agent's status.
        
        Args:
            agent_id: Agent ID to update
            status: New status information
            
        Returns:
            True if update successful
        """
        if agent_id not in self.agents:
            logger.warning(f"Agent not found in registry: {agent_id}")
            return False
            
        agent = self.agents[agent_id]
        
        # Update last seen timestamp
        agent.update_last_seen()
        
        # Update availability if provided
        if "availability" in status:
            agent.availability = status["availability"]
            
        # Trigger updated callbacks
        for callback in self._callbacks["updated"]:
            try:
                callback(agent_id, agent.to_dict())
            except Exception as e:
                logger.error(f"Error in update callback: {e}")
                
        return True
    
    async def get_all_agents(self) -> Dict[str, AgentCard]:
        """
        Get all registered agents.
        
        Returns:
            Dictionary of all agents
        """
        return self.agents.copy()
    
    async def _health_check_loop(self):
        """Main loop for health check monitoring."""
        while self._running:
            current_time = time.time()
            
            # Check each agent's last seen time
            for agent_id, agent in list(self.agents.items()):
                # Consider an agent offline if not seen in 3 check intervals
                if current_time - agent.last_seen > self.check_interval * 3:
                    # Mark as offline but don't remove yet
                    agent.availability["status"] = "offline"
                    logger.warning(f"Agent {agent.name} ({agent_id}) marked as offline")
                    
                    # Trigger updated callbacks
                    for callback in self._callbacks["updated"]:
                        try:
                            callback(agent_id, agent.to_dict())
                        except Exception as e:
                            logger.error(f"Error in health check callback: {e}")
            
            # Sleep until next check interval
            await asyncio.sleep(self.check_interval)
    
    def on_registered(self, callback: Callable[[str, Dict[str, Any]], None]):
        """
        Register a callback for agent registration events.
        
        Args:
            callback: Function to call when an agent is registered
        """
        self._callbacks["registered"].append(callback)
    
    def on_unregistered(self, callback: Callable[[str, Dict[str, Any]], None]):
        """
        Register a callback for agent unregistration events.
        
        Args:
            callback: Function to call when an agent is unregistered
        """
        self._callbacks["unregistered"].append(callback)
    
    def on_updated(self, callback: Callable[[str, Dict[str, Any]], None]):
        """
        Register a callback for agent status update events.
        
        Args:
            callback: Function to call when an agent's status is updated
        """
        self._callbacks["updated"].append(callback)


# Global registry instance for convenience functions
_global_registry: Optional[AgentRegistry] = None

async def get_registry() -> AgentRegistry:
    """
    Get the global agent registry, creating it if needed.
    
    Returns:
        Global AgentRegistry instance
    """
    global _global_registry
    if _global_registry is None:
        _global_registry = AgentRegistry()
        await _global_registry.start()
    return _global_registry

async def register_agent(agent_card: Union[AgentCard, Dict[str, Any]]) -> str:
    """
    Register an agent with the global registry.
    
    Args:
        agent_card: Agent information
        
    Returns:
        Agent ID
    """
    registry = await get_registry()
    return await registry.register(agent_card)

async def unregister_agent(agent_id: str) -> bool:
    """
    Unregister an agent from the global registry.
    
    Args:
        agent_id: Agent ID to unregister
        
    Returns:
        True if unregistration successful
    """
    registry = await get_registry()
    return await registry.unregister(agent_id)

async def find_agents_by_capability(capability: str) -> List[AgentCard]:
    """
    Find agents with a specific capability using the global registry.
    
    Args:
        capability: Capability to search for
        
    Returns:
        List of agents with the requested capability
    """
    registry = await get_registry()
    return await registry.find_by_capability(capability)
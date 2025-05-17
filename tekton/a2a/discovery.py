"""
Discovery Service - Service for discovering A2A agents.

This module provides a service for discovering A2A agents based on
their capabilities, types, and other criteria.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Union, Set

from tekton.a2a.agent_registry import (
    AgentRegistry, 
    AgentCard, 
    get_registry,
    find_agents_by_capability
)

logger = logging.getLogger(__name__)

class DiscoveryService:
    """
    Service for discovering A2A agents.
    
    This class provides methods for finding agents based on various
    criteria, including capabilities, types, and metadata.
    """
    
    def __init__(self, agent_registry: Optional[AgentRegistry] = None):
        """
        Initialize the discovery service.
        
        Args:
            agent_registry: Agent registry to use (uses global registry if None)
        """
        self.agent_registry = agent_registry
        logger.info("Discovery service initialized")
    
    async def _get_registry(self) -> AgentRegistry:
        """
        Get the agent registry, initializing if needed.
        
        Returns:
            Agent registry
        """
        if self.agent_registry:
            return self.agent_registry
        return await get_registry()
    
    async def find_by_id(self, agent_id: str) -> Optional[AgentCard]:
        """
        Find an agent by ID.
        
        Args:
            agent_id: Agent ID to find
            
        Returns:
            AgentCard or None if not found
        """
        registry = await self._get_registry()
        return await registry.get_agent(agent_id)
    
    async def find_by_capability(self, capability: str) -> List[AgentCard]:
        """
        Find agents with a specific capability.
        
        Args:
            capability: Capability to search for
            
        Returns:
            List of matching agents
        """
        registry = await self._get_registry()
        return await registry.find_by_capability(capability)
    
    async def find_by_type(self, agent_type: str) -> List[AgentCard]:
        """
        Find agents of a specific type.
        
        Args:
            agent_type: Agent type to search for
            
        Returns:
            List of matching agents
        """
        registry = await self._get_registry()
        return await registry.find_by_type(agent_type)
    
    async def find_by_metadata(
        self,
        metadata_key: str,
        metadata_value: Any
    ) -> List[AgentCard]:
        """
        Find agents with specific metadata.
        
        Args:
            metadata_key: Metadata key to search for
            metadata_value: Value to match
            
        Returns:
            List of matching agents
        """
        registry = await self._get_registry()
        agents = await registry.get_all_agents()
        
        matching_agents = []
        for agent in agents.values():
            if metadata_key in agent.metadata and agent.metadata[metadata_key] == metadata_value:
                matching_agents.append(agent)
                
        return matching_agents
    
    async def find_by_capabilities(
        self,
        capabilities: List[str],
        require_all: bool = False
    ) -> List[AgentCard]:
        """
        Find agents with specific capabilities.
        
        Args:
            capabilities: List of capabilities to search for
            require_all: If True, agents must have all capabilities
            
        Returns:
            List of matching agents
        """
        registry = await self._get_registry()
        agents = await registry.get_all_agents()
        
        matching_agents = []
        for agent in agents.values():
            if require_all:
                # Agent must have all capabilities
                if all(agent.has_capability(cap) for cap in capabilities):
                    matching_agents.append(agent)
            else:
                # Agent must have at least one capability
                if any(agent.has_capability(cap) for cap in capabilities):
                    matching_agents.append(agent)
                    
        return matching_agents
    
    async def find_best_agent(
        self,
        capabilities: List[str],
        preferred_types: Optional[List[str]] = None,
        exclude_agents: Optional[List[str]] = None
    ) -> Optional[AgentCard]:
        """
        Find the best agent for a set of capabilities.
        
        This method attempts to find the optimal agent by considering
        required capabilities, preferred types, and agent availability.
        
        Args:
            capabilities: Required capabilities
            preferred_types: Preferred agent types
            exclude_agents: Agent IDs to exclude
            
        Returns:
            Best matching agent or None if none found
        """
        registry = await self._get_registry()
        agents = await registry.get_all_agents()
        
        # Filter out excluded agents
        if exclude_agents:
            agents = {
                agent_id: agent for agent_id, agent in agents.items()
                if agent_id not in exclude_agents
            }
        
        # Filter agents with required capabilities
        capable_agents = []
        for agent in agents.values():
            if all(agent.has_capability(cap) for cap in capabilities):
                capable_agents.append(agent)
                
        if not capable_agents:
            logger.warning(f"No agents found with all required capabilities: {capabilities}")
            return None
            
        # Sort by preferred type, if specified
        if preferred_types:
            scored_agents = []
            for agent in capable_agents:
                agent_type = agent.metadata.get("type")
                if agent_type and agent_type in preferred_types:
                    # Higher score for more preferred types
                    type_score = preferred_types.index(agent_type)
                    scored_agents.append((type_score, agent))
                else:
                    # Lowest score for non-preferred types
                    scored_agents.append((len(preferred_types), agent))
                    
            # Sort by score (ascending)
            scored_agents.sort()
            
            # Return the highest-scoring agent
            if scored_agents:
                return scored_agents[0][1]
        
        # If no preferred types or no match, return first capable agent
        if capable_agents:
            return capable_agents[0]
            
        return None
    
    async def discover_all(self) -> List[AgentCard]:
        """
        Discover all available agents.
        
        Returns:
            List of all available agents
        """
        registry = await self._get_registry()
        agents = await registry.get_all_agents()
        return list(agents.values())
    
    async def get_nearby_agents(
        self,
        agent_id: str,
        max_distance: int = 2
    ) -> Dict[str, int]:
        """
        Find agents that are "nearby" in the capability graph.
        
        This method finds agents that share capabilities with the specified
        agent, assigning a distance based on capability overlap.
        
        Args:
            agent_id: Agent ID to find nearby agents for
            max_distance: Maximum distance to consider
            
        Returns:
            Dictionary mapping agent IDs to their distance from the specified agent
        """
        registry = await self._get_registry()
        source_agent = await registry.get_agent(agent_id)
        
        if not source_agent:
            logger.warning(f"Agent not found: {agent_id}")
            return {}
            
        all_agents = await registry.get_all_agents()
        
        # Extract source agent capabilities
        source_capabilities = set()
        for category, capabilities in source_agent.capabilities.items():
            if isinstance(capabilities, list):
                source_capabilities.update(capabilities)
            elif isinstance(capabilities, dict):
                for domain, domain_capabilities in capabilities.items():
                    if isinstance(domain_capabilities, list):
                        source_capabilities.update(domain_capabilities)
        
        # Calculate distances
        distances = {}
        for other_id, other_agent in all_agents.items():
            if other_id == agent_id:
                continue
                
            # Extract other agent capabilities
            other_capabilities = set()
            for category, capabilities in other_agent.capabilities.items():
                if isinstance(capabilities, list):
                    other_capabilities.update(capabilities)
                elif isinstance(capabilities, dict):
                    for domain, domain_capabilities in capabilities.items():
                        if isinstance(domain_capabilities, list):
                            other_capabilities.update(domain_capabilities)
            
            # Calculate capability overlap
            common_capabilities = source_capabilities.intersection(other_capabilities)
            
            if common_capabilities:
                # Calculate distance based on overlap ratio
                overlap_ratio = len(common_capabilities) / len(source_capabilities)
                distance = int((1 - overlap_ratio) * max_distance) + 1
                
                if distance <= max_distance:
                    distances[other_id] = distance
        
        return distances


# Global discovery service instance for convenience functions
_global_discovery_service: Optional[DiscoveryService] = None

def get_discovery_service() -> DiscoveryService:
    """
    Get the global discovery service, creating it if needed.
    
    Returns:
        Global DiscoveryService instance
    """
    global _global_discovery_service
    if _global_discovery_service is None:
        _global_discovery_service = DiscoveryService()
    return _global_discovery_service

async def find_agent_by_id(agent_id: str) -> Optional[AgentCard]:
    """
    Find an agent by ID using the global discovery service.
    
    Args:
        agent_id: Agent ID to find
        
    Returns:
        AgentCard or None if not found
    """
    discovery = get_discovery_service()
    return await discovery.find_by_id(agent_id)

async def find_agents_by_type(agent_type: str) -> List[AgentCard]:
    """
    Find agents of a specific type using the global discovery service.
    
    Args:
        agent_type: Agent type to search for
        
    Returns:
        List of matching agents
    """
    discovery = get_discovery_service()
    return await discovery.find_by_type(agent_type)

async def discover_agents(capabilities: List[str]) -> List[AgentCard]:
    """
    Discover agents with specific capabilities using the global discovery service.
    
    Args:
        capabilities: List of capabilities to search for
        
    Returns:
        List of matching agents
    """
    discovery = get_discovery_service()
    return await discovery.find_by_capabilities(capabilities)
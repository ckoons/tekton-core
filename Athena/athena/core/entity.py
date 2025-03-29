"""
Entity - Knowledge graph entity representation.

This module provides the Entity class for representing nodes in the knowledge graph.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
import uuid


@dataclass
class Entity:
    """
    Representation of a node in the knowledge graph.
    
    Attributes:
        entity_type: Type of entity (e.g., Person, Organization)
        properties: Dictionary of entity properties
        id: Unique identifier for the entity
    """
    
    entity_type: str
    properties: Dict[str, Any] = field(default_factory=dict)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    def add_property(self, key: str, value: Any) -> None:
        """
        Add or update a property.
        
        Args:
            key: Property name
            value: Property value
        """
        self.properties[key] = value
    
    def get_property(self, key: str, default: Any = None) -> Any:
        """
        Get a property value.
        
        Args:
            key: Property name
            default: Default value if property doesn't exist
            
        Returns:
            Property value or default
        """
        return self.properties.get(key, default)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary representation.
        
        Returns:
            Dictionary representation of the entity
        """
        return {
            "id": self.id,
            "type": self.entity_type,
            "properties": self.properties
        }
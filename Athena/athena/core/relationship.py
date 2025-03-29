"""
Relationship - Knowledge graph relationship representation.

This module provides the Relationship class for representing edges in the knowledge graph.
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass, field
import uuid


@dataclass
class Relationship:
    """
    Representation of an edge in the knowledge graph.
    
    Attributes:
        source_id: Source entity ID
        target_id: Target entity ID
        relationship_type: Type of relationship
        properties: Dictionary of relationship properties
        id: Unique identifier for the relationship
    """
    
    source_id: str
    target_id: str
    relationship_type: str
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
            Dictionary representation of the relationship
        """
        return {
            "id": self.id,
            "source": self.source_id,
            "target": self.target_id,
            "type": self.relationship_type,
            "properties": self.properties
        }
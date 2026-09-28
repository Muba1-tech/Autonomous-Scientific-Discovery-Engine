"""Typed edge relationships for the Scientific Knowledge Graph.
Supports relationships: SUPPORTS, CONTRADICTS, CITES, USES_METHOD, TESTS, DERIVED_FROM, DEPENDS_ON, VALIDATES, REFUTES, RELATED_TO.
"""
from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from datetime import datetime
from enum import Enum


class EdgeType(str, Enum):
    SUPPORTS = "SUPPORTS"
    CONTRADICTS = "CONTRADICTS"
    CITES = "CITES"
    USES_METHOD = "USES_METHOD"
    TESTS = "TESTS"
    DERIVED_FROM = "DERIVED_FROM"
    DEPENDS_ON = "DEPENDS_ON"
    VALIDATES = "VALIDATES"
    REFUTES = "REFUTES"
    RELATED_TO = "RELATED_TO"
    CAUSES = "CAUSES"


@dataclass
class Edge:
    """Base class for all graph edges with alias support for source/target/relation."""
    source_id: str = ""
    target_id: str = ""
    type: Any = "RELATED_TO"
    source: str = ""
    target: str = ""
    relation: str = ""
    properties: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        if self.source and not self.source_id:
            self.source_id = self.source
        elif self.source_id and not self.source:
            self.source = self.source_id

        if self.target and not self.target_id:
            self.target_id = self.target
        elif self.target_id and not self.target:
            self.target = self.target_id

        if self.relation and not self.type:
            self.type = self.relation
        elif self.type and not self.relation:
            self.relation = self.type.value if hasattr(self.type, "value") else str(self.type)

        if isinstance(self.type, str):
            t_upper = self.type.upper()
            try:
                self.type = EdgeType[t_upper]
            except KeyError:
                self.type = EdgeType.RELATED_TO

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_id": self.source_id,
            "target_id": self.target_id,
            "source": self.source,
            "target": self.target,
            "relation": self.relation,
            "type": self.type.value if hasattr(self.type, "value") else str(self.type),
            "properties": self.properties,
            "created_at": self.created_at.isoformat()
        }

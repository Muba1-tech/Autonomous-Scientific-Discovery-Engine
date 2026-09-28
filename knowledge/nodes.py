"""Typed node structures for the Scientific Knowledge Graph.
Supports typed entities: Paper, Author, Claim, Hypothesis, Experiment, Dataset, Method, Concept, Result, ResearchGap.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum


class NodeType(str, Enum):
    PAPER = "PAPER"
    AUTHOR = "AUTHOR"
    CLAIM = "CLAIM"
    HYPOTHESIS = "HYPOTHESIS"
    EXPERIMENT = "EXPERIMENT"
    DATASET = "DATASET"
    METHOD = "METHOD"
    CONCEPT = "CONCEPT"
    RESULT = "RESULT"
    RESEARCH_GAP = "RESEARCH_GAP"
    INSTITUTION = "INSTITUTION"
    CITATION = "CITATION"


@dataclass
class Node:
    """Base class for all graph nodes."""
    id: str
    type: Any = "CONCEPT"
    name: str = ""
    properties: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        if isinstance(self.type, str):
            # Normalize to uppercase NodeType if possible
            t_upper = self.type.upper()
            try:
                self.type = NodeType[t_upper]
            except KeyError:
                self.type = NodeType.CONCEPT
        if self.name and "name" not in self.properties:
            self.properties["name"] = self.name

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type.value if hasattr(self.type, "value") else str(self.type),
            "name": self.name or self.properties.get("name", ""),
            "properties": self.properties,
            "created_at": self.created_at.isoformat()
        }


@dataclass
class PaperNode(Node):
    title: str = ""
    abstract: str = ""
    year: int = 0
    doi: Optional[str] = None
    
    def __post_init__(self):
        self.type = NodeType.PAPER
        self.properties.update({"title": self.title, "abstract": self.abstract, "year": self.year, "doi": self.doi})


@dataclass
class AuthorNode(Node):
    name: str = ""
    affiliation: Optional[str] = None

    def __post_init__(self):
        self.type = NodeType.AUTHOR
        self.properties.update({"name": self.name, "affiliation": self.affiliation})


@dataclass
class ClaimNode(Node):
    description: str = ""
    confidence: float = 0.0

    def __post_init__(self):
        self.type = NodeType.CLAIM
        self.properties.update({"description": self.description, "confidence": self.confidence})


@dataclass
class HypothesisNode(Node):
    description: str = ""
    status: str = "proposed"

    def __post_init__(self):
        self.type = NodeType.HYPOTHESIS
        self.properties.update({"description": self.description, "status": self.status})


@dataclass
class ExperimentNode(Node):
    name: str = ""
    description: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        self.type = NodeType.EXPERIMENT
        self.properties.update({"name": self.name, "description": self.description, "parameters": self.parameters})


@dataclass
class DatasetNode(Node):
    name: str = ""
    url: Optional[str] = None
    size: Optional[str] = None

    def __post_init__(self):
        self.type = NodeType.DATASET
        self.properties.update({"name": self.name, "url": self.url, "size": self.size})


@dataclass
class MethodNode(Node):
    name: str = ""
    description: str = ""
    
    def __post_init__(self):
        self.type = NodeType.METHOD
        self.properties.update({"name": self.name, "description": self.description})


@dataclass
class ConceptNode(Node):
    name: str = ""
    definition: str = ""

    def __post_init__(self):
        self.type = NodeType.CONCEPT
        self.properties.update({"name": self.name, "definition": self.definition})


@dataclass
class ResultNode(Node):
    description: str = ""
    metrics: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        self.type = NodeType.RESULT
        self.properties.update({"description": self.description, "metrics": self.metrics})


@dataclass
class ResearchGapNode(Node):
    description: str = ""
    domain: str = ""

    def __post_init__(self):
        self.type = NodeType.RESEARCH_GAP
        self.properties.update({"description": self.description, "domain": self.domain})


@dataclass
class InstitutionNode(Node):
    name: str = ""
    location: Optional[str] = None

    def __post_init__(self):
        self.type = NodeType.INSTITUTION
        self.properties.update({"name": self.name, "location": self.location})


@dataclass
class CitationNode(Node):
    context: str = ""

    def __post_init__(self):
        self.type = NodeType.CITATION
        self.properties.update({"context": self.context})

"""
AION X 2.0 — Persistent Scientific Research Tree
Hierarchical persistent graph structure representing the complete discovery evolution:
Research Question
  ├── Hypotheses (Gen 0)
  │     ├── Hypothesis Variants (Mutations / Crossover Gen 1..N)
  │     │     ├── Experiments (EXP-01, EXP-02...)
  │     │     │     ├── Evidence & Statistical Results
  │     │     │     └── Contradictions & Replications
  │     │     └── Falsification & Kill Chain Verdicts
  │     └── Death Certificates (for Refuted Branches)
  └── Final Synthesis & Next Best Research Actions
"""

import uuid
import json
import logging
from typing import List, Dict, Any, Optional

from database.models import ResearchTreeNode
from database.db_manager import DBManager

logger = logging.getLogger(__name__)


class ResearchTree:
    """Manages and visualizes the hierarchical persistent research tree."""

    def __init__(self, mission_id: str, db_manager: Optional[DBManager] = None):
        self.mission_id = mission_id
        self.db = db_manager
        self._nodes: Dict[str, ResearchTreeNode] = {}

    def add_node(
        self,
        node_id: str,
        parent_id: Optional[str],
        node_type: str,
        title: str,
        status: str = "ACTIVE",
        confidence: float = 0.8,
        data: Optional[Dict[str, Any]] = None
    ) -> ResearchTreeNode:
        """Adds a node to the persistent research tree."""
        node = ResearchTreeNode(
            node_id=node_id,
            parent_id=parent_id,
            node_type=node_type,  # QUESTION, HYPOTHESIS, VARIANT, EXPERIMENT, EVIDENCE, CONTRADICTION, OUTCOME, DEATH_CERTIFICATE
            title=title,
            status=status,
            confidence=confidence,
            mission_id=self.mission_id,
            data=data or {},
            children_ids=[]
        )
        self._nodes[node_id] = node

        if parent_id and parent_id in self._nodes:
            if node_id not in self._nodes[parent_id].children_ids:
                self._nodes[parent_id].children_ids.append(node_id)

        if self.db:
            try:
                self.db.insert_research_tree_node(
                    node_id=node.node_id,
                    parent_id=node.parent_id,
                    node_type=node.node_type,
                    title=node.title,
                    status=node.status,
                    confidence=node.confidence,
                    mission_id=self.mission_id,
                    data=node.data,
                    children_ids=node.children_ids
                )
            except Exception as e:
                logger.warning(f"Error persisting research tree node: {e}")

        return node

    def get_tree_hierarchy(self) -> Dict[str, Any]:
        """Returns the entire tree as a nested JSON structure for Streamlit / D3 rendering."""
        # Find root nodes
        roots = [n for n in self._nodes.values() if not n.parent_id]
        if not roots and self._nodes:
            roots = [list(self._nodes.values())[0]]

        def build_subtree(node: ResearchTreeNode) -> Dict[str, Any]:
            children = [self._nodes[cid] for cid in node.children_ids if cid in self._nodes]
            return {
                "id": node.node_id,
                "name": node.title,
                "type": node.node_type,
                "status": node.status,
                "confidence": node.confidence,
                "data": node.data,
                "children": [build_subtree(c) for c in children]
            }

        return {
            "mission_id": self.mission_id,
            "total_nodes": len(self._nodes),
            "tree": [build_subtree(r) for r in roots]
        }

    def load_from_db(self):
        """Loads all nodes for this mission from SQLite."""
        if not self.db:
            return
        records = self.db.get_research_tree_nodes(mission_id=self.mission_id)
        for r in records:
            node = ResearchTreeNode(
                node_id=r["node_id"],
                parent_id=r.get("parent_id"),
                node_type=r.get("node_type", "HYPOTHESIS"),
                title=r.get("title", ""),
                status=r.get("status", "ACTIVE"),
                confidence=r.get("confidence", 0.8),
                mission_id=self.mission_id,
                data=r.get("data", {}),
                children_ids=r.get("children_ids", [])
            )
            self._nodes[node.node_id] = node

"""Scientific Knowledge Graph Module for AION X.
Provides graph abstraction operating on SQLite (via DBManager) with NetworkX in-memory representation.
Supports typed entities (Paper, Claim, Hypothesis, Experiment, Gap) and queries answering 'Why does AION believe this?'.
"""
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import networkx as nx

from knowledge.nodes import Node, NodeType
from knowledge.edges import Edge, EdgeType

# Optional Neo4j import
try:
    from neo4j import GraphDatabase
    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False

logger = logging.getLogger(__name__)


class ScientificKnowledgeGraph:
    """Knowledge graph interface over SQLite and NetworkX in-memory representation."""

    def __init__(self, db_manager: Optional[Any] = None, neo4j_uri: Optional[str] = None, neo4j_user: Optional[str] = None, neo4j_password: Optional[str] = None):
        self.db = db_manager
        self.nx_graph = nx.DiGraph()
        self._nodes_dict: Dict[str, Node] = {}
        self._edges_dict: Dict[str, List[Edge]] = {}

        if self.db:
            self._init_sqlite_tables()
            self._load_into_memory()

        self.neo4j_driver = None
        if NEO4J_AVAILABLE and neo4j_uri and neo4j_user and neo4j_password:
            try:
                self.neo4j_driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
            except Exception as e:
                logger.warning(f"Failed to initialize Neo4j driver: {e}")

    def _init_sqlite_tables(self):
        """Initialize the necessary SQLite tables for the graph."""
        if not self.db:
            return
        node_query = '''
            CREATE TABLE IF NOT EXISTS graph_nodes (
                id TEXT PRIMARY KEY,
                type TEXT NOT NULL,
                properties TEXT,
                created_at TEXT
            )
        '''
        edge_query = '''
            CREATE TABLE IF NOT EXISTS graph_edges (
                source_id TEXT,
                target_id TEXT,
                type TEXT NOT NULL,
                properties TEXT,
                created_at TEXT,
                PRIMARY KEY (source_id, target_id, type)
            )
        '''
        try:
            if hasattr(self.db, "execute_update"):
                self.db.execute_update(node_query)
                self.db.execute_update(edge_query)
            elif hasattr(self.db, "execute"):
                self.db.execute(node_query)
                self.db.execute(edge_query)
        except Exception as e:
            logger.debug(f"Knowledge graph table init notice: {e}")

    def _load_into_memory(self):
        """Load the full graph from SQLite into NetworkX."""
        if not self.db:
            return
        try:
            nodes_data = None
            if hasattr(self.db, "execute_query"):
                nodes_data = self.db.execute_query("SELECT id, type, properties, created_at FROM graph_nodes")
            if nodes_data:
                for row in nodes_data:
                    props = json.loads(row['properties']) if row['properties'] else {}
                    self.add_node(Node(id=row['id'], type=row['type'], properties=props))

            edges_data = None
            if hasattr(self.db, "execute_query"):
                edges_data = self.db.execute_query("SELECT source_id, target_id, type, properties, created_at FROM graph_edges")
            if edges_data:
                for row in edges_data:
                    props = json.loads(row['properties']) if row['properties'] else {}
                    self.add_edge(Edge(source=row['source_id'], target=row['target_id'], relation=row['type'], properties=props))
        except Exception as e:
            logger.debug(f"Graph in-memory load notice: {e}")

    def add_node(self, node: Node):
        """Adds a node to the knowledge graph."""
        self._nodes_dict[node.id] = node
        self.nx_graph.add_node(node.id, type=getattr(node.type, "value", str(node.type)), properties=node.properties)

        if self.db:
            try:
                query = "INSERT OR REPLACE INTO graph_nodes (id, type, properties, created_at) VALUES (?, ?, ?, ?)"
                props_json = json.dumps(node.properties)
                type_val = node.type.value if hasattr(node.type, "value") else str(node.type)
                if hasattr(self.db, "execute_update"):
                    self.db.execute_update(query, (node.id, type_val, props_json, node.created_at.isoformat()))
            except Exception as e:
                logger.debug(f"Error adding node to DB: {e}")

    def get_node(self, node_id: str) -> Optional[Node]:
        """Retrieve node by ID."""
        return self._nodes_dict.get(node_id)

    def add_edge(self, edge: Edge):
        """Adds an edge to the knowledge graph."""
        src = edge.source_id or edge.source
        tgt = edge.target_id or edge.target
        rel = edge.relation or (edge.type.value if hasattr(edge.type, "value") else str(edge.type))

        if src not in self._edges_dict:
            self._edges_dict[src] = []
        self._edges_dict[src].append(edge)

        self.nx_graph.add_edge(src, tgt, relation=rel, type=rel, properties=edge.properties)

        if self.db:
            try:
                query = "INSERT OR REPLACE INTO graph_edges (source_id, target_id, type, properties, created_at) VALUES (?, ?, ?, ?, ?)"
                props_json = json.dumps(edge.properties)
                if hasattr(self.db, "execute_update"):
                    self.db.execute_update(query, (src, tgt, rel, props_json, edge.created_at.isoformat()))
            except Exception as e:
                logger.debug(f"Error adding edge to DB: {e}")

    def get_edges(self, source_id: str) -> List[Edge]:
        """Get all outgoing edges from source_id."""
        return self._edges_dict.get(source_id, [])

    def query(self, source_id: Optional[str] = None, target_id: Optional[str] = None, relation: Optional[str] = None) -> List[Edge]:
        """Query edges matching source, target, and/or relation filters."""
        matching = []
        for src, edges in self._edges_dict.items():
            if source_id and src != source_id:
                continue
            for edge in edges:
                tgt = edge.target_id or edge.target
                rel = edge.relation or (edge.type.value if hasattr(edge.type, "value") else str(edge.type))
                if target_id and tgt != target_id:
                    continue
                if relation and rel.lower() != relation.lower():
                    continue
                matching.append(edge)
        return matching

    def get_egocentric_neighborhood(self, center_id: str, depth: int = 1) -> Dict[str, Any]:
        """Traverse graph outwards from center_id up to depth hops."""
        visited_nodes = set()
        queue = [(center_id, 0)]
        collected_edges = []

        while queue:
            curr, curr_depth = queue.pop(0)
            if curr in visited_nodes:
                continue
            visited_nodes.add(curr)

            if curr_depth < depth:
                for edge in self._edges_dict.get(curr, []):
                    tgt = edge.target_id or edge.target
                    collected_edges.append(edge)
                    if tgt not in visited_nodes:
                        queue.append((tgt, curr_depth + 1))

        return {
            "center": center_id,
            "depth": depth,
            "nodes": list(visited_nodes),
            "edges": [e.to_dict() for e in collected_edges]
        }

    def query_provenance(self, claim_id: str) -> List[Dict[str, Any]]:
        """Why does AION believe this? Returns all predecessor nodes and relationships."""
        provenance = []
        if claim_id in self.nx_graph:
            for pred in self.nx_graph.predecessors(claim_id):
                edge_data = self.nx_graph.get_edge_data(pred, claim_id)
                node_data = self.nx_graph.nodes[pred]
                provenance.append({
                    "source_id": pred,
                    "source_type": node_data.get("type"),
                    "source_properties": node_data.get("properties"),
                    "relationship": edge_data.get("relation") or edge_data.get("type")
                })
        return provenance

    def to_pyvis_data(self) -> Dict[str, Any]:
        """Format nodes and edges for high-tech UI graph visualization."""
        nodes = []
        edges = []
        for n_id, n_obj in self._nodes_dict.items():
            nodes.append({
                "id": n_id,
                "label": n_obj.name or n_id,
                "group": n_obj.type.value if hasattr(n_obj.type, "value") else str(n_obj.type)
            })
        for src, edge_list in self._edges_dict.items():
            for e in edge_list:
                tgt = e.target_id or e.target
                rel = e.relation or (e.type.value if hasattr(e.type, "value") else str(e.type))
                edges.append({
                    "from": src,
                    "to": tgt,
                    "label": rel
                })
        return {"nodes": nodes, "edges": edges}

    def close(self):
        if self.neo4j_driver:
            self.neo4j_driver.close()

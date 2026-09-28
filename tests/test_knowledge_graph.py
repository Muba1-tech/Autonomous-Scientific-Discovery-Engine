import pytest
from knowledge.graph import ScientificKnowledgeGraph, Node, Edge

@pytest.fixture
def kg():
    return ScientificKnowledgeGraph()

def test_node_addition(kg):
    node = Node(id="n1", type="concept", name="Quantum Entanglement")
    kg.add_node(node)
    assert kg.get_node("n1") == node

def test_edge_addition(kg):
    kg.add_node(Node(id="n1"))
    kg.add_node(Node(id="n2"))
    edge = Edge(source="n1", target="n2", relation="causes")
    kg.add_edge(edge)
    assert edge in kg.get_edges("n1")

def test_query_operations(kg):
    kg.add_node(Node(id="n1", type="concept", name="A"))
    kg.add_node(Node(id="n2", type="concept", name="B"))
    kg.add_edge(Edge(source="n1", target="n2", relation="causes"))
    
    results = kg.query(source_id="n1", relation="causes")
    assert len(results) == 1
    assert results[0].target == "n2"

def test_egocentric_neighborhood_traversal(kg):
    kg.add_node(Node(id="center"))
    kg.add_node(Node(id="n1"))
    kg.add_node(Node(id="n2"))
    kg.add_edge(Edge(source="center", target="n1", relation="relates_to"))
    kg.add_edge(Edge(source="n1", target="n2", relation="relates_to"))
    
    neighborhood = kg.get_egocentric_neighborhood("center", depth=2)
    assert "n1" in neighborhood["nodes"]
    assert "n2" in neighborhood["nodes"]
    assert len(neighborhood["nodes"]) == 3

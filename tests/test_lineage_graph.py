"""Tests for AION X 2.0 Evidence Lineage Graph & Claim Dependency Graph."""
import pytest
from database.db_manager import DBManager
from knowledge.lineage_graph import EvidenceLineageGraph


def test_lineage_graph_basic():
    db = DBManager()
    graph = EvidenceLineageGraph(db_manager=db)

    graph.add_entity("SRC-01", "Source", "Quantum Coherence Paper")
    graph.add_entity("CLM-01", "Claim", "Exciton lifetime exceeds 15ps")
    graph.add_entity("HYP-01", "Hypothesis", "Vibronic resonance preserves coherence")
    graph.add_entity("CONC-01", "Conclusion", "Photosynthetic coherence mechanism validated")

    graph.add_relation("SRC-01", "Source", "CLM-01", "Claim", "SOURCE_PROVIDES_CLAIM")
    graph.add_relation("CLM-01", "Claim", "HYP-01", "Hypothesis", "CLAIM_SUPPORTS_HYPOTHESIS")
    graph.add_relation("HYP-01", "Hypothesis", "CONC-01", "Conclusion", "HYPOTHESIS_YIELDS_CONCLUSION")

    chain = graph.get_provenance_chain("CONC-01")
    assert len(chain) >= 2

    fragility = graph.calculate_conclusion_fragility("CONC-01")
    assert "fragility_score" in fragility
    assert "distinct_sources" in fragility

    graph_json = graph.export_graph_json()
    assert "nodes" in graph_json
    assert "edges" in graph_json

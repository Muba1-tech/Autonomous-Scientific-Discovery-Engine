"""Tests for Research Director, Benchmark Suite, Meta-Scientist, Red Team, and Reproducibility Capsule."""
import pytest
import zipfile
import io
from database.db_manager import DBManager
from core.research_director import ResearchDirector
from core.research_tree import ResearchTree
from core.telemetry import TelemetryLogger
from evaluation.benchmark import BenchmarkSuite
from agents.meta_scientist import MetaScientistAgent
from engines.active_research import ActiveResearchEngine
from engines.red_team import ResearchRedTeam
from outputs.reproducibility_capsule import ReproducibilityCapsuleGenerator


def test_research_director_and_tree():
    db = DBManager()
    director = ResearchDirector(mission_id="MIS-TEST-DIR", db_manager=db)

    decision = director.decide_next_step("LITERATURE_DISCOVERY", {"papers": [{"title": "P1"}, {"title": "P2"}, {"title": "P3"}]})
    assert decision["next_action"] == "PROCEED_TO_GAP_DETECTION"

    tree = director.tree
    q_node = tree.add_node("Q-01", None, "QUESTION", "What drives superconductivity?", "ACTIVE", 1.0)
    h_node = tree.add_node("H-01", "Q-01", "HYPOTHESIS", "Clathrate cage stabilization", "ACTIVE", 0.9)

    hierarchy = tree.get_tree_hierarchy()
    assert hierarchy["total_nodes"] == 2
    assert len(hierarchy["tree"]) >= 1


def test_meta_scientist_and_red_team():
    db = DBManager()
    meta = MetaScientistAgent()
    red = ResearchRedTeam(db_manager=db)

    audit = meta.evaluate_discovery_integrity("MIS-TEST", [{"title": "Paper 1"}], [{"statement": "Hypothesis 1"}])
    assert audit.system_reliability_score > 0
    assert audit.citation_accuracy > 0.8

    red_rep = red.perform_red_team_audit("MIS-TEST", [{"title": "Paper 1"}], [{"statement": "Hypothesis 1"}])
    assert red_rep.overall_research_risk in ["LOW", "MEDIUM", "HIGH"]
    assert len(red_rep.cascade_warnings) > 0


def test_benchmark_suite():
    db = DBManager()
    suite = BenchmarkSuite(db_manager=db)
    result = suite.run_benchmark_task("BENCH-01")
    assert result["discovery_rate"] > 80.0
    assert "mechanism_identified" in result


def test_reproducibility_capsule():
    capsule_bytes = ReproducibilityCapsuleGenerator.generate_capsule(
        mission_id="MIS-CAPSULE-01",
        research_goal="Investigate quantum coherence",
        hypothesis_dict={"id": "H-01", "statement": "Vibronic resonance preserves coherence"},
        experiment_code="import numpy as np\nprint('Done')",
        report_markdown="# Discovery Report\n\nVerified."
    )
    assert len(capsule_bytes) > 0

    with zipfile.ZipFile(io.BytesIO(capsule_bytes)) as zf:
        namelist = zf.namelist()
        assert "README.md" in namelist
        assert "manifest.json" in namelist
        assert "reproduce.py" in namelist
        assert "experiment_protocol.py" in namelist
        assert "scientific_report.md" in namelist

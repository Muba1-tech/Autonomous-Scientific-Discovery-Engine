"""Tests for AION X 2.0 Hypothesis Kill Chain and Adversarial Tournament."""
import pytest
from database.db_manager import DBManager
from engines.kill_chain import HypothesisKillChain
from debate.tournament import AdversarialTournament


def test_kill_chain_execution():
    db = DBManager()
    kc = HypothesisKillChain(db_manager=db)
    hyp = {"id": "H-TEST-01", "statement": "Topological screening reduces thermal dissipation in superconductors.", "score": 85.0}
    papers = [{"title": "Superconducting boundary states", "abstract": "Demonstrates topological protection at 150K"}]

    report = kc.execute_kill_chain(hyp, papers)
    assert report.final_survival_score > 0
    assert "disclaimer" in report.to_dict()


def test_kill_chain_death_certificate():
    db = DBManager()
    kc = HypothesisKillChain(db_manager=db)

    dc = kc.generate_death_certificate(
        hypothesis_id="H-FAIL-01",
        statement="Perpetual motion via zero dissipation",
        cause_of_failure="Violated second law of thermodynamics (entropy non-decrease constraint).",
        fatal_evidence="Non-equilibrium simulation diverged.",
        falsification_stage="Thermodynamics Audit"
    )
    assert dc.certificate_id.startswith("DC-")
    assert dc.hypothesis_id == "H-FAIL-01"
    assert "violated" in dc.cause_of_failure.lower()


def test_adversarial_tournament():
    db = DBManager()
    tourney = AdversarialTournament(db_manager=db)
    hyp = {"id": "H-TEST-02", "statement": "Interfacial topological coupling suppresses dissipation."}
    papers = [{"title": "Quantum Transport", "abstract": "Evidence of topological interfacial states."}]

    result = tourney.run_tournament(hyp, papers)
    assert "arguments" in result
    assert "verdict" in result
    assert len(result["arguments"]) == 8
    assert result["verdict"]["overall_defense_score"] > 0

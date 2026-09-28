"""Tests for Scientific Failure Memory, Evidence Firewall, and Claim Calibration."""
import pytest
from database.db_manager import DBManager
from engines.failure_vault import ScientificFailureVault
from engines.evidence_firewall import EvidenceFirewall
from evaluation.calibration import CalibrationEngine
from evaluation.scoring import DiscoveryScoreEngine


def test_failure_vault_recording_and_warnings():
    db = DBManager()
    vault = ScientificFailureVault(db_manager=db)

    fail_id = vault.record_failure(
        hypothesis_id="H-OLD-01",
        experiment_id="EXP-OLD-01",
        failure_type="NUMERICAL_INSTABILITY",
        observations="Divergence at t=0.05",
        diagnosis="Boundary step size was too large",
        learned_constraint="Enforce CFL condition dt < dx/c"
    )
    assert fail_id.startswith("FAIL-")

    warning_result = vault.check_failure_patterns("Perpetual energy with zero dissipation")
    assert warning_result["has_failure_risk"] is True
    assert len(warning_result["warnings"]) > 0


def test_evidence_firewall_classification():
    db = DBManager()
    firewall = EvidenceFirewall(db_manager=db)
    stmts = [
        "We hypothesize that resonant coupling protects quantum coherence.",
        "Simulation shows that the system reaches equilibrium in 12ms.",
        "Empirical data indicates a 40% improvement in conductivity."
    ]
    papers = [{"title": "Quantum Resonance Paper", "abstract": "Resonant coupling protects quantum coherence effectively."}]

    claims = firewall.classify_and_verify(stmts, papers, mission_id="MIS-TEST-01")
    assert len(claims) == 3
    assert any(c.claim_type == "HYPOTHESIS" for c in claims)
    assert any(c.claim_type == "SIMULATION" for c in claims)


def test_claim_calibration():
    engine = CalibrationEngine(n_bins=5)
    preds = [0.90, 0.80, 0.70, 0.60, 0.50]
    trues = [1, 1, 1, 0, 0]

    result = engine.calculate_calibration(preds, trues)
    assert "brier_score" in result
    assert "expected_calibration_error" in result
    assert result["brier_score"] >= 0.0
    assert result["expected_calibration_error"] >= 0.0


def test_discovery_score_2():
    score_data = DiscoveryScoreEngine.calculate_discovery_score(
        novelty=90.0,
        evidence_quality=88.0,
        source_reliability=92.0,
        replication=85.0,
        agreement=80.0,
        methodological_robustness=86.0,
        falsifiability=88.0,
        reproducibility=90.0,
        causal_strength=84.0,
        information_gain=85.0,
        contradiction_risk=10.0
    )
    assert 0.0 <= score_data["discovery_score"] <= 100.0
    assert "weights" in score_data
    assert abs(sum(score_data["weights"].values()) - 1.0) < 1e-5

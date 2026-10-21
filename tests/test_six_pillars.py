"""
AION X 2.0 — Comprehensive Verification Suite for the 6 Advanced Pillars:
- Pillar 1: Domain Scientific Solvers (Bio Hill Kinetics, Materials Thermodynamics, Dynamical ODEs, ML Benchmark)
- Pillar 2: Dynamic Experiment Protocol Synthesis & Self-Correction
- Pillar 3: Hardened Sandboxing & Enhanced Introspection AST Guards
- Pillar 4: Real Counter-Claim Mining & Popperian Falsification 2.0
- Pillar 5: Real-Time Human-in-the-Loop Steering
- Pillar 6: Academic Two-Column LaTeX & Publication PDF Generation
"""

import pytest
import numpy as np

from simulation.domain_solvers import DomainScientificSolvers
from simulation.dynamic_synthesizer import DynamicExperimentSynthesizer
from simulation.process_sandbox import ASTSecurityAuditor, IsolatedProcessSandbox
from engines.kill_chain import HypothesisKillChain
from core.interactive_pipeline import InteractivePipeline, STEERING_EVENTS
from outputs.report_generator import generate_academic_latex, generate_academic_pdf_bytes


def test_pillar_1_biomedical_hill_kinetics():
    doses = np.logspace(-2, 2, 20)
    result = DomainScientificSolvers.solve_biomedical_hill_kinetics(doses, ec50=2.5, hill_coeff=1.8)
    assert "auc" in result
    assert "ic50_estimated" in result
    assert result["auc"] > 0.0
    assert len(result["response_curve"]) == 20


def test_pillar_1_materials_thermodynamics():
    temps = np.linspace(200, 800, 25)
    result = DomainScientificSolvers.solve_materials_thermodynamics(temps, delta_h=-50.0, delta_s=-0.1)
    assert "gibbs_free_energy" in result
    assert "t_critical_kelvin" in result
    assert result["t_critical_kelvin"] == 500.0


def test_pillar_1_nonlinear_dynamics_ode():
    result = DomainScientificSolvers.solve_nonlinear_dynamics_ode(t_span=(0.0, 5.0), n_points=50)
    assert result["converged"] is True
    assert len(result["displacement"]) == 50
    assert "lyapunov_proxy" in result


def test_pillar_1_ml_benchmark():
    result = DomainScientificSolvers.solve_ml_benchmark(n_samples=100, n_features=4)
    assert result["sample_size"] == 100
    assert "in_sample_r2" in result
    assert "cv_r2_mean" in result


def test_pillar_2_dynamic_synthesizer():
    synth = DynamicExperimentSynthesizer()
    bio_code = synth.synthesize_protocol_code("CAR-T allosteric binding suppresses receptor exhaustion", domain="Oncology")
    assert "run_experiment" in bio_code
    assert "EXPERIMENT_OUTPUT_START" in bio_code
    
    # Test error repair rule
    broken_code = "import json\ndef run():\n  pass\n"
    repaired = synth.repair_code_error(broken_code, "Missing JSON block")
    assert "EXPERIMENT_OUTPUT_START" in repaired


def test_pillar_3_hardened_ast_guards():
    auditor = ASTSecurityAuditor()
    # Test blocked dunder introspection
    exploit_code = "x = ().__class__.__bases__[0].__subclasses__()"
    audit_res = auditor.audit(exploit_code)
    assert audit_res.passed is False
    assert any("__subclasses__" in v or "__class__" in v for v in audit_res.violations)

    # Test safe code passes
    safe_code = "import numpy as np\nx = np.mean([1, 2, 3])"
    safe_res = auditor.audit(safe_code)
    assert safe_res.passed is True


def test_pillar_4_real_counter_claim_mining():
    kc = HypothesisKillChain()
    statement = "Peptide transporter accelerates cellular uptake of targeted kinase inhibitors."
    papers = [
        {"title": "Targeted kinase delivery via peptide motifs", "abstract": "Peptide transporter demonstrates accelerated uptake across human cell lines."},
        {"title": "Resistance mechanisms in targeted kinase inhibitors", "abstract": "However, peptide transporter fails to improve uptake in hypoxic solid tumor microenvironments, leading to underperforms baseline outcomes."}
    ]
    lit_score, contra_score, strongest_support, strongest_contradiction = kc._evaluate_literature_attacks(statement, papers)
    assert "Supported by" in strongest_support
    assert "fails to" in strongest_contradiction or "underperforms" in strongest_contradiction or "Reported in" in strongest_contradiction
    assert contra_score < 80.0  # Contradiction detected lowers score as expected in Popperian falsification


def test_pillar_5_interactive_steering():
    pipeline = InteractivePipeline()
    events_received = []
    pipeline.register_event_callback(lambda evt: events_received.append(evt))

    evt = pipeline._emit_steering_event("gaps_detected", {"gaps": ["Unexplored cryogenic state", "Boundary breakdown"]})
    assert len(events_received) == 1
    assert evt.event_type == "gaps_detected"
    assert "pursue_gap_1" in evt.available_actions

    # Submit user decision
    pipeline.submit_decision(evt.event_id, "pursue_gap_1", {"priority": "high"})
    decision = pipeline._wait_for_decision(evt, timeout=1.0)
    assert decision.chosen_action == "pursue_gap_1"


def test_pillar_6_academic_latex_and_pdf():
    latex_output = generate_academic_latex(
        domain="Quantum Materials",
        hypothesis_text="Coupling high-pressure phonon modes stabilizes electron pairing.",
        gaps=[{"description": "Cryogenic phase boundary instability"}],
        papers=[{"title": "High-Tc Hydride Phases", "authors": ["E. Vance"], "year": 2025}],
        scores={"priority_score": 91.0, "novelty_score": 94.0, "feasibility_score": 86.0}
    )
    assert r"\documentclass[10pt,twocolumn]{article}" in latex_output
    assert "Quantum Materials" in latex_output
    assert r"\begin{equation}" in latex_output

    pdf_bytes = generate_academic_pdf_bytes(
        report_md="# Formal Discovery Report\nHigh-pressure superconductivity evaluation.",
        domain="Quantum Materials",
        scores={"priority_score": 91.0, "novelty_score": 94.0, "feasibility_score": 86.0},
        hypotheses=["Phonon-mediated pairing is enhanced under non-equilibrium optical pumping."],
        gaps=[{"description": "Cryogenic phase boundary instability"}]
    )
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 200

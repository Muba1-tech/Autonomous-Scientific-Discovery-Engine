"""Tests for Autonomous Experiment Generator, Reproducibility Engine, and Counterfactual Lab."""
import pytest
from database.db_manager import DBManager
from experiments.generator import AutonomousExperimentGenerator
from experiments.reproducibility import ReproducibilityEngine
from engines.counterfactual_lab import CounterfactualLab


def test_autonomous_experiment_generator():
    generator = AutonomousExperimentGenerator()
    hyp = {"id": "H-EXP-01", "statement": "Resonant coupling increases reaction kinetics."}

    spec = generator.generate_experiment(hyp)
    assert len(spec.independent_variables) > 0
    assert len(spec.dependent_variables) > 0
    assert "numpy" in spec.python_code
    assert "feasibility_score" in spec.python_code


def test_reproducibility_engine():
    db = DBManager()
    engine = ReproducibilityEngine(db_manager=db)
    code = """
import numpy as np
seed = 42
np.random.seed(seed)
val = float(np.mean(np.random.normal(0.88, 0.02, 100)))
print(f'simulated_feasibility = {val}')
"""
    rep = engine.evaluate_reproducibility({"id": "H-REP-01"}, code, n_trials=5)
    assert rep["reproducibility_score"] >= 80.0
    assert len(rep["multi_run_scores"]) == 5
    assert len(rep["confidence_interval_95"]) == 2


def test_counterfactual_lab():
    db = DBManager()
    lab = CounterfactualLab(db_manager=db)
    hyp = {"id": "H-CF-01", "statement": "Vibronic resonance preserves exciton coherence."}

    report = lab.run_counterfactual_suite(hyp)
    assert report["experiments_run"] == 5
    assert report["overall_counterfactual_robustness_score"] > 0
    assert len(report["details"]) == 5

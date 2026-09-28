import pytest
from engines.falsification import FalsificationEngine
from engines.hypothesis_evolution import Hypothesis

@pytest.fixture
def engine():
    return FalsificationEngine()

def test_formulating_falsification_criteria(engine):
    h = Hypothesis(content="All swans are white.")
    criteria = engine.formulate_criteria(h)
    assert len(criteria) > 0
    assert "black swan" in criteria[0].lower() or "color" in criteria[0].lower()

def test_testing_hypotheses(engine):
    h = Hypothesis(content="Gravity pulls objects downwards.")
    result = engine.test_hypothesis(h)
    assert "passed" in result or "failed" in result
    assert h.falsification_results is not None

def test_survival_score_calculation(engine):
    h = Hypothesis(content="Test hypothesis")
    h.falsification_results = [True, True, False]
    score = engine.calculate_survival_score(h)
    assert score == pytest.approx(0.666, rel=1e-2)

import pytest
from evaluation.confidence import ScientificConfidenceSystem, ConfidenceMetrics

@pytest.fixture
def system():
    return ScientificConfidenceSystem()

def test_multi_dimensional_confidence(system):
    metrics = system.calculate_confidence(
        evidence_strength=0.8,
        methodology_rigor=0.9,
        reproducibility=0.7
    )
    assert isinstance(metrics, ConfidenceMetrics)
    assert metrics.overall_confidence > 0.0
    assert metrics.dimensions["evidence"] == 0.8
    assert metrics.dimensions["methodology"] == 0.9

def test_discovery_index_calculation(system):
    metrics = ConfidenceMetrics(
        overall_confidence=0.85,
        novelty_score=0.9,
        impact_factor=0.75
    )
    discovery_index = system.calculate_discovery_index(metrics)
    assert discovery_index > 0.0
    assert discovery_index <= 1.0
    # Expected weighted sum or similar logic
    assert discovery_index == pytest.approx(0.83, rel=1e-1)

def test_transparency_report(system):
    metrics = ConfidenceMetrics(overall_confidence=0.9)
    report = system.generate_transparency_report(metrics)
    assert "overall_confidence" in report
    assert "0.9" in report

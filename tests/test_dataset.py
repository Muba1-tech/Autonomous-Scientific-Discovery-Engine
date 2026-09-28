import pytest
import pandas as pd
from agents.dataset import DatasetScientist

@pytest.fixture
def dataset_path(tmp_path):
    df = pd.DataFrame({
        "A": [1, 2, 3, 4, 5],
        "B": [5, 4, 3, 2, 1],
        "C": [1, 1, 2, 2, 3]
    })
    path = tmp_path / "test_data.csv"
    df.to_csv(path, index=False)
    return str(path)

@pytest.fixture
def scientist():
    return DatasetScientist()

def test_dataset_profiling(scientist, dataset_path):
    profile = scientist.profile_dataset(dataset_path)
    assert "num_rows" in profile
    assert profile["num_rows"] == 5
    assert profile["num_columns"] == 3

def test_distribution_analysis(scientist, dataset_path):
    distributions = scientist.analyze_distributions(dataset_path)
    assert "A" in distributions
    assert "mean" in distributions["A"]
    assert distributions["A"]["mean"] == 3.0

def test_correlation_matrices(scientist, dataset_path):
    correlations = scientist.calculate_correlations(dataset_path)
    assert "A" in correlations
    assert correlations["A"]["B"] < 0.0  # Perfect negative correlation

def test_candidate_hypothesis_generation(scientist, dataset_path):
    hypotheses = scientist.generate_hypotheses(dataset_path)
    assert len(hypotheses) > 0
    assert any("correlation" in h.lower() for h in hypotheses)

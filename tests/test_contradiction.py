import pytest
from engines.contradiction import ContradictionHunter, Evidence

@pytest.fixture
def hunter():
    return ContradictionHunter()

def test_bidirectional_evidence_comparison(hunter):
    e1 = Evidence(content="A causes B")
    e2 = Evidence(content="A prevents B")
    result = hunter.compare_evidence(e1, e2)
    assert result.is_contradiction == True

def test_contradiction_strength_scoring(hunter):
    e1 = Evidence(content="The drug increases heart rate slightly.")
    e2 = Evidence(content="The drug decreases heart rate significantly.")
    contradiction = hunter.compare_evidence(e1, e2)
    
    assert contradiction.strength_score > 0.5
    assert contradiction.strength_score <= 1.0

def test_no_contradiction(hunter):
    e1 = Evidence(content="A causes B")
    e2 = Evidence(content="B causes C")
    result = hunter.compare_evidence(e1, e2)
    assert result.is_contradiction == False
    assert result.strength_score == 0.0

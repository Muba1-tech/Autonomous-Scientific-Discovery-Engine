import pytest
from debate.arena import ScientificDebateArena, Argument, Verdict

@pytest.fixture
def arena():
    return ScientificDebateArena()

def test_advocate_arguments(arena):
    topic = "String theory is a viable physical theory."
    advocate_arg = arena.generate_advocate_argument(topic)
    assert isinstance(advocate_arg, Argument)
    assert advocate_arg.stance == "pro"
    assert len(advocate_arg.points) > 0

def test_skeptic_arguments(arena):
    topic = "String theory is a viable physical theory."
    skeptic_arg = arena.generate_skeptic_argument(topic)
    assert isinstance(skeptic_arg, Argument)
    assert skeptic_arg.stance == "con"
    assert len(skeptic_arg.points) > 0

def test_verdict_resolution(arena):
    topic = "Climate change is accelerated by human activity."
    advocate_arg = Argument(stance="pro", points=["CO2 levels rising"])
    skeptic_arg = Argument(stance="con", points=["Natural cycles exist"])
    
    verdict = arena.resolve_debate(topic, advocate_arg, skeptic_arg)
    assert isinstance(verdict, Verdict)
    assert verdict.winner in ["pro", "con", "tie"]
    assert verdict.confidence_score >= 0.0
    assert verdict.confidence_score <= 1.0

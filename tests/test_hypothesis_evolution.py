import pytest
from engines.hypothesis_evolution import HypothesisEvolutionEngine, Hypothesis

@pytest.fixture
def engine():
    return HypothesisEvolutionEngine(population_size=10, mutation_rate=0.1)

def test_population_generation(engine):
    initial_prompt = "Generate hypotheses about quantum gravity."
    population = engine.generate_initial_population(initial_prompt)
    assert len(population) == 10
    assert all(isinstance(h, Hypothesis) for h in population)

def test_scoring(engine):
    h = Hypothesis(content="Test hypothesis")
    score = engine.score_hypothesis(h)
    assert 0.0 <= score <= 1.0
    assert h.score == score

def test_tournament_selection(engine):
    population = [Hypothesis(content=f"H{i}", score=i/10.0) for i in range(10)]
    parents = engine.tournament_selection(population, num_parents=2)
    assert len(parents) == 2
    assert parents[0].score >= 0.0

def test_mutation(engine):
    h = Hypothesis(content="Original hypothesis")
    mutated = engine.mutate(h)
    assert mutated.content != h.content
    assert mutated.generation == h.generation + 1

def test_crossover(engine):
    h1 = Hypothesis(content="Hypothesis 1")
    h2 = Hypothesis(content="Hypothesis 2")
    child = engine.crossover(h1, h2)
    assert child.generation == max(h1.generation, h2.generation) + 1
    assert len(child.parents) == 2

def test_generation_lineage(engine):
    h1 = Hypothesis(content="Hypothesis 1", id="h1")
    h2 = Hypothesis(content="Hypothesis 2", id="h2")
    child = engine.crossover(h1, h2)
    assert "h1" in child.parents
    assert "h2" in child.parents

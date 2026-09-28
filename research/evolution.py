import uuid
import json
import random
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Callable
import logging

try:
    from database.db_manager import DBManager
except ImportError:
    # Fallback/mock if not available during isolated test
    class DBManager:
        def execute(self, query, params=()): pass

try:
    from llm_engine.router import smart_route_prompt
except ImportError:
    # Fallback/mock
    def smart_route_prompt(prompt: str) -> str: return ""


logger = logging.getLogger(__name__)

@dataclass
class HypothesisScores:
    novelty: float = 0.0
    evidence: float = 0.0
    feasibility: float = 0.0
    impact: float = 0.0
    falsifiability: float = 0.0
    reproducibility: float = 0.0
    confidence: float = 0.0
    uncertainty: float = 1.0

    def composite_fitness(self) -> float:
        """
        Calculates composite fitness. 
        Note: A high evolutionary fitness score reflects algorithmic promise, 
        NOT positive physical proof.
        """
        return (
            self.novelty * 1.2 +
            self.evidence * 1.5 +
            self.feasibility * 1.0 +
            self.impact * 1.1 +
            self.falsifiability * 1.3 +
            self.reproducibility * 1.0 +
            self.confidence * 0.8 -
            self.uncertainty * 0.5
        )

@dataclass
class EvolvingHypothesis:
    content: str
    generation: int
    parent_ids: List[str] = field(default_factory=list)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    scores: HypothesisScores = field(default_factory=HypothesisScores)
    fitness: float = 0.0


class HypothesisEvolutionEngine:
    def __init__(self, db_manager: DBManager):
        self.db_manager = db_manager
        self._init_db()

    def _init_db(self):
        query = """
        CREATE TABLE IF NOT EXISTS evolving_hypotheses (
            id TEXT PRIMARY KEY,
            content TEXT,
            generation INTEGER,
            parent_ids TEXT,
            scores TEXT,
            fitness REAL
        )
        """
        self.db_manager.execute(query)

    def save_hypothesis(self, hyp: EvolvingHypothesis):
        query = """
        INSERT OR REPLACE INTO evolving_hypotheses (id, content, generation, parent_ids, scores, fitness)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        self.db_manager.execute(query, (
            hyp.id,
            hyp.content,
            hyp.generation,
            json.dumps(hyp.parent_ids),
            json.dumps(hyp.scores.__dict__),
            hyp.fitness
        ))

    def evaluate(self, hyp: EvolvingHypothesis) -> HypothesisScores:
        prompt = f"""
Evaluate the following scientific hypothesis and provide scores between 0.0 and 1.0 for:
novelty, evidence, feasibility, impact, falsifiability, reproducibility, confidence, uncertainty.

Hypothesis:
{hyp.content}

Return ONLY a JSON object with these keys and float values.
"""
        response = smart_route_prompt(prompt)
        try:
            # simple json extraction
            start = response.find("{")
            end = response.rfind("}")
            if start != -1 and end != -1:
                data = json.loads(response[start:end+1])
                scores = HypothesisScores(
                    novelty=float(data.get("novelty", 0.0)),
                    evidence=float(data.get("evidence", 0.0)),
                    feasibility=float(data.get("feasibility", 0.0)),
                    impact=float(data.get("impact", 0.0)),
                    falsifiability=float(data.get("falsifiability", 0.0)),
                    reproducibility=float(data.get("reproducibility", 0.0)),
                    confidence=float(data.get("confidence", 0.0)),
                    uncertainty=float(data.get("uncertainty", 1.0))
                )
                return scores
        except Exception as e:
            logger.error(f"Failed to evaluate hypothesis: {e}")
        
        return HypothesisScores()

    def generate_initial_population(self, seed_topic: str, population_size: int = 20) -> List[EvolvingHypothesis]:
        prompt = f"""
Generate {population_size} distinct, plausible scientific hypotheses regarding: {seed_topic}.
Return ONLY a JSON list of strings, each being a hypothesis.
"""
        response = smart_route_prompt(prompt)
        population = []
        try:
            start = response.find("[")
            end = response.rfind("]")
            if start != -1 and end != -1:
                hypotheses_texts = json.loads(response[start:end+1])
                for text in hypotheses_texts[:population_size]:
                    hyp = EvolvingHypothesis(content=text, generation=0)
                    population.append(hyp)
        except Exception as e:
            logger.error(f"Failed to generate initial population: {e}")
            
        # fallback if parsing fails
        if not population:
            for i in range(population_size):
                population.append(EvolvingHypothesis(content=f"Fallback hypothesis {i} for {seed_topic}", generation=0))
                
        return population

    def tournament_selection(self, population: List[EvolvingHypothesis], k: int = 3) -> EvolvingHypothesis:
        if not population:
            raise ValueError("Empty population")
        tournament = random.sample(population, min(k, len(population)))
        return max(tournament, key=lambda x: x.fitness)

    def mutate(self, hyp: EvolvingHypothesis) -> EvolvingHypothesis:
        prompt = f"""
Mutate the following scientific hypothesis by altering its mechanisms, parameters, assumptions, or incorporating cross-domain metaphors.
Maintain scientific plausibility.

Original Hypothesis:
{hyp.content}

Return ONLY the new hypothesis text.
"""
        new_content = smart_route_prompt(prompt).strip()
        # Clean up any surrounding quotes
        if new_content.startswith('"') and new_content.endswith('"'):
            new_content = new_content[1:-1]
            
        return EvolvingHypothesis(
            content=new_content,
            generation=hyp.generation + 1,
            parent_ids=[hyp.id]
        )

    def crossover(self, parent1: EvolvingHypothesis, parent2: EvolvingHypothesis) -> EvolvingHypothesis:
        prompt = f"""
Synthesize a hybrid child hypothesis that combines the most promising attributes of these two parent hypotheses.

Parent 1:
{parent1.content}

Parent 2:
{parent2.content}

Return ONLY the new hypothesis text.
"""
        new_content = smart_route_prompt(prompt).strip()
        if new_content.startswith('"') and new_content.endswith('"'):
            new_content = new_content[1:-1]
            
        return EvolvingHypothesis(
            content=new_content,
            generation=max(parent1.generation, parent2.generation) + 1,
            parent_ids=[parent1.id, parent2.id]
        )

    def evolve(self, 
               population: List[EvolvingHypothesis], 
               max_generations: int, 
               survivors_per_generation: int, 
               callback: Optional[Callable[[int, List[EvolvingHypothesis]], None]] = None) -> List[EvolvingHypothesis]:
        
        current_population = population
        
        for gen in range(1, max_generations + 1):
            # Evaluate fitness
            for hyp in current_population:
                if hyp.fitness == 0.0:  # Avoid re-evaluating if already evaluated
                    hyp.scores = self.evaluate(hyp)
                    hyp.fitness = hyp.scores.composite_fitness()
                    self.save_hypothesis(hyp)
            
            # Sort and select survivors
            current_population.sort(key=lambda x: x.fitness, reverse=True)
            survivors = current_population[:survivors_per_generation]
            
            if callback:
                callback(gen, survivors)
                
            if gen == max_generations:
                return survivors
                
            # Create new population
            next_generation = list(survivors) # Elitism
            
            # Fill the rest with offspring
            target_size = len(current_population)
            while len(next_generation) < target_size:
                if random.random() < 0.3 and len(survivors) >= 2:
                    # Crossover
                    p1 = self.tournament_selection(survivors)
                    p2 = self.tournament_selection(survivors)
                    child = self.crossover(p1, p2)
                else:
                    # Mutation
                    p = self.tournament_selection(survivors)
                    child = self.mutate(p)
                    
                next_generation.append(child)
                
            current_population = next_generation
            
        return current_population

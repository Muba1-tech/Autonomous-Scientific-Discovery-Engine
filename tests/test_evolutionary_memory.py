import unittest
import os
from database.db_manager import DBManager
from engines.evolutionary_memory import EvolutionaryMemoryEngine

class TestEvolutionaryMemory(unittest.TestCase):
    def setUp(self):
        self.db = DBManager(db_name=":memory:")
        self.memory = EvolutionaryMemoryEngine(self.db)

    def test_record_and_fetch_memory(self):
        self.memory.record_cycle(
            research_id="TEST-001",
            domain="Computer Science",
            hypothesis="Quantum superposition applied to DB query optimization.",
            evidence="Theoretical physics principles.",
            methodology="Simulation",
            experiment_result="Success R2=0.92",
            outcome="SUCCESS",
            novelty_score=90.0,
            feasibility_score=85.0,
            impact_score=95.0
        )
        context = self.memory.get_evolutionary_prompt_context("Computer Science")
        self.assertIn("Proven Successful Strategies", context)

if __name__ == '__main__':
    unittest.main()

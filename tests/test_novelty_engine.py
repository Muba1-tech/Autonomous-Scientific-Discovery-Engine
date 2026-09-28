import unittest
from engines.novelty_engine import NoveltyEngine

class TestNoveltyEngine(unittest.TestCase):
    def setUp(self):
        self.engine = NoveltyEngine()

    def test_evaluate_hypothesis(self):
        hypothesis = "Integrating mycelial fungal network resource routing to optimize distributed GPU cluster compute."
        papers = [{"title": "GPU Scheduling", "abstract": "Standard round robin GPU allocation in server clusters."}]
        scores = self.engine.evaluate_hypothesis(hypothesis, papers, simulated_feasibility=0.85)

        self.assertGreaterEqual(scores.novelty_score, 0.0)
        self.assertLessEqual(scores.novelty_score, 100.0)
        self.assertGreaterEqual(scores.priority_score, 0.0)
        self.assertLessEqual(scores.priority_score, 100.0)

if __name__ == '__main__':
    unittest.main()

import unittest
from engines.cross_domain_engine import CrossDomainEngine

class TestCrossDomainEngine(unittest.TestCase):
    def setUp(self):
        self.engine = CrossDomainEngine()

    def test_cross_domain_synthesis(self):
        res = self.engine.generate_cross_domain_hypothesis("Biology", "Computer Science")
        self.assertEqual(res.source_domain, "Biology")
        self.assertEqual(res.target_domain, "Computer Science")
        self.assertIsNotNone(res.transferred_concept)
        self.assertGreaterEqual(res.novelty_score, 0.0)

if __name__ == '__main__':
    unittest.main()

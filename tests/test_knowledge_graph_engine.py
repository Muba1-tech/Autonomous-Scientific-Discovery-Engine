import unittest
from engines.knowledge_graph_engine import KnowledgeGraphEngine

class TestKnowledgeGraphEngine(unittest.TestCase):
    def setUp(self):
        self.kg = KnowledgeGraphEngine()

    def test_graph_operations(self):
        self.kg.ingest_paper({"title": "Attention Is All You Need", "authors": ["Vaswani et al."]})
        stats = self.kg.get_summary()
        self.assertGreaterEqual(stats['total_nodes'], 2)
        self.assertGreaterEqual(stats['total_edges'], 1)

    def test_search_nodes(self):
        self.kg.add_node("Concept:Transformer", "Transformer", "Concept")
        results = self.kg.search_nodes("Transformer")
        self.assertTrue(len(results) > 0)

if __name__ == '__main__':
    unittest.main()

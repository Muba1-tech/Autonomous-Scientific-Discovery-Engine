import unittest
from engines.research_gap_detector import ResearchGapDetector

class TestResearchGapDetector(unittest.TestCase):
    def setUp(self):
        self.detector = ResearchGapDetector()

    def test_detect_gaps_with_papers(self):
        papers = [
            {"title": "Paper A", "abstract": "Study on dropout prediction using logistic regression. Limited sample size.", "source": "ArXiv"},
            {"title": "Paper B", "abstract": "Deep learning for student risk detection. Lacks real-time data integration.", "source": "PubMed"}
        ]
        gaps = self.detector.detect_gaps(papers, "Education")
        self.assertTrue(len(gaps) > 0)
        self.assertIsNotNone(gaps[0].gap_id)
        self.assertEqual(gaps[0].research_domain, "Education")

    def test_detect_gaps_no_papers_edge_case(self):
        gaps = self.detector.detect_gaps([], "Biology")
        self.assertTrue(len(gaps) > 0)
        self.assertIn("Biology", gaps[0].topic)

if __name__ == '__main__':
    unittest.main()

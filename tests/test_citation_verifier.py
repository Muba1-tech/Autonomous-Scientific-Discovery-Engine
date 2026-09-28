import unittest
from engines.citation_verifier import CitationVerifier

class TestCitationVerifier(unittest.TestCase):
    def setUp(self):
        self.verifier = CitationVerifier()

    def test_verify_claims(self):
        text = "Deep learning models predict student dropout with 92% accuracy."
        papers = [{"title": "Student Dropout Study", "abstract": "Deep learning models achieved high 92% accuracy in predicting dropout risk."}]
        res = self.verifier.verify_claims(text, papers)
        self.assertTrue(len(res.claims) > 0)
        self.assertIn(res.claims[0].status, ["SUPPORTED", "PARTIALLY_SUPPORTED"])

    def test_unverified_fallback(self):
        text = "Unverified claim with no literature."
        res = self.verifier.verify_claims(text, [])
        self.assertEqual(res.overall_status, "INSUFFICIENT EVIDENCE")
        self.assertFalse(res.firewall_passed)

if __name__ == '__main__':
    unittest.main()

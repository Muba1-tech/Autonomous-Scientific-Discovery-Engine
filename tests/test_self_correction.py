import unittest
from engines.self_correction_engine import SelfCorrectionEngine

class TestSelfCorrectionEngine(unittest.TestCase):
    def setUp(self):
        self.engine = SelfCorrectionEngine(max_iterations=1)

    def test_self_correction_flow(self):
        hyp = "Valid student dropout prediction model based on historical GPA and engagement."
        context = "Student engagement and GPA are strong predictors of completion."
        final_hyp, audit = self.engine.self_correct(hyp, context)
        self.assertIsNotNone(final_hyp)
        self.assertTrue(len(audit) > 0)

if __name__ == '__main__':
    unittest.main()

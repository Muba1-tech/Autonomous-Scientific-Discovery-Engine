import unittest
from engines.experiment_simulator import ExperimentSimulator

class TestExperimentSimulator(unittest.TestCase):
    def setUp(self):
        self.simulator = ExperimentSimulator(sample_size=30)

    def test_run_simulation(self):
        res = self.simulator.run_simulation("AI prediction of student dropout.")
        self.assertGreaterEqual(res.simulated_feasibility, 0.0)
        self.assertLessEqual(res.simulated_feasibility, 1.0)
        self.assertIn("SIMULATION RESULT", res.limitations)
        self.assertTrue(len(res.plots_base64) > 0)

if __name__ == '__main__':
    unittest.main()

import unittest
from engines.hypothesis_evolution import HypothesisEvolutionEngine
from engines.failure_vault import ScientificFailureVault
from engines.cross_domain_engine import CrossDomainEngine
from simulation.process_sandbox import CustomExperimentCompiler
from engines.sustainability_engine import SustainabilityEngine
from engines.discovery_league import DiscoveryLeague

class TestNewFlagshipFeatures(unittest.TestCase):

    def test_1_evolutionary_memory_pool_and_speciation(self):
        engine = HypothesisEvolutionEngine(population_size=4)
        pop = engine.generate_initial_population("quantum computing")
        self.assertEqual(len(pop), 4)
        speciation = engine.detect_speciation_events(pop)
        self.assertTrue(len(speciation) > 0)
        lineage = engine.export_lineage_tree(pop)
        self.assertIn("nodes", lineage)

    def test_2_replication_crisis_negation_mining(self):
        vault = ScientificFailureVault()
        papers = [{"title": "Failed attempt to observe effect", "abstract": "Null result observed in study."}]
        res = vault.mine_replication_crisis_negations("quantum effect", papers)
        self.assertTrue(res["replication_risk_score"] > 0)
        self.assertTrue(res["crisis_alert"])

    def test_3_cross_domain_transfer(self):
        engine = CrossDomainEngine()
        hyp = engine.generate_cross_domain_hypothesis("Superconductivity", "Dropout Prediction")
        self.assertEqual(hyp.source_domain, "Superconductivity")
        self.assertEqual(hyp.target_domain, "Dropout Prediction")

    def test_4_custom_experiment_dsl_compiler(self):
        compiler = CustomExperimentCompiler()
        code = compiler.compile_custom_dsl("Custom Concentration Experiment")
        self.assertIn("def run_custom_experiment():", code)

    def test_6_sustainability_and_fair_score(self):
        sust = SustainabilityEngine()
        metrics = sust.calculate_sustainability_metrics(execution_time_sec=12.5)
        self.assertIn("carbon_footprint_g_co2", metrics)
        self.assertTrue(metrics["fair_compliance_score"] > 80.0)

    def test_7_discovery_league(self):
        league = DiscoveryLeague()
        lb = league.get_leaderboard()
        self.assertTrue(len(lb) > 0)
        badges = league.evaluate_badges(novelty=95.0, priority=92.0, fair_score=94.0)
        self.assertIn("🏆 Champion Discovery", badges)

if __name__ == "__main__":
    unittest.main()

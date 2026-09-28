class ConsensusEngine:
    def resolve(self, validation_results, critique):
        if validation_results.get("final_verdict") == "Approved":
            return True, "Consensus reached among agents: Hypothesis is theoretically sound and feasible."
        else:
            return False, "Consensus failed: Hypothesis rejected based on rules or causal conflicts."

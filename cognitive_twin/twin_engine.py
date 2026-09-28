from engines.knowledge_graph_engine import KnowledgeGraphEngine
from cognitive_twin.thought_graph import ThoughtGraph
from cognitive_twin.causal_graph import CausalGraph

class TwinEngine:
    def __init__(self):
        self.kg = KnowledgeGraphEngine()
        self.tg = ThoughtGraph()
        self.cg = CausalGraph()
        
    def integrate_paper(self, paper):
        self.kg.ingest_paper(paper)
        
    def status(self):
        return {
            "kg_stats": self.kg.get_summary(),
            "tg_steps": self.tg.step_counter,
            "is_causal_valid": self.cg.is_valid_dag()
        }

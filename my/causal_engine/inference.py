import networkx as nx

class CausalInference:
    def __init__(self, causal_model):
        self.model = causal_model
        
    def check_path(self, cause, effect):
        if cause in self.model.dag and effect in self.model.dag:
            return nx.has_path(self.model.dag, cause, effect)
        return False
        
    def infer_effect(self, cause):
        if cause in self.model.dag:
            return list(nx.descendants(self.model.dag, cause))
        return []

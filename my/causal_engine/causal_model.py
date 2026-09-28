import networkx as nx

class CausalModel:
    def __init__(self):
        self.dag = nx.DiGraph()
        
    def build_from_text(self, concepts):
        for i in range(len(concepts) - 1):
            self.dag.add_edge(concepts[i], concepts[i+1], relation="causes")
            
    def get_model_structure(self):
        return list(self.dag.edges(data=True))

import networkx as nx

class CausalGraph:
    def __init__(self):
        self.dag = nx.DiGraph()
        
    def add_causal_link(self, cause, effect, weight=1.0):
        self.dag.add_edge(cause, effect, weight=weight)
        
    def is_valid_dag(self):
        return nx.is_directed_acyclic_graph(self.dag)

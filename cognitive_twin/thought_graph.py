import networkx as nx

class ThoughtGraph:
    def __init__(self):
        self.graph = nx.DiGraph()
        self.step_counter = 0
        
    def add_thought_step(self, thought, parent_step=None):
        self.step_counter += 1
        node_id = f"step_{self.step_counter}"
        self.graph.add_node(node_id, thought=thought)
        if parent_step:
            self.graph.add_edge(parent_step, node_id)
        return node_id
        
    def get_chain(self):
        return [data['thought'] for _, data in self.graph.nodes(data=True)]

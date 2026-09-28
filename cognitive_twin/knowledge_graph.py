import networkx as nx
from pyvis.network import Network
import tempfile
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io

class KnowledgeGraph:
    def __init__(self):
        self.graph = nx.DiGraph()
    
    def add_entity(self, entity, attributes=None):
        self.graph.add_node(entity, **(attributes or {}))
    
    def add_relation(self, source, target, relation):
        self.graph.add_edge(source, target, relation=relation)
    
    def get_summary(self):
        return {"nodes": self.graph.number_of_nodes(), "edges": self.graph.number_of_edges()}

    def get_pyvis_html(self):
        net = Network(height="100vh", width="100%", directed=True, notebook=False)
        net.from_nx(self.graph)
        # Generate temp html string for UI rendering
        path = tempfile.mktemp(suffix=".html")
        net.write_html(path)
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    def get_static_image(self):
        plt.figure(figsize=(10, 6))
        pos = nx.spring_layout(self.graph)
        nx.draw(self.graph, pos, with_labels=True, node_color="#c8b6ff", node_size=2000, font_size=10, font_color="#4a148c", edge_color="#a2d2ff", width=2.0, edgecolors="#4a148c")
        buf = io.BytesIO()
        plt.savefig(buf, format="png", bbox_inches="tight", transparent=True)
        plt.close()
        buf.seek(0)
        return buf.getvalue()

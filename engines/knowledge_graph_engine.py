import networkx as nx
from pyvis.network import Network
import tempfile
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import json
from typing import List, Dict, Any, Optional, Tuple

# Distinct visual color coding for node types
# Distinct visual color coding for node types
NODE_COLOR_MAP = {
    "Paper": "#38bdf8",            # Sky Blue
    "Author": "#50e3c2",           # Teal
    "Concept": "#a855f7",          # Purple
    "Research Question": "#f5a623",# Amber
    "Hypothesis": "#10b981",       # Emerald Green
    "Dataset": "#e67e22",          # Orange
    "Method": "#94a3b8",           # Slate Grey
    "Experiment": "#f43f5e",       # Rose Red
    "Research Gap": "#ec4899",     # Hot Pink
    "Claim": "#06b6d4"             # Cyan / Status-colored
}

class KnowledgeGraphEngine:
    """
    Advanced Dynamic Knowledge Graph Engine for PROJECT AION.
    Tracks entities across 10 node types and 10 relationship types using NetworkX.
    Exports interactive PyVis HTML and static Matplotlib figures.
    """
    def __init__(self):
        self.graph = nx.DiGraph()

    def add_node(self, node_id: str, label: str, node_type: str, metadata: Optional[Dict[str, Any]] = None):
        """
        Adds or updates a node with explicit type and color styling.
        """
        color = NODE_COLOR_MAP.get(node_type, "#9b59b6")
        attrs = {
            "label": label,
            "type": node_type,
            "color": color,
            "title": f"[{node_type}] {label}"
        }
        if metadata:
            attrs.update(metadata)
        self.graph.add_node(node_id, **attrs)

    def add_relationship(self, source_id: str, target_id: str, relation_type: str, weight: float = 1.0):
        """
        Adds a directed relationship edge between two nodes.
        Supported relations: SUPPORTS, CONTRADICTS, USES_METHOD, USES_DATASET, RELATED_TO, EXTENDS, INSPIRED_BY, TESTS, PRODUCES, ADDRESSES_GAP, EVIDENCE_FOR
        """
        self.graph.add_edge(source_id, target_id, relation=relation_type, title=relation_type, weight=weight)

    def ingest_paper(self, paper: Dict[str, Any]):
        title = paper.get('title', 'Untitled Paper')
        paper_id = f"Paper:{title}"
        self.add_node(paper_id, title[:45] + ("..." if len(title) > 45 else ""), "Paper", {
            "source": paper.get('source', ''),
            "url": paper.get('url', ''),
            "title": f"[Paper] {title}\nVenue: {paper.get('source', 'Scholarly')}\nDOI/URL: {paper.get('url', '')}"
        })
        
        # Ingest authors if present
        authors = paper.get('authors', [])
        for author in authors:
            auth_id = f"Author:{author}"
            self.add_node(auth_id, author, "Author")
            self.add_relationship(auth_id, paper_id, "EXTENDS")

    def ingest_gap(self, gap: Any):
        gap_id = getattr(gap, 'gap_id', str(gap))
        topic = getattr(gap, 'topic', str(gap))
        node_key = f"Gap:{gap_id}"
        self.add_node(node_key, f"Gap: {topic[:38]}...", "Research Gap", {
            "domain": getattr(gap, 'research_domain', ''),
            "title": f"[Research Gap] {topic}\nDomain: {getattr(gap, 'research_domain', '')}"
        })
        
        # Connect to supporting papers
        supporting_papers = getattr(gap, 'supporting_papers', [])
        linked = False
        for p_title in supporting_papers:
            p_id = f"Paper:{p_title}"
            if self.graph.has_node(p_id):
                self.add_relationship(node_key, p_id, "ADDRESSES_GAP")
                linked = True
            else:
                for n in self.graph.nodes():
                    if n.startswith("Paper:") and (p_title.lower() in n.lower() or n[6:].lower() in p_title.lower()):
                        self.add_relationship(node_key, n, "ADDRESSES_GAP")
                        linked = True
                        break
        # Fallback link to first paper in graph if no specific paper matched
        if not linked:
            for n in self.graph.nodes():
                if n.startswith("Paper:"):
                    self.add_relationship(node_key, n, "ADDRESSES_GAP")
                    break

    def ingest_hypothesis(self, hypothesis_text: str, domain: str, research_id: str, gaps: Optional[List[Any]] = None):
        hyp_id = f"Hypothesis:{research_id}"
        short_title = hypothesis_text[:45] + ("..." if len(hypothesis_text) > 45 else "")
        self.add_node(hyp_id, f"💡 Hypothesis: {short_title}", "Hypothesis", {
            "domain": domain,
            "title": f"[Novel Hypothesis]\n{hypothesis_text[:280]}..."
        })

        # Connect to gaps
        if gaps:
            for g in gaps:
                gap_key = f"Gap:{getattr(g, 'gap_id', str(g))}"
                if self.graph.has_node(gap_key):
                    self.add_relationship(hyp_id, gap_key, "ADDRESSES_GAP")
                else:
                    for n in self.graph.nodes():
                        if n.startswith("Gap:"):
                            self.add_relationship(hyp_id, n, "ADDRESSES_GAP")
                            break
        else:
            for n in self.graph.nodes():
                if n.startswith("Gap:"):
                    self.add_relationship(hyp_id, n, "ADDRESSES_GAP")

    def ingest_experiment(self, sim_result: Any, research_id: str):
        if not sim_result:
            return
        exp_id = f"Experiment:{research_id}"
        outcome = getattr(sim_result, 'expected_outcome', 'Simulated Protocol')
        p_val = getattr(sim_result, 'evaluation_metrics', {}).get('p_value', 0.001) if hasattr(sim_result, 'evaluation_metrics') else 0.001
        self.add_node(exp_id, f"🧪 Sandbox Sim (p={p_val})", "Experiment", {
            "outcome": outcome,
            "title": f"[AST Sandbox Experiment]\nOutcome: {outcome}\np-value: {p_val}"
        })
        hyp_id = f"Hypothesis:{research_id}"
        if self.graph.has_node(hyp_id):
            self.add_relationship(exp_id, hyp_id, "TESTS")

    def ingest_citation(self, claim: Any, research_id: str):
        if not claim:
            return
        claim_text = getattr(claim, 'claim_text', str(claim))
        status = getattr(claim, 'status', 'SUPPORTED')
        source = getattr(claim, 'supporting_source', '')
        confidence = getattr(claim, 'confidence', 0.85)
        claim_id = f"Claim:{claim_text[:30]}"

        # Status-aware visual color coding
        status_color = "#10b981" if status == "SUPPORTED" else ("#f59e0b" if status == "PARTIALLY_SUPPORTED" else "#ef4444")
        self.add_node(claim_id, f"[{status[:4]}] {claim_text[:30]}...", "Claim", {
            "status": status,
            "color": status_color,
            "title": f"[{status} - {int(confidence*100)}% Match]\nClaim: {claim_text}\nSource: {source}"
        })
        
        hyp_id = f"Hypothesis:{research_id}"
        if self.graph.has_node(hyp_id):
            rel = "SUPPORTS" if status in ["SUPPORTED", "PARTIALLY_SUPPORTED"] else "CONTRADICTS" if status == "CONTRADICTED" else "RELATED_TO"
            self.add_relationship(claim_id, hyp_id, rel)
            
        if source and source not in ["None", "UNVERIFIED"]:
            p_id = f"Paper:{source}"
            if self.graph.has_node(p_id):
                self.add_relationship(p_id, claim_id, "EVIDENCE_FOR")
            else:
                for n in self.graph.nodes():
                    if n.startswith("Paper:") and (source.lower() in n.lower() or n[6:].lower() in source.lower()):
                        self.add_relationship(n, claim_id, "EVIDENCE_FOR")
                        break

    def search_nodes(self, query: str) -> List[Tuple[str, Dict[str, Any]]]:
        """
        Searches graph nodes matching the query string.
        """
        matches = []
        for n, data in self.graph.nodes(data=True):
            if query.lower() in n.lower() or query.lower() in data.get('label', '').lower():
                matches.append((n, data))
        return matches

    def get_subgraph_around(self, node_id: str, radius: int = 1) -> nx.DiGraph:
        """
        Extracts egocentric neighborhood subgraph around a specific node.
        """
        if not self.graph.has_node(node_id):
            return nx.DiGraph()
        nodes = nx.single_source_shortest_path_length(self.graph, node_id, cutoff=radius).keys()
        return self.graph.subgraph(nodes).copy()

    def get_pyvis_html(self, node_filter_type: Optional[str] = None) -> str:
        """
        Renders interactive PyVis HTML canvas.
        """
        net = Network(height="650px", width="100%", directed=True, notebook=False, bgcolor="#030a0d", font_color="#ffffff")
        
        target_graph = self.graph
        if node_filter_type and node_filter_type != "All":
            filtered_nodes = [n for n, d in self.graph.nodes(data=True) if d.get('type') == node_filter_type]
            target_graph = self.graph.subgraph(filtered_nodes).copy()

        net.from_nx(target_graph)
        
        # Configure physics for smooth, quick stabilization so nodes settle cleanly without endless jitter
        options = {
            "physics": {
                "barnesHut": {
                    "gravitationalConstant": -4000,
                    "centralGravity": 0.3,
                    "springLength": 120,
                    "springConstant": 0.04,
                    "damping": 0.85,
                    "avoidOverlap": 0.6
                },
                "minVelocity": 0.75,
                "stabilization": {
                    "enabled": True,
                    "iterations": 150,
                    "updateInterval": 25
                }
            },
            "nodes": {
                "font": {"size": 14, "color": "#ffffff"},
                "borderWidth": 2
            },
            "edges": {
                "color": {"color": "#64748b", "highlight": "#38bdf8"},
                "smooth": {"type": "continuous"}
            },
            "interaction": {
                "hover": True,
                "navigationButtons": True,
                "zoomView": True,
                "dragNodes": True
            }
        }
        net.set_options(json.dumps(options))
        
        path = tempfile.mktemp(suffix=".html")
        net.write_html(path)
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    def get_static_image(self) -> bytes:
        """
        Renders Matplotlib static snapshot of the knowledge graph.
        """
        plt.figure(figsize=(10, 6), facecolor='#030a0d')
        ax = plt.gca()
        ax.set_facecolor('#030a0d')
        
        if self.graph.number_of_nodes() == 0:
            plt.text(0.5, 0.5, "Empty Knowledge Graph", color="white", ha="center", va="center")
        else:
            pos = nx.spring_layout(self.graph, seed=42)
            colors = [data.get('color', '#9b59b6') for n, data in self.graph.nodes(data=True)]
            nx.draw_networkx_nodes(self.graph, pos, node_color=colors, node_size=1500, alpha=0.9)
            nx.draw_networkx_labels(self.graph, pos, font_size=8, font_color="#ffffff")
            nx.draw_networkx_edges(self.graph, pos, edge_color="#34495e", width=1.5, arrowsize=15)
            
        buf = io.BytesIO()
        plt.savefig(buf, format="png", bbox_inches="tight", transparent=True)
        plt.close()
        buf.seek(0)
        return buf.getvalue()

    def get_summary(self) -> Dict[str, int]:
        return {
            "total_nodes": self.graph.number_of_nodes(),
            "total_edges": self.graph.number_of_edges()
        }

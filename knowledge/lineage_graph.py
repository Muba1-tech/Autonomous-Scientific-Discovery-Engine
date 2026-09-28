"""
AION X 2.0 — Evidence Lineage & Claim Dependency Graph
Answers: 'Why does AION believe this?'
Traces full provenance:
Conclusion -> Hypothesis -> Evidence -> Claim -> Source -> Passage/Dataset -> Experiment -> Statistical Result
"""

import json
import logging
from typing import List, Dict, Any, Optional, Set
import networkx as nx

logger = logging.getLogger(__name__)


class EvidenceLineageGraph:
    """
    Typed Evidence Lineage Graph & Claim Dependency Tracker for AION X 2.0.
    Provides complete bidirectional provenance and dependency fragility analysis.
    """

    def __init__(self, db_manager=None):
        self.db = db_manager
        self.g = nx.DiGraph()
        self._nodes: Dict[str, Dict[str, Any]] = {}
        self._edges: List[Dict[str, Any]] = []

    def add_entity(self, entity_id: str, entity_type: str, label: str, metadata: Optional[Dict[str, Any]] = None):
        """Add a typed scientific entity to the lineage graph."""
        data = {
            "id": entity_id,
            "type": entity_type,  # Source, Paper, Passage, Figure, Table, Dataset, Claim, Evidence, Hypothesis, Experiment, ExperimentResult, StatisticalResult, Inference, Conclusion
            "label": label,
            "metadata": metadata or {}
        }
        self._nodes[entity_id] = data
        self.g.add_node(entity_id, **data)

    def add_relation(self, source_id: str, source_type: str, target_id: str, target_type: str, relation: str, mission_id: str = ""):
        """
        Add an explicit provenance relation.
        e.g., SOURCE_CONTAINS_PASSAGE, PASSAGE_SUPPORTS_CLAIM, CLAIM_SUPPORTS_HYPOTHESIS,
        HYPOTHESIS_TESTED_BY_EXPERIMENT, EXPERIMENT_PRODUCES_RESULT, CONCLUSION_DEPENDS_ON_HYPOTHESIS
        """
        edge_data = {
            "source_id": source_id,
            "source_type": source_type,
            "target_id": target_id,
            "target_type": target_type,
            "relation": relation,
            "mission_id": mission_id
        }
        self.g.add_edge(source_id, target_id, **edge_data)

        if self.db:
            try:
                self.db.insert_provenance_record(
                    source_entity_id=source_id,
                    source_entity_type=source_type,
                    target_entity_id=target_id,
                    target_entity_type=target_type,
                    relation=relation,
                    mission_id=mission_id
                )
            except Exception as e:
                logger.warning(f"Error recording provenance in db: {e}")

    def get_provenance_chain(self, target_entity_id: str) -> Dict[str, Any]:
        """
        Traces backwards from a Conclusion or Hypothesis to all supporting
        Hypotheses, Claims, Papers, Passages, Experiments, and Statistical Results.
        """
        if target_entity_id not in self.g:
            return {
                "target_id": target_entity_id,
                "found": False,
                "chain": [],
                "summary": "Target entity not found in active lineage graph."
            }

        # Find all ancestor nodes (predecessors in reversed graph or paths to target)
        ancestors = nx.ancestors(self.g, target_entity_id) | {target_entity_id}
        subgraph = self.g.subgraph(ancestors)

        nodes_list = [subgraph.nodes[n] for n in subgraph.nodes]
        edges_list = [
            {
                "source": u,
                "target": v,
                "relation": subgraph.edges[u, v].get("relation", "DEPENDS_ON")
            }
            for u, v in subgraph.edges
        ]

        # Categorize by entity type
        sources = [n for n in nodes_list if n.get("type") in ["Source", "Paper"]]
        passages = [n for n in nodes_list if n.get("type") in ["Passage", "Figure", "Table", "Dataset"]]
        claims = [n for n in nodes_list if n.get("type") in ["Claim", "Evidence"]]
        hypotheses = [n for n in nodes_list if n.get("type") == "Hypothesis"]
        experiments = [n for n in nodes_list if n.get("type") in ["Experiment", "ExperimentResult", "StatisticalResult"]]

        return {
            "target_id": target_entity_id,
            "target_node": self.g.nodes[target_entity_id],
            "found": True,
            "total_nodes": len(nodes_list),
            "total_edges": len(edges_list),
            "nodes": nodes_list,
            "edges": edges_list,
            "breakdown": {
                "sources_count": len(sources),
                "passages_count": len(passages),
                "claims_count": len(claims),
                "hypotheses_count": len(hypotheses),
                "experiments_count": len(experiments)
            },
            "sources": sources,
            "passages": passages,
            "claims": claims,
            "hypotheses": hypotheses,
            "experiments": experiments
        }

    def get_claim_evidence(self, claim_id: str) -> Dict[str, Any]:
        """Finds all supporting and contradicting passages/sources for a claim."""
        supporting = []
        contradicting = []

        if claim_id in self.g:
            # Predecessors of the claim
            for pred in self.g.predecessors(claim_id):
                edge_data = self.g.edges[pred, claim_id]
                rel = edge_data.get("relation", "")
                node = self.g.nodes[pred]
                if "CONTRADICT" in rel:
                    contradicting.append({"node": node, "relation": rel})
                else:
                    supporting.append({"node": node, "relation": rel})

        return {
            "claim_id": claim_id,
            "supporting_evidence": supporting,
            "contradicting_evidence": contradicting,
            "is_contradicted": len(contradicting) > 0,
            "support_count": len(supporting),
            "contradiction_count": len(contradicting)
        }

    def get_hypothesis_support(self, hypothesis_id: str) -> List[Dict[str, Any]]:
        """Returns all claims, evidence, and experiment results supporting a hypothesis."""
        support = []
        if hypothesis_id in self.g:
            for pred in self.g.predecessors(hypothesis_id):
                rel = self.g.edges[pred, hypothesis_id].get("relation", "")
                if "SUPPORT" in rel or "VALIDATE" in rel or "GENERATED" in rel or "TEST" in rel:
                    support.append({
                        "id": pred,
                        "node": self.g.nodes[pred],
                        "relation": rel
                    })
        return support

    def get_hypothesis_contradictions(self, hypothesis_id: str) -> List[Dict[str, Any]]:
        """Returns all contradicting claims, refuted experiments, or falsification results."""
        contradictions = []
        if hypothesis_id in self.g:
            for pred in self.g.predecessors(hypothesis_id):
                rel = self.g.edges[pred, hypothesis_id].get("relation", "")
                if "CONTRADICT" in rel or "REFUTE" in rel or "FAIL" in rel:
                    contradictions.append({
                        "id": pred,
                        "node": self.g.nodes[pred],
                        "relation": rel
                    })
        return contradictions

    def get_downstream_dependencies(self, claim_id: str) -> List[Dict[str, Any]]:
        """
        Finds all hypotheses, inferences, and conclusions that depend on a specific claim.
        Crucial for calculating cascade impact if a claim is retracted or contradicted.
        """
        if claim_id not in self.g:
            return []

        descendants = nx.descendants(self.g, claim_id)
        dependent_nodes = []
        for d in descendants:
            node = self.g.nodes[d]
            dependent_nodes.append({
                "id": d,
                "type": node.get("type", "Unknown"),
                "label": node.get("label", ""),
                "is_conclusion": node.get("type") == "Conclusion"
            })
        return dependent_nodes

    def invalidate_downstream_claims(self, claim_id: str) -> Dict[str, Any]:
        """
        Simulates the effect of invalidating/contradicting a claim.
        Returns all affected downstream conclusions and hypotheses.
        """
        dependencies = self.get_downstream_dependencies(claim_id)
        affected_conclusions = [d for d in dependencies if d["type"] == "Conclusion"]
        affected_hypotheses = [d for d in dependencies if d["type"] == "Hypothesis"]

        return {
            "invalidated_claim_id": claim_id,
            "total_affected_entities": len(dependencies),
            "affected_conclusions": affected_conclusions,
            "affected_hypotheses": affected_hypotheses,
            "severity": "CRITICAL" if len(affected_conclusions) > 0 else "MODERATE" if len(affected_hypotheses) > 0 else "LOW"
        }

    def calculate_conclusion_fragility(self, conclusion_id: str) -> Dict[str, Any]:
        """
        Calculates how fragile a conclusion is based on:
        - Total number of supporting claims
        - Number of claims that have single-source dependencies
        - Presence of any contradicted predecessor claims
        """
        chain = self.get_provenance_chain(conclusion_id)
        if not chain.get("found"):
            return {"conclusion_id": conclusion_id, "fragility_score": 1.0, "robustness": "LOW", "reason": "No provenance chain."}

        claims = chain.get("claims", [])
        sources = chain.get("sources", [])
        total_claims = len(claims)
        if total_claims == 0:
            return {"conclusion_id": conclusion_id, "fragility_score": 0.8, "robustness": "LOW", "reason": "Conclusion has zero underlying claims."}

        # Check if any claim has contradictions
        contradicted_claims = 0
        for c in claims:
            cid = c.get("id")
            if cid:
                ev = self.get_claim_evidence(cid)
                if ev.get("is_contradicted"):
                    contradicted_claims += 1

        # Calculate fragility
        contradiction_ratio = contradicted_claims / max(1, total_claims)
        source_diversity = min(1.0, len(sources) / max(1, total_claims))
        fragility = round(0.5 * contradiction_ratio + 0.5 * (1.0 - source_diversity), 2)

        robustness = "HIGH" if fragility < 0.25 else "MEDIUM" if fragility < 0.60 else "LOW"

        return {
            "conclusion_id": conclusion_id,
            "fragility_score": fragility,
            "robustness": robustness,
            "total_claims": total_claims,
            "contradicted_claims": contradicted_claims,
            "distinct_sources": len(sources),
            "is_single_source_dependent": len(sources) <= 1 and total_claims > 0
        }

    def export_graph_json(self) -> str:
        """Exports graph in D3/Cytoscape/VisJS compatible JSON format."""
        nodes = []
        for n, data in self.g.nodes(data=True):
            nodes.append({
                "id": n,
                "label": data.get("label", n),
                "type": data.get("type", "Concept"),
                "metadata": data.get("metadata", {})
            })

        edges = []
        for u, v, data in self.g.edges(data=True):
            edges.append({
                "source": u,
                "target": v,
                "relation": data.get("relation", "RELATED_TO")
            })

        return json.dumps({"nodes": nodes, "edges": edges}, indent=2)

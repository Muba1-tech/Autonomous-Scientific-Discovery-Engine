"""
Discovery League & Gamified Ranking Engine for AION X.
Manages global/domain leaderboards, community voting, and achievement badges.
"""
from typing import List, Dict, Any

class DiscoveryLeague:
    """Ranks scientific discoveries and assigns gamified achievement badges."""

    def get_leaderboard(self) -> List[Dict[str, Any]]:
        """Returns top-ranked discoveries across scientific domains."""
        return [
            {
                "rank": 1,
                "domain": "Room-Temperature Superconductivity",
                "title": "Interfacial Topological Phonon-Polariton Coupling",
                "priority_score": 96.8,
                "novelty": 98.2,
                "badge": "🏆 Champion Discovery",
                "upvotes": 142
            },
            {
                "rank": 2,
                "domain": "CAR-T Cancer Immunotherapy",
                "title": "Multi-Target Synergistic Receptor Base-Editing",
                "priority_score": 94.5,
                "novelty": 95.0,
                "badge": "🧬 Genome Master",
                "upvotes": 118
            },
            {
                "rank": 3,
                "domain": "Solid-State Battery Energy Storage",
                "title": "2D MXene Interfacial Buffer Engineering",
                "priority_score": 92.1,
                "novelty": 93.4,
                "badge": "⚡ Cross-Domain Pioneer",
                "upvotes": 96
            },
            {
                "rank": 4,
                "domain": "Student Dropout Prediction",
                "title": "Causal Graph Neural Operators with Lyapunov Stability",
                "priority_score": 89.4,
                "novelty": 90.5,
                "badge": "🌿 Eco-Scientist",
                "upvotes": 75
            }
        ]

    def evaluate_badges(self, novelty: float, priority: float, fair_score: float) -> List[str]:
        """Assigns achievement badges based on discovery metrics."""
        badges = ["🔬 Scientific Explorer"]
        if priority >= 90.0:
            badges.append("🏆 Champion Discovery")
        if novelty >= 92.0:
            badges.append("🧬 Genome Master")
        if fair_score >= 90.0:
            badges.append("🌿 Eco-Scientist")
        badges.append("🔴 Popperian Slayer")
        return badges

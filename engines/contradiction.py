"""Contradiction Hunter & Engine for AION X.
Performs pairwise evidence comparison, semantic discrepancy analysis, and contradictory evidence hunting.
"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
import re
from enum import Enum


class ContradictionStrength(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass
class Evidence:
    content: str
    source: str = ""
    confidence: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ComparisonResult:
    is_contradiction: bool
    strength_score: float  # 0.0 to 1.0
    explanation: str = ""
    category: str = "NO_CONTRADICTION"  # NO_CONTRADICTION, MINOR, SIGNIFICANT, MAJOR


class ContradictionHunter:
    """Detects and scores empirical and logical contradictions between claims/evidence."""

    OPPOSITION_PAIRS = [
        ("causes", "prevents"),
        ("increases", "decreases"),
        ("accelerates", "decelerates"),
        ("improves", "degrades"),
        ("promotes", "inhibits"),
        ("stimulates", "suppresses"),
        ("activates", "deactivates"),
        ("enhances", "reduces"),
        ("supports", "refutes"),
        ("proves", "disproves"),
        ("positive", "negative"),
        ("effective", "ineffective"),
    ]

    def compare_evidence(self, e1: Evidence, e2: Evidence) -> ComparisonResult:
        """Compare two pieces of evidence for direct contradiction and score severity."""
        t1 = e1.content.lower().strip()
        t2 = e2.content.lower().strip()

        # Check for direct opposing relation terms
        detected_contradiction = False
        strength = 0.0
        matched_pair = None

        for pos, neg in self.OPPOSITION_PAIRS:
            if (pos in t1 and neg in t2) or (neg in t1 and pos in t2):
                detected_contradiction = True
                matched_pair = (pos, neg)
                break

        # Check for explicit negation
        if not detected_contradiction:
            negations = [" not ", " never ", " fails to ", " does not ", " cannot "]
            has_neg1 = any(n in t1 for n in negations)
            has_neg2 = any(n in t2 for n in negations)
            if has_neg1 != has_neg2:
                # Strip negations and check lexical overlap
                words1 = set(re.findall(r'\w+', t1))
                words2 = set(re.findall(r'\w+', t2))
                overlap = len(words1.intersection(words2)) / max(1, min(len(words1), len(words2)))
                if overlap > 0.5:
                    detected_contradiction = True
                    strength = 0.75

        if detected_contradiction:
            if strength == 0.0:
                # Calculate strength based on modifier adverbs (e.g. significantly vs slightly)
                intensifiers = ["significantly", "strongly", "substantially", "drastically", "completely", "critical"]
                has_intensifier = any(i in t1 or i in t2 for i in intensifiers)
                strength = 0.85 if has_intensifier else 0.70
            
            category = "MAJOR" if strength >= 0.8 else "SIGNIFICANT"
            explanation = f"Opposing evidence detected ({matched_pair[0]} vs {matched_pair[1]})" if matched_pair else "Direct negated assertion"
            return ComparisonResult(
                is_contradiction=True,
                strength_score=round(strength, 3),
                explanation=explanation,
                category=category
            )

        return ComparisonResult(
            is_contradiction=False,
            strength_score=0.0,
            explanation="No semantic or logical contradiction detected.",
            category="NO_CONTRADICTION"
        )

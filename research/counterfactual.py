import json
import logging
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

from llm_engine.router import smart_route_prompt

logger = logging.getLogger(__name__)

@dataclass
class CounterfactualResult:
    question: str
    scenario: str
    outcomes: List[str] = field(default_factory=list)
    assumptions: List[str] = field(default_factory=list)
    underlying_model: str = ""
    uncertainty: str = ""
    limitations: List[str] = field(default_factory=list)

class CounterfactualEngine:
    def __init__(self):
        pass

    def evaluate(self, question: str, context: str) -> CounterfactualResult:
        prompt = (
            f"You are a Counterfactual Engine. Evaluate this question:\n"
            f"Question: {question}\nContext: {context}\n"
            f"Return a JSON object with the following keys:\n"
            f"- 'scenario': string describing the modified scenario\n"
            f"- 'outcomes': list of strings of predicted outcomes\n"
            f"- 'assumptions': list of strings of assumptions made\n"
            f"- 'underlying_model': string explaining the theoretical model used\n"
            f"- 'uncertainty': string describing confidence/uncertainty in outcomes\n"
            f"- 'limitations': list of strings of limitations of this evaluation"
        )
        response = smart_route_prompt(prompt)
        try:
            data = json.loads(response)
            return CounterfactualResult(
                question=question,
                scenario=data.get("scenario", ""),
                outcomes=data.get("outcomes", []),
                assumptions=data.get("assumptions", []),
                underlying_model=data.get("underlying_model", ""),
                uncertainty=data.get("uncertainty", ""),
                limitations=data.get("limitations", [])
            )
        except json.JSONDecodeError:
            logger.error("Failed to parse counterfactual result")
            return CounterfactualResult(
                question=question,
                scenario="Error",
                uncertainty="Failed to parse response."
            )

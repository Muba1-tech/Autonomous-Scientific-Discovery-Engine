import json
import logging
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional
from enum import Enum

from llm_engine.router import smart_route_prompt

logger = logging.getLogger(__name__)

class TestType(Enum):
    CONCEPTUAL = "CONCEPTUAL"
    SIMULATION = "SIMULATION"
    EMPIRICAL = "EMPIRICAL"

class TestStatus(Enum):
    PENDING = "PENDING"
    PASSED = "PASSED"
    FAILED = "FAILED"
    INCONCLUSIVE = "INCONCLUSIVE"

@dataclass
class FalsificationTest:
    name: str
    description: str
    test_type: TestType
    criteria: str
    status: TestStatus = TestStatus.PENDING
    result_details: str = ""

@dataclass
class FalsificationResult:
    hypothesis: str
    survival_score: float
    tests: List[FalsificationTest]
    tests_passed: int
    tests_attempted: int
    note: str = "Survival of falsification is NOT positive proof of truth."

@dataclass
class FalsificationSummary:
    hypothesis: str
    overall_survival_score: float
    summary: str
    results: List[FalsificationResult] = field(default_factory=list)
    
    def to_json(self) -> str:
        return json.dumps(asdict(self), default=str)

class FalsificationEngine:
    """
    Engine to design and run falsification tests for high-ranking hypotheses.
    """
    def __init__(self):
        pass
        
    def formulate_tests(self, hypothesis: str) -> List[FalsificationTest]:
        """
        Formulate precise falsification criteria for the given hypothesis.
        """
        prompt = f"""
You are an expert scientist applying rigorous falsification principles.
For the following hypothesis, formulate precise falsification criteria ("What empirical observation or test would prove this hypothesis wrong?")
and design potential falsification tests (conceptual, simulation, empirical).

HYPOTHESIS: {hypothesis}

Output a JSON array of objects with the following structure:
[
    {{
        "name": "Test Name",
        "description": "Test Description",
        "test_type": "CONCEPTUAL|SIMULATION|EMPIRICAL",
        "criteria": "Precise falsification criteria"
    }}
]
Return ONLY valid JSON.
"""
        try:
            response = smart_route_prompt(prompt)
            if response.startswith("```json"):
                response = response[7:-3].strip()
            elif response.startswith("```"):
                response = response[3:-3].strip()
                
            data = json.loads(response)
            
            tests = []
            for item in data:
                try:
                    test_type = TestType[item.get("test_type", "CONCEPTUAL").upper()]
                except KeyError:
                    test_type = TestType.CONCEPTUAL
                    
                tests.append(FalsificationTest(
                    name=item.get("name", "Unknown Test"),
                    description=item.get("description", ""),
                    test_type=test_type,
                    criteria=item.get("criteria", "")
                ))
            return tests
        except Exception as e:
            logger.error(f"Error formulating tests for hypothesis '{hypothesis}': {e}")
            return []

    def evaluate_test(self, hypothesis: str, test: FalsificationTest) -> FalsificationTest:
        """
        Run/evaluate a falsification test.
        """
        prompt = f"""
You are evaluating a falsification test for a hypothesis.
HYPOTHESIS: {hypothesis}
TEST NAME: {test.name}
TEST TYPE: {test.test_type.value}
DESCRIPTION: {test.description}
FALSIFICATION CRITERIA: {test.criteria}

Based on current scientific knowledge and reasoning, simulate or theoretically evaluate this test.
Does the hypothesis pass (survive) or fail the falsification test?
Output a JSON object:
{{
    "status": "PASSED|FAILED|INCONCLUSIVE",
    "result_details": "Detailed explanation of the test outcome."
}}
Return ONLY valid JSON.
"""
        try:
            response = smart_route_prompt(prompt)
            if response.startswith("```json"):
                response = response[7:-3].strip()
            elif response.startswith("```"):
                response = response[3:-3].strip()
                
            data = json.loads(response)
            
            try:
                test.status = TestStatus[data.get("status", "INCONCLUSIVE").upper()]
            except KeyError:
                test.status = TestStatus.INCONCLUSIVE
                
            test.result_details = data.get("result_details", "")
        except Exception as e:
            logger.error(f"Error evaluating test '{test.name}': {e}")
            test.status = TestStatus.INCONCLUSIVE
            test.result_details = f"Evaluation failed: {str(e)}"
            
        return test
        
    def run(self, hypothesis: str) -> FalsificationSummary:
        """
        Formulate, evaluate tests, and calculate survival score.
        """
        tests = self.formulate_tests(hypothesis)
        evaluated_tests = []
        
        tests_attempted = len(tests)
        tests_passed = 0
        
        for test in tests:
            evaluated_test = self.evaluate_test(hypothesis, test)
            evaluated_tests.append(evaluated_test)
            if evaluated_test.status == TestStatus.PASSED:
                tests_passed += 1
                
        survival_score = 0.0
        if tests_attempted > 0:
            survival_score = (tests_passed / tests_attempted) * 100
            
        result = FalsificationResult(
            hypothesis=hypothesis,
            survival_score=survival_score,
            tests=evaluated_tests,
            tests_passed=tests_passed,
            tests_attempted=tests_attempted
        )
        
        return FalsificationSummary(
            hypothesis=hypothesis,
            overall_survival_score=survival_score,
            summary=f"Evaluated {tests_attempted} tests. Hypothesis passed {tests_passed}. Survival score: {survival_score:.2f}%. Survival of falsification is NOT positive proof of truth.",
            results=[result]
        )

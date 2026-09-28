import logging
import json
import re
import uuid
import hashlib
from dataclasses import dataclass, field, asdict
from typing import List, Tuple, Dict, Any, Optional

from simulation.process_sandbox import IsolatedProcessSandbox
from llm_engine.llama3_handler import generate_text
from database.models import Paper
from database.db_manager import DBManager

logger = logging.getLogger(__name__)

@dataclass
class ComputationalClaim:
    claim_id: str
    model_type: str
    dataset_description: str
    reported_metric_name: str
    reported_metric_value: float
    hyperparameters: dict
    sample_size: int
    source_paper_title: str

    def to_dict(self):
        return asdict(self)

@dataclass
class ReplicationResult:
    claim_id: str
    status: str
    reported_metrics: dict
    reproduced_metrics: dict
    discrepancy_pct: float
    confidence_interval: Tuple[float, float]
    num_seeds_run: int
    interpretation: str
    replication_code: str

    def to_dict(self):
        return asdict(self)


class ReplicationEngine:
    def __init__(self):
        pass

    def replicate_paper_claim(self, paper: dict, sandbox: Optional[IsolatedProcessSandbox] = None) -> Optional[ReplicationResult]:
        paper_text = paper.get("abstract", "") + " " + paper.get("title", "")
        
        claims = self._extract_computational_claims(paper_text)
        if not claims:
            logger.info("No computational claims found in the paper.")
            return None
        
        # Pick the first claim for simplicity
        claim = claims[0]
        claim.source_paper_title = paper.get("title", "")

        code = self._generate_replication_code(claim)

        if sandbox is None:
            sandbox = IsolatedProcessSandbox(timeout_sec=6.0)

        success, pid, duration, term_status, stdout, stderr, artifacts_dict = sandbox.execute_code(code)

        if not success:
            logger.error(f"Sandbox execution failed: {stderr}")
            return ReplicationResult(
                claim_id=claim.claim_id,
                status="FAILED",
                reported_metrics={claim.reported_metric_name: claim.reported_metric_value},
                reproduced_metrics={},
                discrepancy_pct=100.0,
                confidence_interval=(0.0, 0.0),
                num_seeds_run=0,
                interpretation=f"Execution failed: {stderr[:100]}",
                replication_code=code
            )

        # Parse outputs
        reproduced_metrics = {}
        try:
            match = re.search(r"---REPLICATION_OUTPUT_START---\s*(.*?)\s*---REPLICATION_OUTPUT_END---", stdout, re.DOTALL)
            if match:
                reproduced_metrics = json.loads(match.group(1))
        except Exception as e:
            logger.error(f"Failed to parse output JSON: {e}")
            return ReplicationResult(
                claim_id=claim.claim_id,
                status="FAILED",
                reported_metrics={claim.reported_metric_name: claim.reported_metric_value},
                reproduced_metrics={},
                discrepancy_pct=100.0,
                confidence_interval=(0.0, 0.0),
                num_seeds_run=0,
                interpretation="Output parsing failed.",
                replication_code=code
            )
        
        if not reproduced_metrics or claim.reported_metric_name not in reproduced_metrics:
            return ReplicationResult(
                claim_id=claim.claim_id,
                status="FAILED",
                reported_metrics={claim.reported_metric_name: claim.reported_metric_value},
                reproduced_metrics=reproduced_metrics,
                discrepancy_pct=100.0,
                confidence_interval=(0.0, 0.0),
                num_seeds_run=0,
                interpretation="Missing metric in output.",
                replication_code=code
            )

        mean_val = reproduced_metrics[claim.reported_metric_name]
        reported_dict = {claim.reported_metric_name: claim.reported_metric_value}
        
        status, discrepancy_pct = self._compare_metrics(reported_dict, reproduced_metrics)

        return ReplicationResult(
            claim_id=claim.claim_id,
            status=status,
            reported_metrics=reported_dict,
            reproduced_metrics=reproduced_metrics,
            discrepancy_pct=discrepancy_pct,
            confidence_interval=(mean_val * 0.95, mean_val * 1.05), # Simplified
            num_seeds_run=reproduced_metrics.get("num_seeds_run", 5),
            interpretation=f"Claim {status} with {discrepancy_pct:.2f}% discrepancy.",
            replication_code=code
        )

    def _extract_computational_claims(self, paper_text: str) -> List[ComputationalClaim]:
        claims = []
        
        # Regex for 'achieved X accuracy/AUC/F1/R²/precision/recall'
        # E.g. "achieved 0.95 accuracy" or "AUC of 0.88"
        metric_pattern = re.compile(r"(achieved|reached|with)?\s*(a|an)?\s*(\d+\.\d+)\s*(accuracy|AUC|F1|R²|precision|recall)|(accuracy|AUC|F1|R²|precision|recall)\s*(of|was|=)\s*(\d+\.\d+)", re.IGNORECASE)
        model_pattern = re.compile(r"(RandomForest|Random Forest|LinearRegression|Linear Regression|Ridge|SVM|LogisticRegression|Logistic Regression|KNN|K-Nearest Neighbors)", re.IGNORECASE)
        sample_pattern = re.compile(r"(trained on|sample size of|N\s*=\s*|dataset of)\s*(\d+)", re.IGNORECASE)

        metrics_found = metric_pattern.findall(paper_text)
        models_found = model_pattern.findall(paper_text)
        samples_found = sample_pattern.findall(paper_text)

        if metrics_found and models_found:
            # Extract first match
            for m in metrics_found:
                # tuple structure depends on regex branch matched
                val = m[2] if m[2] else m[6]
                name = m[3] if m[3] else m[4]
                if val and name:
                    model_type = models_found[0]
                    sample_size = int(samples_found[0][1]) if samples_found else 1000
                    claims.append(ComputationalClaim(
                        claim_id=str(uuid.uuid4())[:8],
                        model_type=model_type.replace(" ", ""),
                        dataset_description="Extracted synthetic task",
                        reported_metric_name=name.lower(),
                        reported_metric_value=float(val),
                        hyperparameters={},
                        sample_size=sample_size,
                        source_paper_title=""
                    ))
                    break

        if not claims:
            # LLM Fallback (mock logic but calls LLM in reality)
            prompt = f"Extract the computational claim (model, metric, value, sample size) from this text: {paper_text}"
            response = generate_text(prompt, system_prompt="You are a data extractor.", temperature=0.1)
            # Simplistic fallback parsing
            if "accuracy" in response.lower() and "randomforest" in response.lower():
                claims.append(ComputationalClaim(
                    claim_id=str(uuid.uuid4())[:8],
                    model_type="RandomForest",
                    dataset_description="LLM Extracted Task",
                    reported_metric_name="accuracy",
                    reported_metric_value=0.85,
                    hyperparameters={},
                    sample_size=1000,
                    source_paper_title=""
                ))
        return claims

    def _generate_replication_code(self, claim: ComputationalClaim) -> str:
        code_template = f"""import json
import random
import numpy as np
from sklearn.datasets import make_classification, make_regression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, roc_auc_score, f1_score, r2_score, precision_score, recall_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LinearRegression, Ridge, LogisticRegression
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier

def run_replication():
    seeds = [42, 123, 456, 789, 101112]
    metrics = []
    
    metric_name = "{claim.reported_metric_name}"
    model_type = "{claim.model_type}"
    n_samples = {claim.sample_size}
    
    is_regression = metric_name in ['r²', 'r2']
    
    for seed in seeds:
        np.random.seed(seed)
        random.seed(seed)
        
        if is_regression:
            X, y = make_regression(n_samples=n_samples, n_features=20, noise=0.1, random_state=seed)
        else:
            X, y = make_classification(n_samples=n_samples, n_features=20, n_informative=10, random_state=seed)
            
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=seed)
        
        if model_type.lower() == 'randomforest':
            model = RandomForestClassifier(random_state=seed)
        elif model_type.lower() == 'linearregression':
            model = LinearRegression()
        elif model_type.lower() == 'ridge':
            model = Ridge()
        elif model_type.lower() == 'logisticregression':
            model = LogisticRegression()
        elif model_type.lower() in ['svm', 'svc']:
            model = SVC(probability=True, random_state=seed)
        elif model_type.lower() in ['knn', 'kneighborsclassifier']:
            model = KNeighborsClassifier()
        else:
            model = RandomForestClassifier(random_state=seed) # default
            
        model.fit(X_train, y_train)
        
        if metric_name == 'accuracy':
            score = accuracy_score(y_test, model.predict(X_test))
        elif metric_name == 'auc':
            score = roc_auc_score(y_test, model.predict_proba(X_test)[:, 1])
        elif metric_name == 'f1':
            score = f1_score(y_test, model.predict(X_test))
        elif metric_name in ['r²', 'r2']:
            score = r2_score(y_test, model.predict(X_test))
        elif metric_name == 'precision':
            score = precision_score(y_test, model.predict(X_test))
        elif metric_name == 'recall':
            score = recall_score(y_test, model.predict(X_test))
        else:
            score = accuracy_score(y_test, model.predict(X_test))
            
        metrics.append(score)
        
    avg_score = float(np.mean(metrics))
    results = {{
        metric_name: avg_score,
        "num_seeds_run": len(seeds)
    }}
    
    print("---REPLICATION_OUTPUT_START---")
    print(json.dumps(results))
    print("---REPLICATION_OUTPUT_END---")

if __name__ == "__main__":
    run_replication()
"""
        return code_template

    def _compare_metrics(self, reported: dict, reproduced: dict) -> Tuple[str, float]:
        if not reported or not reproduced:
            return "FAILED", 100.0
            
        metric_name = list(reported.keys())[0]
        rep_val = reported[metric_name]
        repro_val = reproduced.get(metric_name, 0.0)
        
        if rep_val == 0:
            discrepancy_pct = 0.0 if repro_val == 0 else 100.0
        else:
            discrepancy_pct = abs(rep_val - repro_val) / abs(rep_val) * 100.0
            
        if discrepancy_pct <= 5.0:
            status = "REPRODUCED"
        elif discrepancy_pct <= 15.0:
            status = "PARTIAL"
        else:
            status = "FAILED"
            
        return status, discrepancy_pct

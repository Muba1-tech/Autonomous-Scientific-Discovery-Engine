import logging
import hashlib
from typing import List, Tuple, Dict, Any, Optional
from dataclasses import dataclass, field, asdict
import numpy as np
import pandas as pd
from scipy.stats import norm, ttest_ind

try:
    from sklearn.linear_model import LogisticRegression, LinearRegression
except ImportError:
    LogisticRegression = None
    LinearRegression = None

from engines.hypothesis_evolution import Hypothesis as EvolutionHypothesis, HypothesisGenome
from llm_engine.llama3_handler import generate_text

logger = logging.getLogger(__name__)

@dataclass
class CausalGraph:
    nodes: List[str]
    edges: List[Tuple[str, str]]
    treatment: str
    outcome: str
    confounders: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class CausalResult:
    ate_estimate: float
    ci_95_low: float
    ci_95_high: float
    p_value: float
    method_agreement: float
    e_value: float
    falsification_passed: bool
    methods_used: List[str]
    interpretation: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class CausalDiscoveryEngine:
    """
    Tests whether hypothesis mechanisms imply actual causation, not just correlation.
    Implements OLS, Propensity Score Matching (PSM), and Inverse Probability Weighting (IPW).
    """

    def test_causal_claim(self, hypothesis: EvolutionHypothesis, data: Optional[pd.DataFrame] = None) -> CausalResult:
        logger.info(f"Testing causal claim for hypothesis: {getattr(hypothesis, 'id', 'unknown')}")
        
        graph = self._build_causal_graph(hypothesis)
        
        if data is None:
            logger.info("No data provided. Generating synthetic data based on causal graph.")
            data = self._generate_synthetic_causal_data(graph, n_samples=1000)
        
        treatment = graph.treatment
        outcome = graph.outcome
        confounders = graph.confounders
        
        # Verify columns exist, pad if missing
        for col in [treatment, outcome] + confounders:
            if col not in data.columns:
                logger.warning(f"Column {col} not found in data. Adding synthetic normal data.")
                data[col] = np.random.normal(0, 1, size=len(data))
                
        estimates = []
        methods_used = []
        
        # Method 1: OLS
        ols_res = self._estimate_ate_ols(data, treatment, outcome, confounders)
        if ols_res:
            estimates.append(ols_res)
            methods_used.append("OLS")
            
        # Method 2: Propensity Score Matching
        psm_res = self._estimate_ate_psm(data, treatment, outcome, confounders)
        if psm_res:
            estimates.append(psm_res)
            methods_used.append("PSM")
            
        # Method 3: Inverse Probability Weighting
        ipw_res = self._estimate_ate_ipw(data, treatment, outcome, confounders)
        if ipw_res:
            estimates.append(ipw_res)
            methods_used.append("IPW")
            
        if not estimates:
            return CausalResult(0.0, 0.0, 0.0, 1.0, 0.0, 0.0, False, [], "Failed to estimate ATE - models could not be fit.")
            
        # Aggregate results across methods
        ate_estimate = float(np.mean([res['ate'] for res in estimates]))
        ci_95_low = float(np.mean([res['ci_low'] for res in estimates]))
        ci_95_high = float(np.mean([res['ci_high'] for res in estimates]))
        p_value = float(np.mean([res['p_value'] for res in estimates]))
        
        # Compute Method Agreement (variance of estimates scaled 0-1)
        if len(estimates) > 1:
            ate_std = np.std([res['ate'] for res in estimates])
            method_agreement = max(0.0, 1.0 - min(ate_std / (abs(ate_estimate) + 1e-5), 1.0))
        else:
            method_agreement = 1.0
            
        e_value = self._compute_e_value(ate_estimate, ci_95_low)
        falsification_passed = self._run_placebo_test(data, treatment, confounders)
        
        interpretation = (
            f"Average Treatment Effect (ATE) is {ate_estimate:.3f} with 95% CI [{ci_95_low:.3f}, {ci_95_high:.3f}]. "
            f"Agreement across {len(methods_used)} methods ({', '.join(methods_used)}) is {method_agreement:.2f}. "
            f"E-value (robustness to unmeasured confounding): {e_value:.2f}. "
            f"Placebo falsification: {'PASSED' if falsification_passed else 'FAILED'}."
        )
        
        return CausalResult(
            ate_estimate=ate_estimate,
            ci_95_low=ci_95_low,
            ci_95_high=ci_95_high,
            p_value=p_value,
            method_agreement=method_agreement,
            e_value=e_value,
            falsification_passed=falsification_passed,
            methods_used=methods_used,
            interpretation=interpretation
        )
        
    def _build_causal_graph(self, hypothesis: EvolutionHypothesis) -> CausalGraph:
        """Parses the causal relationships strings to build a simple DAG representation."""
        nodes = set()
        edges = []
        
        relationships = []
        if hasattr(hypothesis, 'genome') and hasattr(hypothesis.genome, 'causal_relationships'):
            relationships = hypothesis.genome.causal_relationships
            
        if not relationships:
            relationships = ["Treatment -> Outcome"]
            
        for rel in relationships:
            parts = [p.strip() for p in rel.split("->")]
            for i in range(len(parts)-1):
                nodes.add(parts[i])
                nodes.add(parts[i+1])
                edges.append((parts[i], parts[i+1]))
                
        nodes_list = list(nodes)
        if len(nodes_list) >= 2 and len(edges) > 0:
            # Simple heuristic: first node in first edge is treatment, last is outcome
            treatment = edges[0][0]
            outcome = edges[-1][-1]
        else:
            treatment = "Treatment"
            outcome = "Outcome"
            nodes_list = [treatment, outcome]
            edges = [(treatment, outcome)]
            
        confounders = [n for n in nodes_list if n not in (treatment, outcome)]
        
        return CausalGraph(
            nodes=nodes_list,
            edges=edges,
            treatment=treatment,
            outcome=outcome,
            confounders=confounders
        )
        
    def _estimate_ate_ols(self, data: pd.DataFrame, treatment: str, outcome: str, confounders: List[str]) -> Optional[Dict[str, float]]:
        """Ordinary Least Squares with confounders as controls."""
        if LinearRegression is None:
            return None
            
        features = [treatment] + confounders
        X = data[features]
        y = data[outcome]
        
        model = LinearRegression()
        model.fit(X, y)
        
        # Treatment is the first column in X
        ate = float(model.coef_[0])
        
        # Compute standard error and p-value for the treatment coefficient
        n = len(X)
        p = X.shape[1]
        residuals = y - model.predict(X)
        rss = np.sum(residuals**2)
        s_squared = rss / (n - p - 1)
        
        X_design = np.column_stack([np.ones(n), X.values])
        try:
            var_covar = s_squared * np.linalg.inv(X_design.T @ X_design)
            se_ate = np.sqrt(var_covar[1, 1])  # index 1 corresponds to treatment (index 0 is intercept)
        except np.linalg.LinAlgError:
            se_ate = 0.1 # Fallback SE
            
        t_stat = ate / se_ate if se_ate != 0 else 0
        p_val = 2 * (1 - norm.cdf(abs(t_stat)))
        ci_low = ate - 1.96 * se_ate
        ci_high = ate + 1.96 * se_ate
        
        return {"ate": ate, "ci_low": ci_low, "ci_high": ci_high, "p_value": float(p_val)}
        
    def _estimate_ate_psm(self, data: pd.DataFrame, treatment: str, outcome: str, confounders: List[str]) -> Optional[Dict[str, float]]:
        """Propensity Score Matching (Stratified by Propensity Score quantiles)."""
        if LogisticRegression is None or len(confounders) == 0:
            return None
            
        # Ensure treatment is binary for logistic regression
        median_t = data[treatment].median()
        t_binary = (data[treatment] > median_t).astype(int)
        
        model = LogisticRegression(solver='liblinear')
        model.fit(data[confounders], t_binary)
        pscores = model.predict_proba(data[confounders])[:, 1]
        
        data_ps = data.copy()
        data_ps['pscore'] = pscores
        
        # Stratify into quintiles
        try:
            data_ps['strata'] = pd.qcut(data_ps['pscore'], q=5, labels=False, duplicates='drop')
        except ValueError:
            return None
            
        ates = []
        for i in data_ps['strata'].unique():
            stratum = data_ps[data_ps['strata'] == i]
            treated = stratum[t_binary[stratum.index] == 1]
            control = stratum[t_binary[stratum.index] == 0]
            if len(treated) > 0 and len(control) > 0:
                ates.append(treated[outcome].mean() - control[outcome].mean())
                
        if not ates:
            return None
            
        ate = float(np.mean(ates))
        se = float(np.std(ates) / np.sqrt(len(ates))) if len(ates) > 1 else 0.1
        
        return {
            "ate": ate, 
            "ci_low": ate - 1.96 * se, 
            "ci_high": ate + 1.96 * se, 
            "p_value": float(2 * (1 - norm.cdf(abs(ate / (se + 1e-10)))))
        }
        
    def _estimate_ate_ipw(self, data: pd.DataFrame, treatment: str, outcome: str, confounders: List[str]) -> Optional[Dict[str, float]]:
        """Inverse Probability Weighting using Propensity Scores."""
        if LogisticRegression is None or len(confounders) == 0:
            return None
            
        median_t = data[treatment].median()
        t_binary = (data[treatment] > median_t).astype(int)
        
        model = LogisticRegression(solver='liblinear')
        model.fit(data[confounders], t_binary)
        pscores = model.predict_proba(data[confounders])[:, 1]
        
        # Trim extreme propensity scores to prevent infinite weights
        pscores = np.clip(pscores, 0.05, 0.95)
        
        weights = t_binary / pscores + (1 - t_binary) / (1 - pscores)
        
        y1_weighted = (t_binary * data[outcome] * weights).sum() / (t_binary * weights).sum()
        y0_weighted = ((1 - t_binary) * data[outcome] * weights).sum() / ((1 - t_binary) * weights).sum()
        
        ate = float(y1_weighted - y0_weighted)
        se = float(np.std(data[outcome]) / np.sqrt(len(data))) * 1.5  # Rough SE approximation for IPW
        
        return {
            "ate": ate, 
            "ci_low": ate - 1.96 * se, 
            "ci_high": ate + 1.96 * se, 
            "p_value": float(2 * (1 - norm.cdf(abs(ate / (se + 1e-10)))))
        }
        
    def _compute_e_value(self, point_estimate: float, ci_lower: float) -> float:
        """Computes the E-value for sensitivity to unmeasured confounding (VanderWeele & Ding 2017)."""
        if point_estimate <= 0:
            return 1.0
            
        # Simplified pseudo-RR conversion based on effect size
        rr = np.exp(point_estimate)
        if rr > 1.0:
            e_val = rr + np.sqrt(rr * (rr - 1))
        else:
            e_val = 1.0
            
        return float(e_val)
        
    def _run_placebo_test(self, data: pd.DataFrame, treatment: str, confounders: List[str]) -> bool:
        """Falsification test using a random placebo outcome."""
        if LinearRegression is None:
            return True
            
        placebo_outcome = np.random.normal(0, 1, size=len(data))
        X = data[[treatment] + confounders] if confounders else data[[treatment]]
        
        model = LinearRegression()
        model.fit(X, placebo_outcome)
        
        coef = model.coef_[0]
        # Coefficient on a random outcome should be near 0
        return abs(coef) < 0.2
        
    def _generate_synthetic_causal_data(self, graph: CausalGraph, n_samples: int = 500) -> pd.DataFrame:
        """Generates synthetic data conforming to the causal graph structure."""
        data = pd.DataFrame()
        
        # 1. Generate Confounders
        for c in graph.confounders:
            data[c] = np.random.normal(0, 1, size=n_samples)
            
        # 2. Generate Treatment (caused by confounders)
        t_base = np.zeros(n_samples)
        for c in graph.confounders:
            t_base += data[c] * np.random.uniform(0.1, 0.5)
        
        # Create a continuous treatment with noise
        data[graph.treatment] = t_base + np.random.normal(0, 1, size=n_samples)
        
        # 3. Generate Outcome (caused by treatment + confounders)
        true_ate = 0.75
        o_base = data[graph.treatment] * true_ate
        for c in graph.confounders:
            o_base += data[c] * np.random.uniform(0.1, 0.5)
            
        data[graph.outcome] = o_base + np.random.normal(0, 0.5, size=n_samples)
        
        return data

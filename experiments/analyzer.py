import numpy as np
import scipy.stats as stats
from typing import Tuple, List
from dataclasses import dataclass
from enum import Enum

class ResultOrigin(Enum):
    SIMULATION = "simulation"
    PHYSICAL_EMPIRICAL = "physical_empirical"

@dataclass
class StatisticalResult:
    p_value: float
    effect_size_cohens_d: float
    confidence_interval: Tuple[float, float]
    is_significant: bool
    origin: ResultOrigin

class ExperimentAnalyzer:
    """Analyzes experiment results, calculating statistics and effect sizes."""
    
    def __init__(self, alpha: float = 0.05):
        self.alpha = alpha
        
    def analyze_two_groups(
        self, 
        control_group: List[float], 
        treatment_group: List[float], 
        origin: ResultOrigin = ResultOrigin.SIMULATION
    ) -> StatisticalResult:
        """Performs statistical analysis between two groups."""
        
        ctrl = np.array(control_group)
        trt = np.array(treatment_group)
        
        t_stat, p_value = stats.ttest_ind(ctrl, trt, equal_var=False)
        
        nx, ny = len(ctrl), len(trt)
        dof = nx + ny - 2
        
        var_ctrl = np.var(ctrl, ddof=1) if nx > 1 else 0
        var_trt = np.var(trt, ddof=1) if ny > 1 else 0
        
        pool_sd = np.sqrt(((nx - 1) * var_ctrl + (ny - 1) * var_trt) / dof) if dof > 0 else 0.0
        cohens_d = (np.mean(trt) - np.mean(ctrl)) / pool_sd if pool_sd > 0 else 0.0
        
        diff_mean = np.mean(trt) - np.mean(ctrl)
        se = np.sqrt(var_ctrl/nx + var_trt/ny) if nx > 0 and ny > 0 else 0.0
        
        if se > 0 and dof > 0:
            ci_low, ci_high = stats.t.interval(1 - self.alpha, dof, loc=diff_mean, scale=se)
        else:
            ci_low, ci_high = (diff_mean, diff_mean)
        
        return StatisticalResult(
            p_value=float(p_value) if not np.isnan(p_value) else 1.0,
            effect_size_cohens_d=float(cohens_d),
            confidence_interval=(float(ci_low), float(ci_high)),
            is_significant=(p_value < self.alpha) if not np.isnan(p_value) else False,
            origin=origin
        )
        
    def interpret_results(self, result: StatisticalResult) -> str:
        """Provides a textual interpretation of the statistical results."""
        interpretation = (
            f"The results are derived from {result.origin.value.replace('_', ' ')}. "
            f"The difference between groups is {'statistically significant' if result.is_significant else 'not statistically significant'} "
            f"(p = {result.p_value:.4f}). "
            f"The effect size (Cohen's d) is {result.effect_size_cohens_d:.2f}. "
            f"The 95% confidence interval for the difference in means is {result.confidence_interval}."
        )
        
        if result.origin == ResultOrigin.SIMULATION:
            interpretation += " Note: These are simulated results and must be validated empirically in physical reality."
            
        return interpretation

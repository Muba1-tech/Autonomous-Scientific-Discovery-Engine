import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from dataclasses import dataclass
import warnings

@dataclass
class Hypothesis:
    statement: str
    target_variable: str
    predictors: List[str]
    rationale: str

@dataclass
class DatasetProfile:
    missing_values: Dict[str, float]
    outliers: Dict[str, int]
    distributions: Dict[str, Dict[str, float]]
    correlations: Dict[str, Dict[str, float]]
    feature_importance: Dict[str, float]
    hypotheses: List[Hypothesis]
    epistemological_warnings: List[str]

class DatasetScientist:
    """Analyzes datasets and formulates hypotheses while strictly adhering to scientific epistemology."""
    
    def __init__(self):
        self.standard_warnings = [
            "CORRELATION does not imply CAUSATION. Observed relationships are merely statistical.",
            "ASSOCIATION implies variables change together, but does not identify a mechanism.",
            "CAUSATION requires rigorous experimental design, intervention, or robust causal inference methods.",
            "HYPOTHESIS is a testable proposed explanation, not a proven fact."
        ]

    def ingest(self, file_path: str) -> pd.DataFrame:
        """Ingests datasets of various formats."""
        if file_path.endswith('.csv'):
            return pd.read_csv(file_path)
        elif file_path.endswith(('.xls', '.xlsx')):
            return pd.read_excel(file_path)
        elif file_path.endswith('.json'):
            return pd.read_json(file_path)
        elif file_path.endswith('.parquet'):
            return pd.read_parquet(file_path)
        else:
            raise ValueError("Unsupported file format. Use CSV, Excel, JSON, or Parquet.")

    def profile(self, df: pd.DataFrame, target_col: Optional[str] = None) -> DatasetProfile:
        """Automated profiling of the dataset."""
        df_numeric = df.select_dtypes(include=[np.number])
        
        missing = (df.isnull().sum() / len(df)).to_dict()
        
        outliers = {}
        for col in df_numeric.columns:
            Q1 = df_numeric[col].quantile(0.25)
            Q3 = df_numeric[col].quantile(0.75)
            IQR = Q3 - Q1
            outlier_count = ((df_numeric[col] < (Q1 - 1.5 * IQR)) | (df_numeric[col] > (Q3 + 1.5 * IQR))).sum()
            outliers[col] = int(outlier_count)
            
        distributions = {}
        for col in df_numeric.columns:
            distributions[col] = {
                "mean": float(df_numeric[col].mean()) if not pd.isna(df_numeric[col].mean()) else 0.0,
                "std": float(df_numeric[col].std()) if not pd.isna(df_numeric[col].std()) else 0.0,
                "skew": float(df_numeric[col].skew()) if not pd.isna(df_numeric[col].skew()) else 0.0
            }
            
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            corr_matrix = df_numeric.corr().to_dict()
            
        feature_importance = {}
        if target_col and target_col in df_numeric.columns:
            corr_with_target = df_numeric.corr()[target_col].abs().sort_values(ascending=False)
            feature_importance = corr_with_target.drop(target_col, errors='ignore').to_dict()
            
        hypotheses = self._suggest_hypotheses(corr_matrix, target_col)
        
        return DatasetProfile(
            missing_values=missing,
            outliers=outliers,
            distributions=distributions,
            correlations=corr_matrix,
            feature_importance=feature_importance,
            hypotheses=hypotheses,
            epistemological_warnings=self.standard_warnings
        )
        
    def _suggest_hypotheses(self, corr_matrix: Dict[str, Dict[str, float]], target_col: Optional[str] = None) -> List[Hypothesis]:
        """Suggests testable candidate hypotheses grounded in data patterns."""
        hypotheses = []
        
        if target_col and target_col in corr_matrix:
            for feature, corr_value in corr_matrix[target_col].items():
                if feature != target_col and not pd.isna(corr_value) and abs(corr_value) > 0.5:
                    direction = "increases" if corr_value > 0 else "decreases"
                    hypotheses.append(
                        Hypothesis(
                            statement=f"An increase in {feature} is associated with a {direction} in {target_col}.",
                            target_variable=target_col,
                            predictors=[feature],
                            rationale=f"Observed strong statistical correlation (r={corr_value:.2f}). Needs experimental validation to establish causation."
                        )
                    )
        
        return hypotheses

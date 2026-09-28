"""Dataset Scientist Agent for AION X.
Automates dataset profiling, distribution analysis, correlation mining, and data-driven hypothesis generation.
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
import os


class DatasetScientist:
    """Specialized agent for empirical dataset exploration and statistical profiling."""

    def __init__(self, name: str = "DatasetScientist"):
        self.name = name

    def profile_dataset(self, dataset_path: str) -> Dict[str, Any]:
        """Generate high-level profile of dataset shape, columns, and types."""
        df = self._load_dataframe(dataset_path)
        return {
            "num_rows": len(df),
            "num_columns": len(df.columns),
            "columns": list(df.columns),
            "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
            "missing_values": df.isnull().sum().to_dict()
        }

    def analyze_distributions(self, dataset_path: str) -> Dict[str, Dict[str, float]]:
        """Compute statistical distributions (mean, std, min, max, quartiles) for numeric columns."""
        df = self._load_dataframe(dataset_path)
        numeric_df = df.select_dtypes(include=[np.number])
        distributions = {}
        for col in numeric_df.columns:
            distributions[col] = {
                "mean": float(numeric_df[col].mean()),
                "std": float(numeric_df[col].std()) if len(numeric_df) > 1 else 0.0,
                "min": float(numeric_df[col].min()),
                "max": float(numeric_df[col].max()),
                "median": float(numeric_df[col].median()),
                "skew": float(numeric_df[col].skew()) if len(numeric_df) > 2 else 0.0
            }
        return distributions

    def calculate_correlations(self, dataset_path: str) -> Dict[str, Dict[str, float]]:
        """Compute Pearson correlation matrix for numeric columns."""
        df = self._load_dataframe(dataset_path)
        numeric_df = df.select_dtypes(include=[np.number])
        if numeric_df.empty or len(numeric_df.columns) < 2:
            return {}
        corr_matrix = numeric_df.corr().to_dict()
        return {col1: {col2: float(val) for col2, val in row.items()} for col1, row in corr_matrix.items()}

    def generate_hypotheses(self, dataset_path: str) -> List[str]:
        """Formulate testable scientific hypotheses derived from empirical correlations and anomalies."""
        correlations = self.calculate_correlations(dataset_path)
        distributions = self.analyze_distributions(dataset_path)
        hypotheses = []

        seen_pairs = set()
        for col1, targets in correlations.items():
            for col2, r_val in targets.items():
                if col1 == col2:
                    continue
                pair_key = tuple(sorted([col1, col2]))
                if pair_key in seen_pairs:
                    continue
                seen_pairs.add(pair_key)

                if abs(r_val) >= 0.5:
                    direction = "positive" if r_val > 0 else "negative (inverse)"
                    hypotheses.append(
                        f"There is a strong {direction} correlation (r={r_val:.2f}) between {col1} and {col2}, suggesting a potential causal coupling or shared regulator."
                    )
                elif abs(r_val) < 0.1:
                    hypotheses.append(
                        f"Variables {col1} and {col2} exhibit orthogonality (r={r_val:.2f}), indicating independent mechanistic pathways."
                    )

        if not hypotheses:
            hypotheses.append("Dataset features demonstrate mild linear correlation across baseline distributions.")

        return hypotheses

    def _load_dataframe(self, dataset_path: str) -> pd.DataFrame:
        if not os.path.exists(dataset_path):
            raise FileNotFoundError(f"Dataset path does not exist: {dataset_path}")
        if dataset_path.endswith(".csv"):
            return pd.read_csv(dataset_path)
        elif dataset_path.endswith(".parquet"):
            return pd.read_parquet(dataset_path)
        elif dataset_path.endswith(".json"):
            return pd.read_json(dataset_path)
        else:
            return pd.read_csv(dataset_path)

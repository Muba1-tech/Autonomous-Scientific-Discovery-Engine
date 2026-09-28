import json
import base64
from typing import Dict, Any, Optional
from dataclasses import dataclass
from .sandbox import ExperimentSandbox, SandboxResult

@dataclass
class ExperimentResult:
    metrics: Dict[str, Any]
    logs: str
    plots: Dict[str, str]
    reproducibility_metadata: Dict[str, Any]
    success: bool
    error: Optional[str]

class ExperimentRunner:
    """Runs experiments by converting specifications to code and executing in sandbox."""
    
    def __init__(self, sandbox: Optional[ExperimentSandbox] = None):
        self.sandbox = sandbox or ExperimentSandbox()

    def generate_code(self, design_spec: Dict[str, Any]) -> str:
        """Converts an experimental design specification into executable Python code."""
        if "code" in design_spec:
            return design_spec["code"]
        
        code_lines = [
            "import pandas as pd",
            "import numpy as np",
            "import matplotlib.pyplot as plt",
            "import json",
            "",
            f"def run_experiment():",
            f"    np.random.seed({design_spec.get('seed', 42)})",
            "    metrics = {'status': 'completed'}",
            "    with open('metrics.json', 'w') as f:",
            "        json.dump(metrics, f)",
            "",
            "if __name__ == '__main__':",
            "    run_experiment()"
        ]
        
        return "\n".join(code_lines)

    def run(self, design_spec: Dict[str, Any]) -> ExperimentResult:
        """Runs the experiment and formats the output."""
        code = self.generate_code(design_spec)
        
        sandbox_result = self.sandbox.execute(code)
        
        metrics = {}
        plots = {}
        
        if sandbox_result.success:
            for name, data in sandbox_result.artifacts.items():
                if name.endswith('.json') and 'metrics' in name:
                    try:
                        metrics.update(json.loads(data.decode('utf-8')))
                    except json.JSONDecodeError:
                        pass
                elif name.endswith('.png') or name.endswith('.jpg'):
                    plots[name] = base64.b64encode(data).decode('utf-8')
                    
        metadata = {
            "execution_time_sec": sandbox_result.execution_time_sec,
            "design_spec": design_spec
        }
        
        return ExperimentResult(
            metrics=metrics,
            logs=sandbox_result.stdout + "\n" + sandbox_result.stderr,
            plots=plots,
            reproducibility_metadata=metadata,
            success=sandbox_result.success,
            error=sandbox_result.error_message
        )

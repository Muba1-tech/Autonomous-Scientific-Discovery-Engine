import os
import sys
import tempfile
import subprocess
import time
from typing import Dict, Optional
from dataclasses import dataclass

@dataclass
class SandboxResult:
    success: bool
    stdout: str
    stderr: str
    execution_time_sec: float
    artifacts: Dict[str, bytes]
    error_message: Optional[str] = None

class ExperimentSandbox:
    """Executes generated Python experiment code in an isolated subprocess."""

    ALLOWED_MODULES = {"numpy", "scipy", "pandas", "sklearn", "matplotlib", "math", "random", "typing", "json"}

    def __init__(self, timeout_sec: int = 60, memory_limit_mb: int = 512):
        self.timeout_sec = timeout_sec
        self.memory_limit_mb = memory_limit_mb

    def execute(self, code: str) -> SandboxResult:
        self._check_code_safety(code)

        start_time = time.time()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            script_path = os.path.join(temp_dir, "experiment.py")
            with open(script_path, "w") as f:
                f.write(code)
            
            try:
                process = subprocess.Popen(
                    [sys.executable, script_path],
                    cwd=temp_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                stdout, stderr = process.communicate(timeout=self.timeout_sec)
                success = process.returncode == 0
                error_message = None if success else f"Process exited with code {process.returncode}"
                
            except subprocess.TimeoutExpired as e:
                process.kill()
                stdout = e.stdout.decode('utf-8') if e.stdout else ""
                stderr = e.stderr.decode('utf-8') if e.stderr else ""
                success = False
                error_message = f"Execution timed out after {self.timeout_sec} seconds"
            except Exception as e:
                stdout = ""
                stderr = str(e)
                success = False
                error_message = f"Execution failed: {e}"
                
            execution_time = time.time() - start_time
            
            artifacts = {}
            for root, _, files in os.walk(temp_dir):
                for file in files:
                    if file == "experiment.py":
                        continue
                    if file.endswith((".csv", ".png", ".jpg", ".txt", ".json")):
                        file_path = os.path.join(root, file)
                        with open(file_path, "rb") as f:
                            rel_path = os.path.relpath(file_path, temp_dir)
                            artifacts[rel_path] = f.read()

            return SandboxResult(
                success=success,
                stdout=stdout,
                stderr=stderr,
                execution_time_sec=execution_time,
                artifacts=artifacts,
                error_message=error_message
            )

    def _check_code_safety(self, code: str) -> None:
        """Performs simple static checks to prevent obvious malicious operations."""
        import ast
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            raise ValueError(f"Syntax error in experiment code: {e}")

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    base_module = alias.name.split('.')[0]
                    if base_module not in self.ALLOWED_MODULES:
                        raise ValueError(f"Importing unauthorized module: {base_module}")
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    base_module = node.module.split('.')[0]
                    if base_module not in self.ALLOWED_MODULES:
                        raise ValueError(f"Importing unauthorized module: {base_module}")
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in {"eval", "exec", "open", "system", "popen"}:
                        raise ValueError(f"Unauthorized function call: {node.func.id}")

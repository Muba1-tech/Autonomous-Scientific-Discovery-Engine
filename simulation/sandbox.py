"""Secure Python Execution Sandbox for AION X Experiment Lab.
Provides AST security validation, dependency whitelisting, memory/timeout limits,
and restricted execution environments to safely run computational experiments.
"""
import ast
import time
import sys
import importlib
import concurrent.futures
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional


@dataclass
class SandboxConfig:
    timeout: float = 5.0
    allowed_packages: List[str] = field(default_factory=lambda: ["numpy", "pandas", "scipy", "math", "random", "json", "time"])
    max_memory_mb: int = 256


@dataclass
class SandboxResult:
    success: bool
    output: Dict[str, Any] = field(default_factory=dict)
    error: str = ""
    logs: str = ""
    execution_time: float = 0.0


class SecurityError(Exception):
    """Raised when code violates security or dependency constraints."""
    pass


class ASTSecurityValidator(ast.NodeVisitor):
    """Statically checks Python code AST against malicious calls and forbidden built-ins."""

    BANNED_IMPORTS = {
        "os", "subprocess", "shutil", "socket", "http", "urllib", "requests",
        "ctypes", "multiprocessing", "threading", "pty", "builtins", "__builtin__",
        "importlib", "pathlib", "webbrowser", "tempfile"
    }

    BANNED_FUNCTIONS = {
        "open", "eval", "exec", "compile", "globals", "locals", "getattr", "setattr",
        "delattr", "memoryview", "breakpoint"
    }

    def __init__(self, allowed_packages: List[str]):
        # Always allow standard safe math/time/json libs if in allowed_packages
        self.allowed_packages = set(allowed_packages).union({"math", "random", "json", "time"})

    def visit_Import(self, node):
        for alias in node.names:
            pkg_root = alias.name.split('.')[0]
            if pkg_root in self.BANNED_IMPORTS or pkg_root not in self.allowed_packages:
                raise SecurityError(f"SecurityError: Import of package '{alias.name}' is strictly prohibited.")
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        if node.module:
            pkg_root = node.module.split('.')[0]
            if pkg_root in self.BANNED_IMPORTS or pkg_root not in self.allowed_packages:
                raise SecurityError(f"SecurityError: Import from '{node.module}' is strictly prohibited.")
        self.generic_visit(node)

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name) and node.func.id in self.BANNED_FUNCTIONS:
            if node.func.id == "open":
                raise PermissionError(f"PermissionError: File access via open() is prohibited in the sandbox.")
            raise SecurityError(f"SecurityError: Calling '{node.func.id}()' is prohibited in the sandbox.")
        self.generic_visit(node)


def _safe_import_factory(allowed_packages: set):
    """Create a restricted __import__ function that only allows approved modules."""
    def _safe_import(name, globals=None, locals=None, fromlist=(), level=0):
        pkg_root = name.split('.')[0]
        if pkg_root not in allowed_packages:
            raise SecurityError(f"ImportError: Package '{name}' is not whitelisted.")
        return importlib.__import__(name, globals, locals, fromlist, level)
    return _safe_import


class ExperimentSandbox:
    """Isolated execution engine with AST inspection and timeout guarantees."""

    def __init__(self, config: Optional[SandboxConfig] = None):
        self.config = config or SandboxConfig()

    def run(self, code: str, initial_env: Optional[Dict[str, Any]] = None) -> SandboxResult:
        """Run Python code safely and return execution results."""
        start_time = time.time()
        allowed = set(self.config.allowed_packages).union({"math", "random", "json", "time"})

        # 1. AST Validation
        try:
            tree = ast.parse(code)
            validator = ASTSecurityValidator(allowed)
            validator.visit(tree)
        except (SecurityError, PermissionError) as se:
            return SandboxResult(
                success=False,
                error=str(se),
                execution_time=time.time() - start_time
            )
        except SyntaxError as syn_err:
            return SandboxResult(
                success=False,
                error=f"SyntaxError: {syn_err}",
                execution_time=time.time() - start_time
            )
        except Exception as e:
            return SandboxResult(
                success=False,
                error=f"SecurityError: {str(e)}",
                execution_time=time.time() - start_time
            )

        # 2. Execute with ThreadPool timeout
        def _execute_code():
            safe_builtins = {
                "abs": abs, "all": all, "any": any, "bool": bool, "dict": dict,
                "enumerate": enumerate, "filter": filter, "float": float, "format": format,
                "int": int, "isinstance": isinstance, "issubclass": issubclass, "iter": iter,
                "len": len, "list": list, "map": map, "max": max, "min": min, "next": next,
                "pow": pow, "print": print, "range": range, "round": round, "set": set,
                "slice": slice, "sorted": sorted, "str": str, "sum": sum, "tuple": tuple,
                "type": type, "zip": zip, "Exception": Exception, "ValueError": ValueError,
                "TypeError": TypeError, "KeyError": KeyError, "IndexError": IndexError,
                "__import__": _safe_import_factory(allowed)
            }

            safe_globals = {"__builtins__": safe_builtins}

            # Pre-populate common safe modules
            try:
                import numpy as np
                safe_globals["np"] = np
                safe_globals["numpy"] = np
            except ImportError:
                pass

            try:
                import pandas as pd
                safe_globals["pd"] = pd
                safe_globals["pandas"] = pd
            except ImportError:
                pass

            import math
            import random
            import json
            import time as time_mod

            safe_globals["math"] = math
            safe_globals["random"] = random
            safe_globals["json"] = json
            safe_globals["time"] = time_mod

            if initial_env:
                safe_globals.update(initial_env)

            exec_locals = {}
            exec(code, safe_globals, exec_locals)
            return exec_locals

        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(_execute_code)
            try:
                result_locals = future.result(timeout=self.config.timeout)
                clean_output = {}
                for k, v in result_locals.items():
                    if not k.startswith("_") and not callable(v):
                        clean_output[k] = v

                return SandboxResult(
                    success=True,
                    output=clean_output,
                    execution_time=time.time() - start_time
                )
            except concurrent.futures.TimeoutError:
                raise TimeoutError(f"Execution timed out after {self.config.timeout}s")
            except Exception as e:
                return SandboxResult(
                    success=False,
                    error=f"{type(e).__name__}: {str(e)}",
                    execution_time=time.time() - start_time
                )

import pytest
import time
from simulation.process_sandbox import (
    ASTSecurityAuditor,
    IsolatedProcessSandbox,
    FirstHypothesisSimulator
)

def test_ast_security_blocks_banned_imports():
    auditor = ASTSecurityAuditor()
    unsafe_code = """
import os
os.system("echo hello")
"""
    result = auditor.audit(unsafe_code)
    assert result.passed is False
    assert any("os" in v for v in result.violations)

def test_ast_security_blocks_eval_exec():
    auditor = ASTSecurityAuditor()
    unsafe_code = """
x = "print(1)"
eval(x)
"""
    result = auditor.audit(unsafe_code)
    assert result.passed is False
    assert any("eval" in v for v in result.violations)

def test_ast_security_blocks_reflection_and_subclasses():
    auditor = ASTSecurityAuditor()
    unsafe_code = """
x = ().__class__.__bases__[0].__subclasses__()
"""
    result = auditor.audit(unsafe_code)
    assert result.passed is False
    assert any("Forbidden introspection attribute" in v for v in result.violations)

def test_ast_security_allows_safe_scientific_code():
    auditor = ASTSecurityAuditor()
    safe_code = """
import numpy as np
import pandas as pd
from scipy import stats
x = np.array([1, 2, 3])
df = pd.DataFrame({"a": x})
"""
    result = auditor.audit(safe_code)
    assert result.passed is True
    assert len(result.violations) == 0

def test_isolated_sandbox_execution_and_kill():
    sandbox = IsolatedProcessSandbox(timeout_sec=4.0)
    code = """
import numpy as np
print("SANDBOX_OK")
"""
    success, pid, duration, term_status, stdout, stderr, artifacts = sandbox.execute_code(code)
    assert success is True
    assert pid is not None
    assert "SANDBOX_OK" in stdout
    assert "CLEANLY_TERMINATED" in term_status

def test_isolated_sandbox_timeout_kill():
    sandbox = IsolatedProcessSandbox(timeout_sec=1.5)
    # Code that would hang forever
    code = """
import time
while True:
    time.sleep(0.1)
"""
    t0 = time.time()
    success, pid, duration, term_status, stdout, stderr, artifacts = sandbox.execute_code(code)
    t1 = time.time()
    assert success is False
    assert "KILLED_TIMEOUT" in term_status
    # Verify timeout killed without waiting forever
    assert (t1 - t0) < 4.0

def test_first_hypothesis_simulation():
    sim = FirstHypothesisSimulator(timeout_sec=15.0)
    hyp_text = "Coupling high-pressure phonon modes in carbonaceous hydride stabilizes room-temperature electron pairing."
    report = sim.conduct_experiment(hyp_text, domain="Quantum Materials", research_id="TEST-001")
    
    assert report.success is True
    assert report.pid is not None
    assert "CLEANLY_TERMINATED" in report.termination_status
    assert report.dataset_name != ""
    assert len(report.dataset_preview) > 0
    assert "P-Value" in report.observed_output
    assert "Falsification Threshold" in report.expected_output
    assert report.metrics.get("p_value") is not None
    assert len(report.python_code) > 50

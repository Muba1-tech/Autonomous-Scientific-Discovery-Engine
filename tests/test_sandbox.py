import pytest
from simulation.sandbox import ExperimentSandbox, SandboxConfig

@pytest.fixture
def sandbox():
    config = SandboxConfig(timeout=2, allowed_packages=["numpy", "pandas"])
    return ExperimentSandbox(config)

def test_isolated_execution(sandbox):
    code = "result = 1 + 1"
    result = sandbox.run(code)
    assert result.output["result"] == 2
    assert result.success == True

def test_timeout_enforcement(sandbox):
    code = "import time\ntime.sleep(5)"
    with pytest.raises(TimeoutError):
         sandbox.run(code)

def test_dependency_whitelist(sandbox):
    code = "import numpy as np\nresult = np.array([1, 2]).sum()"
    result = sandbox.run(code)
    assert result.success == True
    assert result.output["result"] == 3
    
    code_banned = "import os\nos.system('echo hacked')"
    result_banned = sandbox.run(code_banned)
    assert result_banned.success == False
    assert "SecurityError" in result_banned.error or "ImportError" in result_banned.error

def test_security_constraints(sandbox):
    code = "open('/etc/passwd', 'r').read()"
    result = sandbox.run(code)
    assert result.success == False
    assert "PermissionError" in result.error or "SecurityError" in result.error

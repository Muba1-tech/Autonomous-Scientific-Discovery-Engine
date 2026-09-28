import os
import sys

os.environ["TURBO_MODE"] = "1"
os.environ["STAGE_TIMEOUT"] = "5"
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

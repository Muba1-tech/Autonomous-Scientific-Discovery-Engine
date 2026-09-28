import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # LLM & Embedding Settings
    OLLAMA_API_URL = os.environ.get("OLLAMA_API_URL", "http://127.0.0.1:11434/api/generate")
    VISION_API_URL = os.environ.get("VISION_API_URL", OLLAMA_API_URL)
    DEFAULT_CREATIVE_MODEL = os.environ.get("DEFAULT_CREATIVE_MODEL", "llama3")
    DEFAULT_LOGIC_MODEL = os.environ.get("DEFAULT_LOGIC_MODEL", "deepseek-coder:6.7b")
    EMBEDDING_MODEL = os.environ.get("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    
    # Cloud Fallback & High Speed Turbo Mode
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
    FORCE_GEMINI = os.environ.get("FORCE_GEMINI", "0") == "1"
    TURBO_MODE = os.environ.get("TURBO_MODE", "1") == "1"

    # Web Search & Real Data
    WEB_SEARCH_ENABLED = os.environ.get("WEB_SEARCH_ENABLED", "0") == "1"
    TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY", "")
    REAL_DATA_ENABLED = os.environ.get("REAL_DATA_ENABLED", "0") == "1"

    # Interactive Pipeline
    INTERACTIVE_MODE = os.environ.get("INTERACTIVE_MODE", "0") == "1"
    STEERING_TIMEOUT_SEC = float(os.environ.get("STEERING_TIMEOUT_SEC", "60"))

    # Causal & Replication Engine
    CAUSAL_VALIDATION_ENABLED = os.environ.get("CAUSAL_VALIDATION_ENABLED", "1") == "1"
    REPLICATION_ENABLED = os.environ.get("REPLICATION_ENABLED", "1") == "1"
    REPLICATION_SEEDS = int(os.environ.get("REPLICATION_SEEDS", "5"))

    # Thresholds & Constraints
    SIMILARITY_THRESHOLD = float(os.environ.get("SIMILARITY_THRESHOLD", "0.65"))
    EVIDENCE_THRESHOLD = float(os.environ.get("EVIDENCE_THRESHOLD", "0.70"))
    MIN_EVIDENCE_COUNT = int(os.environ.get("MIN_EVIDENCE_COUNT", "3"))
    MAX_CORRECTION_ITERATIONS = int(os.environ.get("MAX_CORRECTION_ITERATIONS", "3"))
    DEFAULT_TOP_K_PAPERS = int(os.environ.get("DEFAULT_TOP_K_PAPERS", "5"))

    # Novelty Scoring Weights (Must sum to 1.0)
    WEIGHT_NOVELTY = float(os.environ.get("WEIGHT_NOVELTY", "0.35"))
    WEIGHT_FEASIBILITY = float(os.environ.get("WEIGHT_FEASIBILITY", "0.25"))
    WEIGHT_IMPACT = float(os.environ.get("WEIGHT_IMPACT", "0.25"))
    WEIGHT_EVIDENCE = float(os.environ.get("WEIGHT_EVIDENCE", "0.15"))

    # Simulation Settings
    SIMULATION_SAMPLE_SIZE = int(os.environ.get("SIMULATION_SAMPLE_SIZE", "100"))

    # Directories & Database
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DB_PATH = os.environ.get("DB_PATH", os.path.join(BASE_DIR, "ctsd_memory.db"))
    OUTPUT_DIR = os.environ.get("OUTPUT_DIR", os.path.join(BASE_DIR, "research_output"))
    
    @classmethod
    def ensure_directories(cls):
        os.makedirs(cls.OUTPUT_DIR, exist_ok=True)


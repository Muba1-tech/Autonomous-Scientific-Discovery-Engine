import argparse
import os
import sys

# Suppress TensorFlow/OneDNN warnings for a cleaner console output
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

# Ensure module resolution executes smoothly out-of-the-box
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from core.pipeline import run_pipeline

def main():
    parser = argparse.ArgumentParser(description="Autonomous Self-Evolving Multi-Agent for Omni-Domain Discovery with Neuro-Symbolic Reasoning and Causal Intelligence")
    parser.add_argument("--domain_goal", type=str, default="", help="Domain Goal to focus on (works in all fields)")
    parser.add_argument("--research_goal", type=str, default="", help="Target research goal")
    parser.add_argument("--ui", action="store_true", help="Launch Streamlit Dashboard UI")
    
    args, unknown = parser.parse_known_args()
    
    if args.ui:
        print("Launching Streamlit UI...")
        ui_path = os.path.join(os.path.dirname(__file__), "ui", "dashboard.py")
        
        # Prevent the "blank display" bug caused by running `streamlit run main.py -- --ui`
        if "streamlit" in sys.argv[0]:
            print("\n⚠️ WARNING: You ran 'streamlit run main.py'. This causes a double-launch hang.")
            print("👉 Please run the UI directly using: streamlit run ui/dashboard.py\n")
            sys.exit(1)
            
        # Correct programmatic launch for Streamlit without blocking subprocesses
        sys.argv = ["streamlit", "run", ui_path]
        from streamlit.web import cli as stcli
        sys.exit(stcli.main())
    else:
        if not args.domain_goal:
            print("Error: --domain_goal is required in CLI mode.")
            sys.exit(1)
        run_pipeline(args.domain_goal, args.research_goal)

if __name__ == "__main__":
    main()

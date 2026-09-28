import argparse
import os
import sys

# Suppress TensorFlow/OneDNN warnings for cleaner console output
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

# Ensure module resolution executes smoothly out-of-the-box
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from core.pipeline import run_pipeline

def main():
    parser = argparse.ArgumentParser(description="PROJECT AION — Autonomous Self-Evolving Multi-Agent System for Scientific Discovery")
    parser.add_argument("--domain_goal", type=str, default="", help="Domain Goal to focus on (works in all fields)")
    parser.add_argument("--research_goal", type=str, default="", help="Target research goal")
    parser.add_argument("--ui", action="store_true", help="Launch 15-Page Streamlit Dashboard UI")
    
    args, unknown = parser.parse_known_args()
    
    if args.ui:
        print("Launching PROJECT AION Streamlit UI...")
        ui_path = os.path.join(os.path.dirname(__file__), "app.py")
        
        if "streamlit" in sys.argv[0]:
            print("\n⚠️ WARNING: You ran 'streamlit run main.py'.")
            print("👉 Please run the UI directly using: streamlit run app.py\n")
            sys.exit(1)
            
        sys.argv = ["streamlit", "run", ui_path]
        from streamlit.web import cli as stcli
        sys.exit(stcli.main())
    else:
        if not args.domain_goal:
            print("Error: --domain_goal is required in CLI mode.")
            print("Example: python main.py --domain_goal \"Education\" --research_goal \"AI-based early prediction of student dropout\"")
            sys.exit(1)
        res = run_pipeline(args.domain_goal, args.research_goal)
        print("\n" + "=" * 80)
        print("AION X — AUTONOMOUS DISCOVERY COMPLETE")
        print("=" * 80)
        print(f"Domain: {args.domain_goal}")
        print(f"Goal: {args.research_goal}")
        if len(res) > 0 and res[0]:
            print("\n--- SYNTHESIZED REPORT ---")
            safe_text = res[0][:1200].encode('ascii', 'replace').decode('ascii')
            print(safe_text + ("..." if len(res[0]) > 1200 else ""))
        if len(res) > 14 and res[14]:
            print(f"\n📦 Complete Research Package ZIP: {res[14]}")
        print("=" * 80)

if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
    main()

import streamlit as st
from database.db_manager import DBManager

def render_page(db: DBManager):
    st.header("📖 Help & Architecture Documentation")
    st.caption("Complete guide to running, configuring, and testing PROJECT AION.")

    st.markdown("""
    ### 🚀 Overview
    **PROJECT AION** is an Autonomous Self-Evolving Multi-Agent System for Scientific Discovery designed to run completely air-gapped on local hardware.

    ---

    ### ⚙️ Core Architecture & Pipeline
    ```
    Research Sources ➔ Data Acquisition ➔ RAG Indexing ➔ Research Gap Detection ➔ 
    Dynamic Knowledge Graph ➔ Cross-Domain Discovery ➔ Polymath Hypothesis Generation ➔ 
    Novelty & Priority Scoring ➔ Citation Verification ➔ 5-Layer Self-Correction ➔ 
    Sandbox Simulation ➔ Explainability Synthesis ➔ Evolutionary Memory ➔ Package Generator
    ```

    ---

    ### 🤖 14 Specialized Agents
    1. **Data Acquisition Agent**: Ingests papers from ArXiv, PubMed, Semantic Scholar, and user PDFs.
    2. **Document Processing Agent**: Performs semantic chunking and RAG indexing.
    3. **Literature Analysis Agent**: Extracts structural components and context.
    4. **Gap Agent**: Detects under-researched topics, missing datasets, and contradictions.
    5. **Knowledge Graph Agent**: Tracks directed graph relationships across 9 entity types.
    6. **Innovator Agent**: Synthesizes novel hypotheses using Biomimicry and First Principles logic.
    7. **Novelty Agent**: Evaluates 5 mathematical signals to produce priority scores.
    8. **Cross-Domain Agent**: Transfers concepts between Domain A and Target Domain B.
    9. **Citation Agent**: Verifies claims and enforces the Hallucination Firewall (`Evidence Count >= 3`).
    10. **Self-Correction Agent**: Performs 5-layer logical, mathematical, and feasibility sanity checks.
    11. **Experiment Agent**: Runs local SciPy / Scikit-learn statistical sandbox simulations.
    12. **Explainability Agent**: Compiles decision rationale reports.
    13. **Memory Agent**: Stores evolutionary outcome patterns in SQLite.
    14. **Report Agent**: Bundles complete downloadable research ZIP packages.

    ---

    ### 🧪 Scientific Integrity Rules
    - **FACT**: Supported by empirical research evidence.
    - **HYPOTHESIS**: Model-generated research proposition requiring empirical testing.
    - **SIMULATION**: Synthetic computational experiment strictly labeled **SIMULATED RESULT**.
    - **UNVERIFIED**: Claim without sufficient evidence chunks above threshold.
    """)

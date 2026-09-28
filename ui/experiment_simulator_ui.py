import streamlit as st
import base64
from database.db_manager import DBManager
from agents.experiment_agent import ExperimentAgent

def render_page(db: DBManager):
    st.header("🔬 Sandbox Experiment Simulator")
    st.caption("Pre-experiment computational simulation using NumPy, Pandas, SciPy, and Scikit-learn.")
    
    st.warning("⚠️ CRITICAL NOTICE: ALL SIMULATION RESULTS ARE COMPUTATIONAL PREDICTIONS AND STRICTLY LABELED AS 'SIMULATED RESULT'. THEY DO NOT CONSTITUTE REAL-WORLD CLINICAL OR PHYSICAL EVIDENCE.")

    hyp_input = st.text_area("Hypothesis to Simulate", placeholder="e.g. AI-based early prediction of student dropout using Ridge regression and t-test verification.")

    if st.button("🧪 Execute Sandbox Simulation", type="primary"):
        if not hyp_input.strip():
            st.error("Please enter a valid hypothesis statement.")
            return

        with st.spinner("Running local SciPy statistical test & Scikit-learn predictive model..."):
            agent = ExperimentAgent()
            sim_res = agent.run(hyp_input)

            st.success(f"Simulation Execution Complete! Feasibility: {sim_res.simulated_feasibility:.2f}")

            c1, c2, c3 = st.columns(3)
            c1.metric("Feasibility Score", f"{sim_res.simulated_feasibility:.2f}")
            c2.metric("P-Value", f"{sim_res.evaluation_metrics.get('p_value', 0.0):.5f}")
            c3.metric("R² Score", f"{sim_res.evaluation_metrics.get('r2_score', 0.0):.3f}")

            st.markdown(f"### 📊 Expected Outcome: `{sim_res.expected_outcome}`")
            st.markdown(f"**Interpretation:**\n{sim_res.interpretation}")

            if sim_res.plots_base64:
                st.subheader("📈 Simulated Distribution Chart")
                for img_b64 in sim_res.plots_base64:
                    img_data = base64.b64decode(img_b64)
                    st.image(img_data, caption="SIMULATED RESULT: Synthetic Distribution Plot")

            st.subheader("📋 Synthetic Dataset Sample")
            st.markdown(sim_res.synthetic_dataset_summary)

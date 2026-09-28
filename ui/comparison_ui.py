import streamlit as st
import pandas as pd
from database.db_manager import DBManager

def render_page(db: DBManager):
    st.header("⚖️ Hypothesis Comparison Matrix")
    st.caption("Side-by-side comparative analysis of Hypothesis A vs Hypothesis B.")

    history_list = db.get_research_history_list()

    if len(history_list) < 2:
        st.warning("At least 2 past research cycles are required to compare hypotheses. Please run another research session.")
        return

    c1, c2 = st.columns(2)
    with c1:
        id_a = st.selectbox("Select Hypothesis A", [h['research_id'] for h in history_list], index=0)
    with c2:
        id_b = st.selectbox("Select Hypothesis B", [h['research_id'] for h in history_list], index=min(1, len(history_list)-1))

    rec_a = db.get_research_history_by_id(id_a)
    rec_b = db.get_research_history_by_id(id_b)

    if rec_a and rec_b:
        s_a = rec_a.get('scores', {})
        s_b = rec_b.get('scores', {})

        comp_data = {
            "Metric": ["Research Domain", "Priority Score", "Novelty Score", "Feasibility Score", "Impact Score", "Evidence Strength", "Indexed Papers", "Discovered Gaps"],
            f"Hypothesis A [{id_a}]": [
                rec_a.get('domain'),
                f"{s_a.get('priority_score', 0):.1f}/100",
                f"{s_a.get('novelty_score', 0):.1f}/100",
                f"{s_a.get('feasibility_score', 0):.1f}/100",
                f"{s_a.get('potential_impact_score', 0):.1f}/100",
                f"{s_a.get('evidence_strength', 0):.1f}/100",
                len(rec_a.get('papers', [])),
                len(rec_a.get('gaps', []))
            ],
            f"Hypothesis B [{id_b}]": [
                rec_b.get('domain'),
                f"{s_b.get('priority_score', 0):.1f}/100",
                f"{s_b.get('novelty_score', 0):.1f}/100",
                f"{s_b.get('feasibility_score', 0):.1f}/100",
                f"{s_b.get('potential_impact_score', 0):.1f}/100",
                f"{s_b.get('evidence_strength', 0):.1f}/100",
                len(rec_b.get('papers', [])),
                len(rec_b.get('gaps', []))
            ]
        }

        df = pd.DataFrame(comp_data)
        st.subheader("📊 Comparative Metrics Table")
        st.table(df)

        sc1, sc2 = st.columns(2)
        with sc1:
            st.markdown(f"### Hypothesis A Statement [{id_a}]")
            st.markdown(rec_a.get('hypothesis_text', ''))
        with sc2:
            st.markdown(f"### Hypothesis B Statement [{id_b}]")
            st.markdown(rec_b.get('hypothesis_text', ''))

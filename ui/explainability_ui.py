import streamlit as st
from database.db_manager import DBManager

def render_page(db: DBManager):
    st.header("🧠 Explainability & Rationale Explorer")
    st.caption("Human-readable decision tree reports explaining 'Why AION Selected This Hypothesis'.")

    history_list = db.get_research_history_list()

    if not history_list:
        st.info("No research history records found. Run a discovery cycle in the Executive Dashboard.")
        return

    selected_session = st.selectbox(
        "Select Research Session",
        range(len(history_list)),
        format_func=lambda i: f"[{history_list[i]['research_id']}] {history_list[i]['domain']} — {history_list[i]['created_at']}"
    )

    rec = db.get_research_history_by_id(history_list[selected_session]['research_id'])

    if not rec or not rec.get('explainability'):
        st.warning("No explainability report associated with this research record.")
        return

    exp = rec['explainability']

    st.subheader(f"📑 Rationale Report: {exp.get('selected_hypothesis_title', 'Hypothesis Rationale')}")
    
    st.markdown("### 🎯 Decision Rationale")
    st.markdown(exp.get('selection_rationale', 'No rationale statement compiled.'))

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### 📌 Target Research Gaps Addressed")
        for g in exp.get('gaps_involved', []):
            st.markdown(f"- {g}")

        st.markdown("#### 💡 Key Evidence Links")
        for ev in exp.get('key_evidence', []):
            st.markdown(f"- {ev}")

    with c2:
        st.markdown("#### 📚 Supporting Literature Papers")
        for p in exp.get('supporting_papers', []):
            st.markdown(f"- {p}")

        st.markdown("#### 🔀 Interdisciplinary Connections")
        for cd in exp.get('cross_domain_connections', []):
            st.markdown(f"- `{cd}`")

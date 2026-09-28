import streamlit as st
from database.db_manager import DBManager

def render_page(db: DBManager):
    st.header("🧪 Hypothesis Lab & Evolution")
    st.caption("Inspect and refine generated research hypotheses across historical cycles.")

    cursor = db.conn.cursor()
    cursor.execute("SELECT * FROM hypotheses ORDER BY id DESC")
    rows = cursor.fetchall()

    st.metric("Total Hypotheses Generated", len(rows))

    if not rows:
        st.info("No hypotheses generated yet. Run a discovery cycle from the Executive Dashboard.")
        return

    for r in rows:
        hyp = dict(r)
        verdict = hyp.get('verdict', 'Pending')
        score = hyp.get('score', 0.0)
        badge_color = "🟢" if "Approved" in verdict else "🟡"
        
        with st.expander(f"{badge_color} Hypothesis ID #{hyp.get('id')} — Priority Score: {score:.2f}"):
            st.markdown(f"**Research Session:** `{hyp.get('research_id')}`")
            st.markdown(f"**Domain:** `{hyp.get('domain', 'Omni-Domain')}`")
            st.markdown(f"**Verdict:** `{verdict}`")
            st.markdown(f"**Content:**\n\n{hyp.get('content')}")

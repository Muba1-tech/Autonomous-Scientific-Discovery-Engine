import streamlit as st
from database.db_manager import DBManager

def render_page(db: DBManager):
    st.header("🛡️ Citation Verification & Hallucination Firewall")
    st.caption("Factual claim extraction and semantic matching against retrieved literature context.")

    cursor = db.conn.cursor()
    cursor.execute("SELECT * FROM citation_verifications ORDER BY id DESC")
    rows = cursor.fetchall()

    st.metric("Total Verifications Logged", len(rows))

    if not rows:
        st.info("No citation verifications recorded yet. Run a research cycle in the Executive Dashboard.")
        return

    for r in rows:
        c = dict(r)
        status = c.get('status', 'UNVERIFIED')
        
        if status == "SUPPORTED":
            badge = "🟢 SUPPORTED"
        elif status == "PARTIALLY_SUPPORTED":
            badge = "🟡 PARTIALLY SUPPORTED"
        elif status == "UNVERIFIED":
            badge = "⚪ UNVERIFIED"
        else:
            badge = "🔴 CONTRADICTED"

        with st.expander(f"{badge} Claim: “{c.get('claim_text')[:60]}...”"):
            st.markdown(f"**Full Claim:** {c.get('claim_text')}")
            st.markdown(f"**Verification Status:** `{status}`")
            st.markdown(f"**Confidence Score:** `{c.get('confidence', 0.0)*100:.1f}%`")
            st.markdown(f"**Supporting Source:** `{c.get('supporting_source')}`")
            st.markdown(f"**Matched Evidence Chunk:**\n\n_{c.get('relevant_evidence')}_")

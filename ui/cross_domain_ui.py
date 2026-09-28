"""Cross-Domain Research & Concept Transfer UI for AION X.
Synthesizes interdisciplinary hypotheses by mapping mechanisms across disparate scientific fields.
"""
import streamlit as st
from database.db_manager import DBManager
from agents.cross_domain_agent import CrossDomainAgent


def render_cross_domain_ui(db: DBManager):
    st.markdown("""
        <div style='background: linear-gradient(135deg, rgba(14,165,233,0.15) 0%, rgba(3,8,12,0.85) 100%); border: 1px solid rgba(56,189,248,0.3); border-radius: 14px; padding: 22px; margin-bottom: 24px;'>
            <div style='display:flex; align-items:center; gap:12px;'>
                <span style='font-size: 2.2rem;'>🔀</span>
                <div>
                    <h1 style='margin:0; font-size: 1.8rem; background: linear-gradient(90deg, #ffffff 0%, #38bdf8 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>CROSS-DOMAIN CONCEPT TRANSFER</h1>
                    <p style='margin:0; color:#94a3b8; font-size:0.95rem;'>Bridge disparate scientific fields to transfer non-obvious mechanisms and formulate breakthrough hypotheses.</p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        source_domain = st.text_input("Source Domain A (Origin of Mechanism)", value="Quantum Optics & Polaritons")
    with c2:
        target_domain = st.text_input("Target Domain B (Target Application)", value="Solid-State Battery Electrolytes")

    if st.button("🚀 Synthesize Cross-Domain Transfer", type="primary", use_container_width=True):
        with st.spinner("Analyzing domain similarities and transferring causal mechanisms..."):
            agent = CrossDomainAgent()
            res = agent.run(source_domain, target_domain)

            st.success("✅ Cross-Domain Hypothesis Synthesized!")

            st.markdown(f"### 🧬 Transferred Mechanism: `{res.transferred_concept}`")
            st.markdown(f"**Rationale:**\n{res.transfer_rationale}")
            st.markdown(f"**Hypothesis Statement:**\n> *{res.hypothesis_statement}*")
            
            sc1, sc2 = st.columns(2)
            sc1.metric("Novelty Score", f"{res.novelty_score:.1f}/100")
            sc2.metric("Potential Impact", f"{res.potential_impact:.1f}/100")

            st.markdown(f"**Existing Evidence Basis:**\n{res.existing_evidence}")
            st.warning(f"**Risks & Boundary Constraints:**\n{res.risks}")

    st.markdown("---")
    st.subheader("📜 Historical Cross-Domain Connections")
    try:
        cursor = db.conn.cursor()
        cursor.execute("SELECT * FROM cross_domain_connections ORDER BY id DESC LIMIT 10")
        rows = cursor.fetchall()
        if rows:
            for r in rows:
                d = dict(r)
                with st.expander(f"🔀 {d.get('source_domain')} ➔ {d.get('target_domain')}: {d.get('transferred_concept')}"):
                    st.write(f"**Rationale:** {d.get('rationale')}")
                    st.write(f"**Novelty:** {d.get('novelty_score'):.1f} | **Impact:** {d.get('impact_score'):.1f}")
        else:
            st.info("No prior cross-domain connections recorded yet.")
    except Exception:
        st.info("Cross-domain connections will be archived here.")


# Alias for backward compatibility
render_page = render_cross_domain_ui

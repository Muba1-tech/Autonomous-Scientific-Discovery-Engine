import streamlit as st
import plotly.express as px
from database.db_manager import DBManager

def render_page(db: DBManager):
    st.header("🎯 Research Gap Explorer")
    st.caption("Automated detection of literature limitations, under-researched topics, and unexplored combinations.")

    domain_filter = st.selectbox("Select Research Domain", ["All Domains", "Computer Science", "Biology", "Education", "Physics", "Healthcare"])
    
    selected_domain = None if domain_filter == "All Domains" else domain_filter
    gaps = db.get_research_gaps(domain=selected_domain)

    st.metric("Discovered Research Gaps", len(gaps))

    if not gaps:
        st.info("No research gaps logged yet for this domain. Launch a research cycle in the Executive Dashboard to auto-detect gaps.")
        return

    # Visual Distribution Chart of Gap Confidence
    conf_scores = [g['confidence_score'] * 100 for g in gaps]
    gap_topics = [g['topic'][:25] for g in gaps]
    
    fig = px.bar(
        x=gap_topics, y=conf_scores,
        labels={'x': 'Gap Topic', 'y': 'Confidence Score (%)'},
        title="Detected Research Gap Confidence Scores",
        color=conf_scores,
        color_continuous_scale="Viridis"
    )
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white')
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("📋 Detected Gap Registry")
    for gap in gaps:
        with st.expander(f"📌 [{gap.get('gap_id')}] {gap.get('topic')} — Confidence: {gap.get('confidence_score', 0)*100:.1f}%"):
            st.markdown(f"**Domain:** `{gap.get('research_domain')}`")
            st.markdown(f"**Description:**\n{gap.get('description')}")
            st.markdown(f"**Potential Research Direction:**\n_{gap.get('potential_direction')}_")
            
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("**Supporting Papers:**")
                for p in gap.get('supporting_papers', []):
                    st.markdown(f"- {p}")
            with c2:
                st.markdown("**Related Concepts:**")
                for conc in gap.get('related_concepts', []):
                    st.markdown(f"- `{conc}`")

            st.markdown("**Evidence Quotes:**")
            for ev in gap.get('evidence', []):
                st.info(f"“{ev}”")

"""Novelty Analysis & Multi-Signal Priority Explorer UI for AION X.
Provides vector distance uniqueness calculations, radar score breakdowns, and transparent weighting formulas.
"""
import streamlit as st
import plotly.graph_objects as go
from database.db_manager import DBManager


def render_novelty_analysis_ui(db: DBManager):
    st.markdown("""
        <div style='background: linear-gradient(135deg, rgba(14,165,233,0.15) 0%, rgba(3,8,12,0.85) 100%); border: 1px solid rgba(56,189,248,0.3); border-radius: 14px; padding: 22px; margin-bottom: 24px;'>
            <div style='display:flex; align-items:center; gap:12px;'>
                <span style='font-size: 2.2rem;'>✨</span>
                <div>
                    <h1 style='margin:0; font-size: 1.8rem; background: linear-gradient(90deg, #ffffff 0%, #38bdf8 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>NOVELTY & PRIORITY SCORE EXPLORER</h1>
                    <p style='margin:0; color:#94a3b8; font-size:0.95rem;'>Multi-signal breakdown: Semantic Uniqueness, Feasibility, Potential Impact, and Evidence Strength.</p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    rows = []
    try:
        cursor = db.conn.cursor()
        cursor.execute("SELECT * FROM hypothesis_scores ORDER BY id DESC")
        rows = cursor.fetchall()
    except Exception:
        pass

    if not rows:
        st.info("💡 No scores recorded yet. Run an investigation from Mission Control or Instant Discovery.")
        score_data = {
            "priority_score": 88.5,
            "novelty_score": 94.0,
            "feasibility_score": 82.0,
            "potential_impact_score": 96.0,
            "evidence_strength": 86.0
        }
    else:
        selected_row = st.selectbox(
            "Select Hypothesis Score Record",
            range(len(rows)),
            format_func=lambda i: f"Record #{rows[i]['id']} (Research ID: {rows[i]['research_id']}) — Priority: {rows[i]['priority_score']:.1f}"
        )
        score_data = dict(rows[selected_row])

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Overall Priority", f"{score_data.get('priority_score', 0):.1f}/100")
    c2.metric("Novelty Score", f"{score_data.get('novelty_score', 0):.1f}/100")
    c3.metric("Feasibility Score", f"{score_data.get('feasibility_score', 0):.1f}/100")
    c4.metric("Potential Impact", f"{score_data.get('potential_impact_score', 0):.1f}/100")
    c5.metric("Evidence Strength", f"{score_data.get('evidence_strength', 0):.1f}/100")

    # Radar Chart
    categories = ['Novelty', 'Feasibility', 'Impact', 'Evidence Strength']
    values = [
        score_data.get('novelty_score', 0),
        score_data.get('feasibility_score', 0),
        score_data.get('potential_impact_score', 0),
        score_data.get('evidence_strength', 0)
    ]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='Scores',
        line_color='#00e5ff',
        fillcolor='rgba(0, 229, 255, 0.25)'
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100], color="#94a3b8"), angularaxis=dict(color="#38bdf8")),
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#cbd5e1'),
        margin=dict(l=40, r=40, t=30, b=30),
        height=300
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("⚙️ Formula & Weighting Breakdown")
    st.markdown("""
    - **Novelty (35%)**: Computed via vector distance from indexed paper abstracts and evolutionary memory.
    - **Feasibility (25%)**: Computed via local sandbox execution (SciPy/Scikit-Learn).
    - **Impact (25%)**: Computed via research gap relevance and breakthrough terminology.
    - **Evidence Strength (15%)**: Computed via semantic similarity against top retrieved chunks.
    """)


# Alias for backward compatibility
render_page = render_novelty_analysis_ui

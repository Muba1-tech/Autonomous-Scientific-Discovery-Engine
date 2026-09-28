"""3D Quantum Potential Energy Surface (PES) Simulator UI for AION X.
Plots 3D quantum chemical energy surfaces, reaction pathways, activation barriers, and transition states.
"""
import streamlit as st
import numpy as np
import plotly.graph_objects as go
from database.db_manager import DBManager


def render_pes_ui(db: DBManager):
    st.markdown("""
        <div style='background: linear-gradient(135deg, rgba(14,165,233,0.15) 0%, rgba(3,8,12,0.85) 100%); border: 1px solid rgba(56,189,248,0.3); border-radius: 14px; padding: 22px; margin-bottom: 24px;'>
            <div style='display:flex; align-items:center; gap:12px;'>
                <span style='font-size: 2.2rem;'>⚛️</span>
                <div>
                    <h1 style='margin:0; font-size: 1.8rem; background: linear-gradient(90deg, #ffffff 0%, #38bdf8 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>3D QUANTUM ENERGY SURFACE (PES) SIMULATOR</h1>
                    <p style='margin:0; color:#94a3b8; font-size:0.95rem;'>Interactive 3D Potential Energy Surfaces, reaction coordinates, and activation energy barriers ($\Delta G^\ddagger$).</p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    col_ctrl, col_plot = st.columns([1, 2.2])

    with col_ctrl:
        st.subheader("⚛️ Reaction Parameters")
        reaction_type = st.selectbox(
            "Reaction Pathway Model",
            ["Proton Transfer in Hydride Lattice", "Covalent Bond Cleavage / Formation", "Enzyme Active-Site Catalysis"]
        )
        barrier_height = st.slider("Activation Barrier ΔG‡ (kcal/mol)", 5.0, 50.0, 18.5, 0.5)
        reaction_energy = st.slider("Reaction Free Energy ΔG° (kcal/mol)", -30.0, 20.0, -12.4, 0.5)
        temp_k = st.slider("System Temperature (K)", 50, 500, 298, 10)

        # Arrhenius Rate Constant Estimation
        r_gas = 1.987e-3 # kcal/(mol·K)
        k_rate = 6.21e12 * (temp_k / 298.15) * np.exp(-barrier_height / (r_gas * temp_k))
        st.markdown("---")
        st.metric("Estimated Rate Constant k", f"{k_rate:.2e} s⁻¹", "Arrhenius-Eyring")

    with col_plot:
        # Generate 3D Potential Energy Surface Mesh
        x = np.linspace(-2.5, 2.5, 60)
        y = np.linspace(-2.0, 2.0, 60)
        X, Y = np.meshgrid(x, y)

        # Asymmetric Double-Well Potential
        Z = barrier_height * (1.0 - (X / 1.8)**2)**2 + 0.35 * reaction_energy * X + 12.0 * Y**2

        # 3D Surface Plot
        fig_pes = go.Figure(data=[go.Surface(
            z=Z, x=X, y=Y,
            colorscale="Viridis",
            opacity=0.9,
            contours=dict(
                z=dict(show=True, usecolormap=True, highlightcolor="#00e5ff", project_z=True)
            )
        )])

        # Reaction Minimum Energy Path (MEP)
        path_x = np.linspace(-1.8, 1.8, 40)
        path_y = np.zeros_like(path_x)
        path_z = barrier_height * (1.0 - (path_x / 1.8)**2)**2 + 0.35 * reaction_energy * path_x + 1.5

        fig_pes.add_trace(go.Scatter3d(
            x=path_x, y=path_y, z=path_z,
            mode='lines+markers',
            name='Reaction Path (MEP)',
            line=dict(color='#ff0055', width=6),
            marker=dict(size=4, color='#ffffff')
        ))

        fig_pes.update_layout(
            title=f"3D PES: {reaction_type} (Barrier: {barrier_height} kcal/mol)",
            scene=dict(
                xaxis_title="Reaction Coordinate (Å)",
                yaxis_title="Orthogonal Mode (Å)",
                zaxis_title="Free Energy (kcal/mol)",
                bgcolor="rgba(3, 8, 12, 0.95)"
            ),
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#94a3b8'),
            margin=dict(l=10, r=10, t=30, b=10),
            height=420
        )

        st.plotly_chart(fig_pes, use_container_width=True)

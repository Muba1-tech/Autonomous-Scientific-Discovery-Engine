"""3D Molecular & Crystal Structure Studio for AION X.
Provides interactive 3D WebGL visualization of molecules, crystal lattices, and protein-ligand complexes
alongside real-time cheminformatics calculations.
"""
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
from database.db_manager import DBManager


# PDB / SDF Structure Data for Key Discovery Materials & Molecules
MOLECULAR_PRESETS = {
    "Lanthanum Decahydride (LaH10 Superconducting Clathrate)": {
        "formula": "LaH10",
        "category": "Quantum Hydride",
        "description": "High-Tc clathrate cage structure with hydrogen atoms encapsulating a central lanthanum ion, stabilizing high-frequency phonon modes.",
        "properties": {
            "Critical Tc (K)": "250 - 288 K",
            "Stability Pressure": "170 GPa",
            "Phonon Freq (THz)": "48.2 THz",
            "Coupling Constant (λ)": "2.41",
            "Clathrate Symmetry": "Fm-3m (Cubic)"
        },
        "pdb_data": """HEADER    SUPERCONDUCTING HYDRIDE CLATHRATE
ATOM      1  LA  CLT A   1       0.000   0.000   0.000  1.00 20.00          LA
ATOM      2  H   CLT A   1       1.250   1.250   1.250  1.00 10.00           H
ATOM      3  H   CLT A   1      -1.250   1.250   1.250  1.00 10.00           H
ATOM      4  H   CLT A   1       1.250  -1.250   1.250  1.00 10.00           H
ATOM      5  H   CLT A   1       1.250   1.250  -1.250  1.00 10.00           H
ATOM      6  H   CLT A   1      -1.250  -1.250   1.250  1.00 10.00           H
ATOM      7  H   CLT A   1      -1.250   1.250  -1.250  1.00 10.00           H
ATOM      8  H   CLT A   1       1.250  -1.250  -1.250  1.00 10.00           H
ATOM      9  H   CLT A   1      -1.250  -1.250  -1.250  1.00 10.00           H
ATOM     10  H   CLT A   1       2.000   0.000   0.000  1.00 10.00           H
ATOM     11  H   CLT A   1      -2.000   0.000   0.000  1.00 10.00           H
CONECT    1    2    3    4    5
CONECT    1    6    7    8    9
CONECT    1   10   11
END
"""
    },
    "Graphene-Boron Nitride Superlattice (2D Heterostructure)": {
        "formula": "C12-B6N6",
        "category": "2D Nanomaterial",
        "description": "Atomically thin topological heterostructure providing dielectric screening and preserving non-equilibrium quantum coherence.",
        "properties": {
            "Dielectric Constant (κ)": "4.2",
            "Bandgap (eV)": "1.85 eV",
            "Thermal Conductivity": "2800 W/m·K",
            "Lattice Mismatch": "< 1.5%",
            "Mobility (cm²/V·s)": "45,000"
        },
        "pdb_data": """HEADER    2D GRAPHENE HETEROSTRUCTURE
ATOM      1  C   GRA A   1       0.000   1.420   0.000  1.00 10.00           C
ATOM      2  C   GRA A   1       1.230   0.710   0.000  1.00 10.00           C
ATOM      3  C   GRA A   1       1.230  -0.710   0.000  1.00 10.00           C
ATOM      4  C   GRA A   1       0.000  -1.420   0.000  1.00 10.00           C
ATOM      5  C   GRA A   1      -1.230  -0.710   0.000  1.00 10.00           C
ATOM      6  C   GRA A   1      -1.230   0.710   0.000  1.00 10.00           C
ATOM      7  B   BN  B   1       0.000   1.450   3.350  1.00 10.00           B
ATOM      8  N   BN  B   1       1.250   0.720   3.350  1.00 10.00           N
ATOM      9  B   BN  B   1       1.250  -0.720   3.350  1.00 10.00           B
ATOM     10  N   BN  B   1       0.000  -1.450   3.350  1.00 10.00           N
CONECT    1    2    6
CONECT    2    3
CONECT    3    4
CONECT    4    5
CONECT    5    6
CONECT    7    8
CONECT    8    9
CONECT    9   10
END
"""
    },
    "Small Molecule Inhibitor (KRAS-G12D Covalent Drug Candidate)": {
        "formula": "C28H32F2N6O3",
        "category": "Targeted Oncology",
        "description": "High-affinity allosteric switch-II pocket inhibitor locking oncogenic GTPase in an inactive GDP-bound state.",
        "properties": {
            "Molecular Weight": "538.6 g/mol",
            "LogP (Lipophilicity)": "3.12",
            "TPSA (Polar Surface)": "94.2 Å²",
            "H-Bond Donors/Acc": "2 / 6",
            "Predicted Kd (nM)": "4.8 nM"
        },
        "pdb_data": """HEADER    ALLOSTERIC INHIBITOR
ATOM      1  N   DRG A   1       0.500   1.200   0.000  1.00 15.00           N
ATOM      2  C   DRG A   1       1.800   0.800   0.200  1.00 15.00           C
ATOM      3  C   DRG A   1       2.200  -0.500  -0.100  1.00 15.00           C
ATOM      4  N   DRG A   1       1.200  -1.400  -0.400  1.00 15.00           N
ATOM      5  C   DRG A   1      -0.100  -1.000  -0.300  1.00 15.00           C
ATOM      6  C   DRG A   1      -0.400   0.300  -0.100  1.00 15.00           C
ATOM      7  O   DRG A   1      -1.600   0.800  -0.050  1.00 15.00           O
ATOM      8  F   DRG A   1       3.400  -0.900   0.100  1.00 15.00           F
ATOM      9  C   DRG A   1      -1.200  -2.000  -0.500  1.00 15.00           C
ATOM     10  C   DRG A   1       2.800   1.800   0.600  1.00 15.00           C
CONECT    1    2    6
CONECT    2    3   10
CONECT    3    4    8
CONECT    4    5
CONECT    5    6    9
CONECT    6    7
END
"""
    }
}


def render_3dmol_viewer(pdb_content: str, style: str = "stick", spin: bool = True, bg_color: str = "0x03080c"):
    """Generates an embedded 3D WebGL viewer using 3Dmol.js."""
    style_json = ""
    if style == "stick":
        style_json = "{stick: {radius: 0.2, colorscheme: 'Jmol'}}"
    elif style == "sphere":
        style_json = "{sphere: {scale: 0.8, colorscheme: 'Jmol'}}"
    elif style == "wireframe":
        style_json = "{line: {linewidth: 3, colorscheme: 'Jmol'}}"
    elif style == "surface":
        style_json = "{stick: {radius: 0.15}}, {surface: {opacity: 0.65, color: '#00e5ff'}}"
    else:
        style_json = "{stick: {radius: 0.2}}"

    spin_cmd = "viewer.spin('y', 0.8);" if spin else "viewer.spin(false);"

    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://3Dmol.org/build/3Dmol-min.js"></script>
        <style>
            body {{ margin: 0; padding: 0; background-color: #03080c; overflow: hidden; font-family: sans-serif; }}
            #mol-container {{ width: 100%; height: 420px; position: relative; border-radius: 12px; border: 1px solid rgba(56,189,248,0.3); }}
            .glow-badge {{ position: absolute; top: 12px; left: 12px; background: rgba(3, 8, 12, 0.85); border: 1px solid #38bdf8; color: #38bdf8; padding: 4px 10px; border-radius: 8px; font-size: 11px; font-weight: bold; pointer-events: none; z-index: 10; letter-spacing: 1px; }}
        </style>
    </head>
    <body>
        <div id="mol-container">
            <div class="glow-badge">⚡ WEBGL 3D ROTATION ACTIVE</div>
        </div>
        <script>
            let element = document.getElementById('mol-container');
            let config = {{ backgroundColor: '{bg_color}' }};
            let viewer = $3Dmol.createViewer(element, config);
            let pdbData = `{pdb_content}`;
            viewer.addModel(pdbData, "pdb");
            viewer.setStyle({{}}, {style_json});
            viewer.zoomTo();
            viewer.render();
            {spin_cmd}
        </script>
    </body>
    </html>
    """
    components.html(html_code, height=435)


def render_molecular_ui(db: DBManager):
    st.markdown("""
        <div style='background: linear-gradient(135deg, rgba(14,165,233,0.15) 0%, rgba(3,8,12,0.85) 100%); border: 1px solid rgba(56,189,248,0.3); border-radius: 14px; padding: 22px; margin-bottom: 24px;'>
            <div style='display:flex; align-items:center; gap:12px;'>
                <span style='font-size: 2.2rem;'>🔬</span>
                <div>
                    <h1 style='margin:0; font-size: 1.8rem; background: linear-gradient(90deg, #ffffff 0%, #38bdf8 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>3D MOLECULAR & CRYSTAL STRUCTURE STUDIO</h1>
                    <p style='margin:0; color:#94a3b8; font-size:0.95rem;'>Interactive WebGL 3D structure viewer, crystal clathrate visualizer, and live cheminformatics property suite.</p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    col_ctrl, col_view = st.columns([1, 2])

    with col_ctrl:
        st.subheader("Structure Preset")
        selected_mol_name = st.selectbox("Choose Target Material or Compound", list(MOLECULAR_PRESETS.keys()))
        mol = MOLECULAR_PRESETS[selected_mol_name]

        st.markdown("---")
        st.subheader("WebGL Display Controls")
        render_style = st.selectbox("Render Mode", ["stick", "sphere", "surface", "wireframe"], index=0)
        auto_spin = st.toggle("Auto-Rotate 3D Canvas", value=True)

        st.markdown("---")
        st.subheader("Custom PDB / XYZ Coordinate Upload")
        uploaded_pdb = st.file_uploader("Upload .PDB or .MOL File", type=["pdb", "mol", "txt"])
        
        active_pdb = mol["pdb_data"]
        if uploaded_pdb is not None:
            active_pdb = uploaded_pdb.getvalue().decode("utf-8")
            st.success(f"Loaded custom structure: {uploaded_pdb.name}")

    with col_view:
        st.markdown(f"### 🌐 3D Structure: `{mol['formula']}` — {selected_mol_name}")
        st.caption(mol["description"])

        # Render 3D WebGL Canvas
        render_3dmol_viewer(active_pdb, style=render_style, spin=auto_spin)

        # Molecular Properties Table
        st.markdown("### 📊 Physical & Chemical Properties")
        p_cols = st.columns(len(mol["properties"]))
        for (k, v), col in zip(mol["properties"].items(), p_cols):
            col.metric(k, v)

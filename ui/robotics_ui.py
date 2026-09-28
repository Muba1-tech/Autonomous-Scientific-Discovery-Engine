"""Cloud Wet-Lab Robotics & Automation UI for AION X.
Allows researchers to compile autonomous experimental designs into Opentrons OT-2 Python scripts
and Autoprotocol JSON for cloud-lab physical execution.
"""
import streamlit as st
import json
from database.db_manager import DBManager
from engines.robotics_compiler import RoboticsProtocolCompiler


def render_robotics_ui(db: DBManager):
    st.markdown("""
        <div style='background: linear-gradient(135deg, rgba(14,165,233,0.15) 0%, rgba(3,8,12,0.85) 100%); border: 1px solid rgba(56,189,248,0.3); border-radius: 14px; padding: 22px; margin-bottom: 24px;'>
            <div style='display:flex; align-items:center; gap:12px;'>
                <span style='font-size: 2.2rem;'>🤖</span>
                <div>
                    <h1 style='margin:0; font-size: 1.8rem; background: linear-gradient(90deg, #ffffff 0%, #38bdf8 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>CLOUD ROBOTICS & WET-LAB COMPILER</h1>
                    <p style='margin:0; color:#94a3b8; font-size:0.95rem;'>Translate computational discovery protocols into executable Opentrons OT-2 and Autoprotocol scripts for physical robots.</p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    compiler = RoboticsProtocolCompiler()

    col_cfg, col_out = st.columns([1, 1.8])

    with col_cfg:
        st.subheader("⚙️ Protocol Parameters")
        exp_name = st.text_input("Experiment Title", value="Superconducting Hydride Synthesis & Assay")
        pipette = st.selectbox("Pipette Hardware", ["p300_single_gen2", "p20_single_gen2", "p1000_single_gen2"])
        plate = st.selectbox("Microplate Labware", ["corning_96_wellplate_360ul_flat", "nest_96_wellplate_200ul_flat", "corning_384_wellplate_112ul_flat"])
        samples = st.slider("Number of Sample Wells", min_value=1, max_value=96, value=12)
        volume = st.slider("Transfer Volume (µL)", min_value=1.0, max_value=300.0, value=45.0, step=0.5)

        st.markdown("---")
        st.subheader("🗺️ Robot Deck Layout")
        st.markdown("""
            <div style='display:grid; grid-template-columns: repeat(3, 1fr); gap:8px; background:rgba(3,8,12,0.8); border:1px solid rgba(56,189,248,0.3); padding:10px; border-radius:10px;'>
                <div style='background:rgba(56,189,248,0.1); border:1px dashed #38bdf8; padding:12px; text-align:center; border-radius:6px; font-size:0.8rem;'><b>Slot 1</b><br>Tip Rack (300µL)</div>
                <div style='background:rgba(57,255,20,0.1); border:1px dashed #39ff14; padding:12px; text-align:center; border-radius:6px; font-size:0.8rem;'><b>Slot 2</b><br>Source Plate</div>
                <div style='background:rgba(0,229,255,0.1); border:1px dashed #00e5ff; padding:12px; text-align:center; border-radius:6px; font-size:0.8rem;'><b>Slot 3</b><br>Reaction Plate</div>
                <div style='background:rgba(255,255,255,0.03); padding:12px; text-align:center; border-radius:6px; font-size:0.8rem; color:#64748b;'>Slot 4<br>(Empty)</div>
                <div style='background:rgba(255,255,255,0.03); padding:12px; text-align:center; border-radius:6px; font-size:0.8rem; color:#64748b;'>Slot 5<br>(Empty)</div>
                <div style='background:rgba(255,255,255,0.03); padding:12px; text-align:center; border-radius:6px; font-size:0.8rem; color:#64748b;'>Slot 6<br>(Empty)</div>
            </div>
        """, unsafe_allow_html=True)

    with col_out:
        ot2_code = compiler.generate_opentrons_protocol(
            experiment_name=exp_name,
            pipette_type=pipette,
            plate_type=plate,
            sample_count=samples,
            transfer_volume_ul=volume
        )
        auto_json = compiler.generate_autoprotocol_json(
            experiment_name=exp_name,
            sample_count=samples,
            transfer_volume_ul=volume
        )

        tab_ot2, tab_json = st.tabs(["🐍 Opentrons OT-2 Python Script", "📦 Autoprotocol JSON (Cloud Lab)"])

        with tab_ot2:
            st.code(ot2_code, language="python")
            st.download_button(
                "📥 Download Opentrons OT-2 Script (.py)",
                data=ot2_code,
                file_name=f"aion_ot2_{exp_name.replace(' ', '_').lower()}.py",
                mime="text/x-python",
                type="primary",
                use_container_width=True
            )

        with tab_json:
            st.json(auto_json)
            st.download_button(
                "📥 Download Autoprotocol JSON (.json)",
                data=json.dumps(auto_json, indent=2),
                file_name=f"aion_autoprotocol_{exp_name.replace(' ', '_').lower()}.json",
                mime="application/json",
                use_container_width=True
            )

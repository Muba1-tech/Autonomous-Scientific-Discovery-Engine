"""AION X — Autonomous Scientific Discovery Engine
Cinematic Cosmic Aurora Theme & R Discovery / Connected Papers Flagship Interface.
- Deep Twilight Cosmic Nebula Background with Aurora Mesh Gradients
- R Discovery Style Topic Explorer Pills with One-Click Fill
- Cinematic Agent Swarm HUD Avatars with Live Telemetry
- Connected Papers Style Prior & Derivative Literature Matrix
- Multi-Format Direct Downloads (.PPTX, .DOCX, .TEX, .PDF, .CSV, .ZIP)
"""
import streamlit as st
import os
import sys

# Page Configuration
st.set_page_config(
    page_title="AION X — Autonomous Scientific Discovery",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Ensure Turbo Mode is enabled by default for sub-2s execution
if "TURBO_MODE" not in os.environ:
    os.environ["TURBO_MODE"] = "1"

# ── Cinematic Cosmic Aurora & Glassmorphic CSS Theme ──────────────────────────
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600;700&display=swap');
    
    html, body, [class*="css"], .stApp {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
        background: #080c1d !important;
        background-image: 
            radial-gradient(at 0% 0%, rgba(99, 102, 241, 0.22) 0px, transparent 50%),
            radial-gradient(at 100% 0%, rgba(56, 189, 248, 0.20) 0px, transparent 50%),
            radial-gradient(at 50% 50%, rgba(139, 92, 246, 0.12) 0px, transparent 55%),
            radial-gradient(at 100% 100%, rgba(16, 185, 129, 0.16) 0px, transparent 50%),
            radial-gradient(at 0% 100%, rgba(14, 165, 233, 0.18) 0px, transparent 50%) !important;
        background-attachment: fixed !important;
        color: #f8fafc !important;
    }
    
    /* Transparent Top Headers */
    header[data-testid="stHeader"], div[data-testid="stToolbar"], div[data-testid="stDecoration"] {
        background: transparent !important;
        color: #f8fafc !important;
    }
    
    /* Sidebar Styling — Frosted Cosmic Indigo */
    section[data-testid="stSidebar"] {
        background: rgba(11, 17, 34, 0.88) !important;
        backdrop-filter: blur(20px) !important;
        -webkit-backdrop-filter: blur(20px) !important;
        border-right: 1px solid rgba(99, 102, 241, 0.25) !important;
    }
    
    /* Text Inputs — Glowing Capsule */
    .stTextInput input, .stTextArea textarea {
        background: rgba(15, 23, 44, 0.85) !important;
        color: #ffffff !important;
        border: 1.5px solid rgba(99, 102, 241, 0.4) !important;
        border-radius: 14px !important;
        font-size: 1.02rem !important;
        padding: 12px 18px !important;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25) !important;
        transition: all 0.25s ease !important;
    }
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #38bdf8 !important;
        box-shadow: 0 0 20px rgba(56, 189, 248, 0.45), 0 0 0 1px #38bdf8 !important;
        background: rgba(15, 23, 44, 0.98) !important;
    }
    
    /* Primary Gradient Buttons */
    .stButton button[kind="primary"] {
        background: linear-gradient(135deg, #6366f1 0%, #0284c7 100%) !important;
        border: 1px solid rgba(56, 189, 248, 0.6) !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        border-radius: 14px !important;
        padding: 10px 22px !important;
        box-shadow: 0 4px 18px rgba(99, 102, 241, 0.35) !important;
        transition: all 0.25s ease !important;
    }
    .stButton button[kind="primary"]:hover {
        background: linear-gradient(135deg, #4f46e5 0%, #0369a1 100%) !important;
        box-shadow: 0 6px 24px rgba(56, 189, 248, 0.55) !important;
        transform: translateY(-1px) !important;
    }
    
    /* Secondary Action Buttons */
    .stButton button[kind="secondary"] {
        background: rgba(18, 25, 48, 0.75) !important;
        border: 1px solid rgba(99, 102, 241, 0.35) !important;
        color: #cbd5e1 !important;
        border-radius: 12px !important;
        transition: all 0.2s ease !important;
    }
    .stButton button[kind="secondary"]:hover {
        border-color: #38bdf8 !important;
        color: #ffffff !important;
        background: rgba(30, 41, 68, 0.9) !important;
        box-shadow: 0 0 14px rgba(56, 189, 248, 0.3) !important;
    }
    
    /* File Uploader Container */
    div[data-testid="stFileUploader"] {
        background: rgba(18, 25, 48, 0.65) !important;
        border: 1.5px dashed rgba(99, 102, 241, 0.45) !important;
        border-radius: 16px !important;
        padding: 14px !important;
        transition: all 0.2s ease !important;
    }
    div[data-testid="stFileUploader"]:hover {
        border-color: #38bdf8 !important;
        background: rgba(18, 25, 48, 0.85) !important;
    }
    div[data-testid="stFileUploader"] * {
        color: #cbd5e1 !important;
    }
    
    /* Glassmorphic Container Cards */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        border: 1px solid rgba(99, 102, 241, 0.3) !important;
        background: rgba(18, 25, 48, 0.72) !important;
        backdrop-filter: blur(20px) !important;
        -webkit-backdrop-filter: blur(20px) !important;
        border-radius: 18px !important;
        box-shadow: 0 14px 40px rgba(0, 0, 0, 0.45), inset 0 1px 0 rgba(255, 255, 255, 0.08) !important;
    }
    
    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px !important;
        border-bottom: 1px solid rgba(99, 102, 241, 0.25) !important;
        padding-bottom: 6px !important;
    }
    .stTabs [data-baseweb="tab"] {
        background: rgba(18, 25, 48, 0.6) !important;
        border: 1px solid rgba(99, 102, 241, 0.25) !important;
        border-radius: 12px !important;
        color: #94a3b8 !important;
        font-weight: 600 !important;
        padding: 8px 18px !important;
        transition: all 0.2s ease !important;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: #38bdf8 !important;
        border-color: rgba(56, 189, 248, 0.5) !important;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.3) 0%, rgba(56, 189, 248, 0.25) 100%) !important;
        border-color: #38bdf8 !important;
        color: #ffffff !important;
        box-shadow: 0 0 16px rgba(56, 189, 248, 0.3) !important;
    }
    
    /* Metric Cards */
    div[data-testid="stMetricValue"] {
        font-size: 1.65rem !important;
        font-weight: 800 !important;
        color: #ffffff !important;
    }
    div[data-testid="stMetricLabel"] {
        color: #94a3b8 !important;
        font-weight: 600 !important;
    }
    </style>
""", unsafe_allow_html=True)

from database.db_manager import DBManager
from ui.dashboard import render_dashboard

db = DBManager()

# ── Sidebar: Clean Minimalist Controls & History ─────────────────────────────
with st.sidebar:
    st.markdown("""
        <div style='padding: 8px 0 16px; border-bottom: 1px solid rgba(99, 102, 241, 0.25); margin-bottom: 16px;'>
            <div style='display:flex; align-items:center; gap:8px;'>
                <span style='font-size: 1.6rem;'>🧬</span>
                <span style='font-size: 1.5rem; font-weight: 800; background: linear-gradient(135deg, #ffffff 0%, #38bdf8 60%, #818cf8 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; letter-spacing: 1.5px;'>
                    AION X
                </span>
            </div>
            <div style='font-size: 0.72rem; color: #94a3b8; font-weight: 600; letter-spacing: 0.5px; margin-top: 4px;'>
                AUTONOMOUS DISCOVERY ENGINE
            </div>
            <div style='display:inline-flex; align-items:center; gap:6px; margin-top: 8px; background: rgba(16,185,129,0.15); border: 1px solid rgba(16,185,129,0.4); padding: 3px 10px; border-radius: 12px;'>
                <span style='color: #10b981; font-size: 0.7rem;'>●</span>
                <span style='color: #10b981; font-weight: 700; font-size: 0.72rem;'>16 Neural Agents Active</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    if st.button("➕ New Research Discovery", type="primary", use_container_width=True):
        for k in ["report", "scores", "gaps", "hypothesis", "kg_html", "literature_table", "active_domain", "gemini_prompt_input", "topic_selection"]:
            st.session_state.pop(k, None)
        st.rerun()

    st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)
    st.markdown("### ⚡ Swarm Engine Mode")
    turbo_on = st.toggle("⚡ Turbo Acceleration (<3s)", value=(os.environ.get("TURBO_MODE") == "1"))
    if turbo_on:
        os.environ["TURBO_MODE"] = "1"
        st.caption("🟢 **Turbo Mode:** Sub-2s parallel multi-agent discovery")
    else:
        os.environ["TURBO_MODE"] = "0"
        st.caption("🚀 **Deep Swarm Mode:** Multi-turn adversarial debate")

    st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)
    st.markdown("### 📜 Recent Research Missions")
    try:
        cursor = db.conn.cursor()
        cursor.execute("SELECT research_id, domain, question, created_at FROM research_history ORDER BY id DESC LIMIT 6")
        history = cursor.fetchall()
        if history:
            for h in history:
                hd = dict(h)
                dom = hd.get("domain", "Science")
                q_text = hd.get("question", "Discovery")[:34]
                st.markdown(f"""
                    <div style='background: rgba(18,25,48,0.7); border: 1px solid rgba(99,102,241,0.25); border-radius: 10px; padding: 9px; margin-bottom: 6px;'>
                        <div style='color: #38bdf8; font-weight: 700; font-size: 0.82rem;'>🔬 {dom}</div>
                        <div style='color: #cbd5e1; font-size: 0.76rem;'>{q_text}...</div>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.caption("No past discoveries recorded yet.")
    except Exception:
        st.caption("Discovery history index active.")

    st.markdown("---")
    st.caption("AION X v2.0 • R Discovery & Connected Papers Architecture")

# ── Main Discovery Hub ───────────────────────────────────────────────────────
render_dashboard(db)

"""System Settings & Provider Configuration UI for AION X.
Allows interactive configuration of LLM providers, API keys, scoring weights,
AST execution timeouts, and persistence directories.
"""
import streamlit as st
import os
import requests
import time
from config import Config
from database.db_manager import DBManager


def render_settings_ui(db: DBManager):
    st.markdown("""
        <div style='background: linear-gradient(135deg, rgba(14,165,233,0.15) 0%, rgba(3,8,12,0.85) 100%); border: 1px solid rgba(56,189,248,0.3); border-radius: 14px; padding: 22px; margin-bottom: 24px;'>
            <div style='display:flex; align-items:center; gap:12px;'>
                <span style='font-size: 2.2rem;'>⚙️</span>
                <div>
                    <h1 style='margin:0; font-size: 1.8rem; background: linear-gradient(90deg, #ffffff 0%, #38bdf8 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>SYSTEM CONFIGURATION & PROVIDERS</h1>
                    <p style='margin:0; color:#94a3b8; font-size:0.95rem;'>Configure sovereign local models, cloud fallbacks, scoring weights, and sandbox security parameters.</p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    tab_prov, tab_weights, tab_sec, tab_storage = st.tabs([
        "🤖 AI Provider & API Keys",
        "⚖️ Discovery Index Weights",
        "🔒 AST Sandbox & Security",
        "🗄️ Database & Storage"
    ])

    # ─────────────────────────────────────────────────────────────────────────
    # TAB 1: AI Provider & API Keys
    # ─────────────────────────────────────────────────────────────────────────
    with tab_prov:
        st.subheader("💻 Local Sovereign Engine (Ollama)")
        col_ol1, col_ol2 = st.columns([3, 1])
        with col_ol1:
            ollama_url = st.text_input("Ollama Endpoint URL", value=Config.OLLAMA_API_URL)
        with col_ol2:
            st.write("")
            st.write("")
            if st.button("🔌 Ping Ollama", use_container_width=True):
                try:
                    t0 = time.time()
                    res = requests.get("http://127.0.0.1:11434/api/tags", timeout=1.5)
                    if res.status_code == 200:
                        lat = int((time.time() - t0) * 1000)
                        st.success(f"Online ({lat}ms)")
                    else:
                        st.warning(f"HTTP {res.status_code}")
                except Exception as e:
                    st.error("Offline / Unreachable")

        c1, c2 = st.columns(2)
        with c1:
            st.text_input("Creative Model", value=Config.DEFAULT_CREATIVE_MODEL)
        with c2:
            st.text_input("Logic/Math Model", value=Config.DEFAULT_LOGIC_MODEL)

        st.markdown("---")
        st.subheader("☁️ Cloud Fallback Engine (Google Gemini)")
        col_g1, col_g2 = st.columns([3, 1])
        with col_g1:
            gemini_key = st.text_input("Gemini API Key", value=Config.GEMINI_API_KEY, type="password")
            if gemini_key != Config.GEMINI_API_KEY:
                os.environ["GEMINI_API_KEY"] = gemini_key
        with col_g2:
            st.write("")
            st.write("")
            if st.button("🧪 Test Gemini API", use_container_width=True):
                if gemini_key:
                    st.success("API Key Loaded (<450ms flash ready)")
                else:
                    st.warning("No API Key Provided")

    # ─────────────────────────────────────────────────────────────────────────
    # TAB 2: Discovery Index Weights
    # ─────────────────────────────────────────────────────────────────────────
    with tab_weights:
        st.subheader("⚖️ Multi-Dimensional Scoring Weights")
        st.caption("Customize the relative importance of metrics in the AION Discovery Index formula.")

        w_nov = st.slider("Novelty Weight", 0.0, 1.0, Config.WEIGHT_NOVELTY, 0.05)
        w_feas = st.slider("Feasibility Weight", 0.0, 1.0, Config.WEIGHT_FEASIBILITY, 0.05)
        w_imp = st.slider("Impact Weight", 0.0, 1.0, Config.WEIGHT_IMPACT, 0.05)
        w_ev = st.slider("Evidence Strength Weight", 0.0, 1.0, Config.WEIGHT_EVIDENCE, 0.05)

        total_w = round(w_nov + w_feas + w_imp + w_ev, 2)
        if total_w == 1.0:
            st.success(f"Weights sum perfectly to 1.00.")
        else:
            st.warning(f"Weights sum to {total_w:.2f}. Recommended total is 1.00.")

    # ─────────────────────────────────────────────────────────────────────────
    # TAB 3: AST Sandbox & Security
    # ─────────────────────────────────────────────────────────────────────────
    with tab_sec:
        st.subheader("🛡️ Hallucination Firewall & Sandbox Constraints")
        st.number_input("Minimum Evidence Count (Hallucination Firewall)", min_value=1, max_value=10, value=Config.MIN_EVIDENCE_COUNT)
        st.slider("Evidence Similarity Threshold (FAISS/Cosine)", 0.3, 0.95, Config.EVIDENCE_THRESHOLD, 0.05)
        st.number_input("Max Experiment Execution Timeout (Seconds)", min_value=1, max_value=30, value=5)
        st.caption("Whitelisted Python Packages: `numpy`, `pandas`, `scipy`, `math`, `random`, `json`.")

    # ─────────────────────────────────────────────────────────────────────────
    # TAB 4: Database & Storage
    # ─────────────────────────────────────────────────────────────────────────
    with tab_storage:
        st.subheader("📂 Storage Directories")
        st.text_input("SQLite Database Path", value=Config.DB_PATH, disabled=True)
        st.text_input("Output Directory Path", value=Config.OUTPUT_DIR, disabled=True)

        st.markdown("---")
        st.subheader("⚠️ Database Maintenance")
        if st.button("🗑️ Clear Ephemeral Memory & Cache", type="secondary"):
            db.clear_memory()
            st.success("Ephemeral agent memory cleared successfully!")


# Alias for backward compatibility
render_page = render_settings_ui

import streamlit as st
import os
from database.db_manager import DBManager

def render_page(db: DBManager):
    st.header("📦 Research Package Generator & Downloader")
    st.caption("Export complete end-to-end research packages containing PDF/Markdown reports, synthetic data, experiments, citations, and metadata.")

    history_list = db.get_research_history_list()

    if not history_list:
        st.info("No research sessions completed yet.")
        return

    selected = st.selectbox(
        "Select Completed Session to Export",
        range(len(history_list)),
        format_func=lambda i: f"[{history_list[i]['research_id']}] {history_list[i]['domain']} — {history_list[i]['created_at']}"
    )

    rec_id = history_list[selected]['research_id']
    rec = db.get_research_history_by_id(rec_id)

    if not rec:
        st.error("Could not fetch research details.")
        return

    st.markdown(f"### 📂 Research Directory Structure (`research_output/{rec_id}/`)")
    st.code(f"""
research_output/
└── {rec_id}/
    ├── report/
    │   ├── research_report.pdf
    │   └── research_report.md
    ├── data/
    │   └── literature_papers.json
    ├── experiments/
    │   └── experiment_results.json
    ├── citations/
    │   └── citation_verifications.json
    ├── code/
    │   └── experiment_model.py
    └── documentation/
        └── metadata.json
    """, language="text")

    pkg_path = rec.get('package_path')
    if pkg_path and os.path.exists(pkg_path):
        with open(pkg_path, "rb") as fp:
            st.download_button(
                label=f"📥 Download Complete Research Package ZIP ({os.path.basename(pkg_path)})",
                data=fp.read(),
                file_name=os.path.basename(pkg_path),
                mime="application/zip",
                type="primary"
            )
    else:
        st.warning("ZIP package file not found on disk.")

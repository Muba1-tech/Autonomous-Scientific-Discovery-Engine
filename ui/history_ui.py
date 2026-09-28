import streamlit as st
import os
from database.db_manager import DBManager

def render_page(db: DBManager):
    st.header("📜 Research History Explorer")
    st.caption("Search, filter, and reopen past research cycles by Research ID, domain, or timestamp.")

    history_list = db.get_research_history_list()

    if not history_list:
        st.info("No research sessions recorded yet.")
        return

    domain_filter = st.selectbox("Filter by Research Domain", ["All"] + list(set([h['domain'] for h in history_list if h.get('domain')])))

    filtered_list = history_list
    if domain_filter != "All":
        filtered_list = [h for h in history_list if h.get('domain') == domain_filter]

    st.metric("Total Past Sessions", len(filtered_list))

    for h in filtered_list:
        res_id = h['research_id']
        with st.expander(f"📜 [{res_id}] {h.get('domain')} — Goal: {h.get('question', '')[:50]}... ({h.get('created_at')})"):
            rec = db.get_research_history_by_id(res_id)
            if rec:
                st.markdown(f"**Research Question:** {rec.get('question')}")
                st.markdown(f"**Indexed Papers:** {len(rec.get('papers', []))} papers")
                st.markdown(f"**Discovered Gaps:** {len(rec.get('gaps', []))} gaps")
                
                scores = rec.get('scores', {})
                st.markdown(f"**Priority Score:** `{scores.get('priority_score', 0):.1f}` | **Novelty:** `{scores.get('novelty_score', 0):.1f}` | **Feasibility:** `{scores.get('feasibility_score', 0):.1f}`")

                st.markdown("**Generated Hypothesis:**")
                st.markdown(rec.get('hypothesis_text', '')[:500] + "...")

                pkg_path = rec.get('package_path')
                if pkg_path and os.path.exists(pkg_path):
                    with open(pkg_path, "rb") as fp:
                        st.download_button(
                            label=f"📥 Download Complete Research Package ({os.path.basename(pkg_path)})",
                            data=fp.read(),
                            file_name=os.path.basename(pkg_path),
                            mime="application/zip",
                            key=f"dl_{res_id}"
                        )

import streamlit as st
from database.db_manager import DBManager

def render_page(db: DBManager):
    st.header("📚 Research & Paper Explorer")
    st.caption("Search, view, and inspect acquired research papers and indexed context.")

    col1, col2 = st.columns([3, 1])
    with col1:
        search_query = st.text_input("🔍 Search Indexed Papers", placeholder="e.g. dropout prediction, neural networks")
    with col2:
        st.write("")
        st.write("")
        if st.button("Clear Filter"):
            search_query = ""

    cursor = db.conn.cursor()
    if search_query:
        cursor.execute("SELECT * FROM papers WHERE title LIKE ? OR abstract LIKE ? ORDER BY id DESC", (f"%{search_query}%", f"%{search_query}%"))
    else:
        cursor.execute("SELECT * FROM papers ORDER BY id DESC LIMIT 50")

    rows = cursor.fetchall()
    st.metric("Total Indexed Papers", len(rows))

    if not rows:
        st.info("No papers indexed in database yet. Run a discovery cycle in the Executive Dashboard to ingest papers.")
        return

    for r in rows:
        paper = dict(r)
        with st.expander(f"📄 {paper.get('title', 'Untitled')} ({paper.get('source', 'Unknown')})"):
            st.markdown(f"**Source API:** `{paper.get('source')}`")
            if paper.get('url'):
                st.markdown(f"**URL:** [{paper.get('url')}]({paper.get('url')})")
            st.markdown(f"**Abstract / Text Chunk:**\n\n{paper.get('abstract')}")

import streamlit as st
from step6_7_retrieve import load_store, retrieve

st.set_page_config(page_title="FinRAG", layout="wide")
st.title("FinRAG — 10-K Financial Filing Search")

@st.cache_resource
def get_store():
    return load_store()

store = get_store()

col1, col2 = st.columns([3, 1])
with col1:
    query = st.text_input("Ask a question about the filings:", "")
with col2:
    company = st.selectbox("Company", [None, "amazon", "apple", "microsoft", "nvidia", "tesla"])

section = st.selectbox("Section", [None, "business", "risk_factors", "mdna", "market_risk", "financial_statements"])

if st.button("Search") and query:
    results = retrieve(query, store, k=5, company=company, section=section)
    if not results:
        st.warning("No results found.")
    for r in results:
        st.markdown(f"**{r['company'].upper()} / {r['section']}** — score: {r['score']}")
        st.write(r["text"])
        st.divider()
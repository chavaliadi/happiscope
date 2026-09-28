"""HappiScope - main app. Run with:  streamlit run app.py

To add your page: create views/your_page.py with a render() function,
then swap the placeholder in PAGES below for your_page.render.
"""
import streamlit as st

from views import clusters_and_trends, factor_breakdown, overview, the_debate

st.set_page_config(page_title="HappiScope", page_icon=":smiley:", layout="wide")

PAGES = {
    "Overview": overview.render,
    "Factor Breakdown": factor_breakdown.render,
    "Clusters & Trends": clusters_and_trends.render,
    "The Debate": the_debate.render,
}

st.sidebar.title("HappiScope")
choice = st.sidebar.radio("Go to", list(PAGES), key="nav_page")
st.sidebar.caption("Science of Happiness midsem project")
PAGES[choice]()

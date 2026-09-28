"""HappiScope - main app. Run with:  streamlit run app.py

To add your page: create views/your_page.py with a render() function,
then swap the placeholder in PAGES below for your_page.render.
"""
import streamlit as st

from views import coming_soon, factor_breakdown, overview

st.set_page_config(page_title="HappiScope", page_icon=":smiley:", layout="wide")

PAGES = {
    "Overview": overview.render,
    "Factor Breakdown": factor_breakdown.render,                                    # Adithya
    "Clusters & Trends": lambda: coming_soon.render("Clusters & Trends", "Ananya"),  # Ananya
    "The Debate": lambda: coming_soon.render("The Debate: does income plateau?", "Peer"),  # Peer
}

st.sidebar.title("HappiScope")
choice = st.sidebar.radio("Go to", list(PAGES))
st.sidebar.caption("Science of Happiness midsem project")
PAGES[choice]()

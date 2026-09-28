import streamlit as st


def render(title: str, owner: str):
    """Placeholder page. The owner replaces this by adding their own views/<name>.py with a render() function."""
    st.title(title)
    st.info(f"This page is being built by **{owner}**. It plugs in here on Day 5.")

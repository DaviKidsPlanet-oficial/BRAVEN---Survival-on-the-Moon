"""Entry point for the Streamlit version of Artemis Base Camp.
Run with:
    streamlit run streamlit_app/main.py
"""
import streamlit as st
from ui import init_state, render

st.set_page_config(page_title="BRAVEN: Survival on the Moon", layout="wide")

# Initialise or restore session state variables
init_state()

# Render the appropriate UI based on the current game state
render()

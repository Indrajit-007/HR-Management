# test_streamlit.py
import streamlit as st
from orchestrator import CollegeAssistantOrchestrator
import os

st.title("Test")

if "orch" not in st.session_state:
    api_key = os.getenv("GROQ_API_KEY")
    st.session_state.orch = CollegeAssistantOrchestrator(api_key)
    st.success("Loaded!")

st.write("If you see this, it works!")
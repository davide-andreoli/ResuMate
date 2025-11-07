import streamlit as st
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.DEBUG)

load_dotenv()


def landing():
    st.markdown("# ResuMate")


pages = st.navigation(
    {
        "Landing": [landing],
        "Resume": ["resume/resume_data.py", "resume/templates.py"],
        "Chat": ["chat/chat.py"],
    }
)
pages.run()

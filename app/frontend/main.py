import streamlit as st
from dotenv import load_dotenv

load_dotenv()


def landing():
    st.markdown("# ApplAI")


pages = st.navigation(
    {
        "Landing": [landing],
        "Resume": ["resume/resume_data.py", "resume/templates.py", "resume/chat.py"],
    }
)
pages.run()

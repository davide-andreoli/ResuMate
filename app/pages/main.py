import streamlit as st
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.DEBUG)

load_dotenv()

pages = {
    "Home": [st.Page("home/home.py", title="Home")],
    "Resume": [
        st.Page("resume/resume_data.py", title="Edit Resume"),
        st.Page("resume/templates.py", title="Templates"),
    ],
    "Chat": [st.Page("chat/chat.py", title="Chat")],
}

pg = st.navigation(pages, expanded=True)
pg.run()

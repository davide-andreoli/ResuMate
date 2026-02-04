import streamlit as st
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO)

load_dotenv()

home_page = st.Page("home/home.py", title="Home")
resumes_page = st.Page("resume/resumes.py", title="Resumes")
edit_resume_page = st.Page("resume/edit.py", title="Edit Resume")
templates_page = st.Page("resume/templates.py", title="Templates")
template_page = st.Page("resume/template.py", title="Template Preview")
chat_page = st.Page("chat/chat.py", title="Chat")
conversations_page = st.Page("chat/conversations.py", title="Conversations")


pages = {
    "Home": [home_page],
    "Resume": [
        resumes_page,
        edit_resume_page,
        templates_page,
        template_page,
    ],
    "Chat": [
        chat_page,
        conversations_page,
    ],
}

pg = st.navigation(pages, position="hidden")
with st.sidebar:
    st.title("ResuMate")

    st.page_link(home_page)

    st.header("Resume")
    st.page_link(resumes_page)
    st.page_link(templates_page)

    st.header("Chat")
    st.page_link(conversations_page)

pg.run()

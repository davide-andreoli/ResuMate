import streamlit as st
from app.frontend.dependencies import get_storage, get_yaml_manager
from jinja2 import Environment, FileSystemLoader, select_autoescape
import asyncio
import sys
from playwright.sync_api import sync_playwright
import io

if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

storage = get_storage()
yaml_manager = get_yaml_manager()


def render_template(resume_path, template_path):
    resume = storage.get_resume(resume_path)
    env = Environment(
        loader=FileSystemLoader(storage.template_folder),
        autoescape=select_autoescape(["html", "xml"]),
    )
    template = env.get_template(template_path)
    return template.render(resume=resume)


def html_to_pdf_bytes(html: str) -> bytes:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.set_content(html, wait_until="networkidle")  # allow CSS/fonts to load
        pdf_bytes = page.pdf(format="A4", print_background=True)  # keep colors
        browser.close()
        return pdf_bytes


st.title("Templates & Export")

st.subheader("Provide Resume YAML")

selected_resume = st.selectbox(
    "Choose from your resumes", options=storage.list_resumes()
)

st.subheader("Select Template")
selected_template = st.selectbox(
    "Choose from your resumes", options=storage.list_templates()
)

html = render_template(selected_resume, selected_template)

st.subheader("Preview")

pdf_bytes = html_to_pdf_bytes(html)

st.pdf(io.BytesIO(pdf_bytes))
st.html(html)

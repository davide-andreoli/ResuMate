import streamlit as st
from app.models.resume import Resume
from datetime import date
from app.models.experience import Experience
from app.models.education import Education
from app.models.link import Link
from app.models.skill import Skill
from app.models.certification import Certification
from app.models.project import Project
from app.models.langauge import Language
from app.frontend.ui_utils.section_renderer import render_pydantic_section
import requests


def load_default_resume() -> Resume:
    return Resume(name="Your Name", date_of_birth=date(2000, 1, 1))


def initialize_basic_fields(resume: Resume):
    """Initialize basic fields in session state if not already present."""
    basic_fields = ["name", "title", "email", "phone"]

    for field in basic_fields:
        session_key = f"basic_{field}"
        if session_key not in st.session_state:
            st.session_state[session_key] = getattr(resume, field, "")


def get_resume_with_current_data() -> Resume:
    """Create a resume object with current session state data."""
    resume = st.session_state["resume"]

    # Update basic fields from session state
    basic_fields = ["name", "title", "email", "phone"]
    for field in basic_fields:
        session_key = f"basic_{field}"
        if session_key in st.session_state:
            setattr(resume, field, st.session_state[session_key])

    return resume


if "resume" not in st.session_state:
    st.session_state["resume"] = None

st.markdown("# Resume Data")

if st.session_state["resume"] is None:
    st.markdown("### How would you like to start?")
    resume_source = st.radio(
        "Start with a resume:", ["Create new", "Select existing", "Upload file"]
    )

    if resume_source == "Create new":
        if st.button("Start new resume"):
            st.session_state["resume"] = load_default_resume()
            keys_to_clear = [
                key
                for key in st.session_state.keys()
                if str(key).endswith("_data") or str(key).startswith("basic_")
            ]
            for key in keys_to_clear:
                del st.session_state[key]
            st.rerun()

    elif resume_source == "Select existing":
        options = requests.get("http://127.0.0.1:8000/resume/list").json()
        selected = st.selectbox("Choose from your resumes", options=options)
        if selected and st.button("Load selected"):
            response = requests.get(f"http://127.0.0.1:8000/resume/{selected}")
            if response.status_code == 200:
                st.session_state["resume"] = Resume(**response.json())
            else:
                st.error("Failed to load resume.")
            keys_to_clear = [
                key
                for key in st.session_state.keys()
                if str(key).endswith("_data") or str(key).startswith("basic_")
            ]
            for key in keys_to_clear:
                del st.session_state[key]
            st.rerun()

    elif resume_source == "Upload file":
        uploaded_file = st.file_uploader("Upload YAML", type=["yml", "yaml"])
        if uploaded_file and st.button("Load uploaded file"):
            response = requests.post(
                "http://127.0.0.1:8000/resume/upload", files={"file": uploaded_file}
            )
            if response.status_code != 200:
                st.error("Failed to upload resume.")

            response = requests.get(
                f"http://127.0.0.1:8000/resume/{uploaded_file.name}"
            )

            if response.status_code != 200:
                st.error("Failed to load uploaded resume.")
            st.session_state["resume"] = Resume(**response.json())
            keys_to_clear = [
                key
                for key in st.session_state.keys()
                if str(key).endswith("_data") or str(key).startswith("basic_")
            ]
            for key in keys_to_clear:
                del st.session_state[key]
            st.rerun()

else:
    resume = st.session_state["resume"]

    initialize_basic_fields(resume)

    st.subheader("Basics")

    st.text_input("Name", key="basic_name")
    st.text_input("Title", key="basic_title")
    st.text_input("Email", key="basic_email")
    st.text_input("Phone", key="basic_phone")

    render_pydantic_section("Experience", Experience, resume, section_key="experience")
    render_pydantic_section("Education", Education, resume, section_key="education")
    render_pydantic_section("Links", Link, resume, section_key="links")
    render_pydantic_section("Skills", Skill, resume, section_key="skills")
    render_pydantic_section("Projects", Project, resume, section_key="projects")
    render_pydantic_section(
        "Certifications", Certification, resume, section_key="certifications"
    )
    render_pydantic_section("Languages", Language, resume, section_key="languages")

    st.subheader("YAML Preview")

    current_resume = get_resume_with_current_data()
    yaml_string = current_resume.dump_to_yaml_string()
    st.code(yaml_string, language="yaml")

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("💾 Save Resume"):
            response = requests.post(
                "http://127.0.0.1:8000/resume/save",
                json={"resume": get_resume_with_current_data()},
            )
            if response.status_code == 200:
                st.success("Resume saved successfully!")
            else:
                st.error("Failed to save resume.")

    with col2:
        if st.button("↩ Back to source selection"):
            st.session_state["resume"] = None
            keys_to_clear = [
                key
                for key in st.session_state.keys()
                if str(key).endswith("_data") or str(key).startswith("basic_")
            ]
            for key in keys_to_clear:
                del st.session_state[key]
            st.rerun()

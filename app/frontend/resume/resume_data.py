import streamlit as st
from app.models.resume import Resume
from app.frontend.dependencies import get_storage, get_yaml_manager
from datetime import date
from app.models.experience import Experience
from app.models.education import Education
from app.models.link import Link
from app.models.skill import Skill
from app.models.certification import Certification
from app.models.project import Project
from app.models.langauge import Language
from app.frontend.ui_utils.section_renderer import render_pydantic_section


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


storage = get_storage()
yaml_manager = get_yaml_manager()

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
        selected = st.selectbox(
            "Choose from your resumes", options=storage.list_resumes()
        )
        if selected and st.button("Load selected"):
            st.session_state["resume"] = storage.get_resume(resume_name=selected)
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
            storage.save_resume(
                uploaded_file.read().decode("utf-8"), uploaded_file.name
            )
            st.session_state["resume"] = storage.get_resume(
                resume_name=uploaded_file.name
            )
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
    yaml_string = yaml_manager.dump_resume_to_yaml_string(current_resume)
    st.code(yaml_string, language="yaml")

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("💾 Save Resume"):
            final_resume = get_resume_with_current_data()
            final_yaml = yaml_manager.dump_resume_to_yaml_string(final_resume)
            storage.save_resume(final_yaml, final_resume.name + ".yaml")
            st.success("Resume saved successfully!")

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

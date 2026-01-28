import streamlit as st
from app.models.resume import Resume
from app.models.experience import Experience
from app.models.education import Education
from app.models.link import Link
from app.models.skill import Skill
from app.models.certification import Certification
from app.models.project import Project
from app.models.langauge import Language
from app.pages.ui_utils.section_renderer import render_pydantic_section
import requests


def initialize_basic_fields(resume: Resume):
    """Initialize basic fields in session state if not already present."""
    basic_fields = ["name", "display_name", "title", "email", "phone"]

    for field in basic_fields:
        session_key = f"basic_{field}"
        if session_key not in st.session_state:
            st.session_state[session_key] = getattr(resume, field, "")


def get_resume_with_current_data() -> Resume:
    """Create a resume object with current session state data."""
    resume = st.session_state["resume"]

    # Update basic fields from session state
    basic_fields = ["name", "display_name", "title", "email", "phone"]
    for field in basic_fields:
        session_key = f"basic_{field}"
        if session_key in st.session_state:
            setattr(resume, field, st.session_state[session_key])

    return resume


if st.query_params.get("resume_id"):
    resume_id = st.query_params["resume_id"]
else:
    # Should not happen as we redirect from conversations page
    raise ValueError("No resume_id provided in query parameters")

if "resume" not in st.session_state:
    response = requests.get(f"http://127.0.0.1:8000/resumes/{resume_id}")
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

st.markdown("# Edit Resume")

resume = st.session_state["resume"]

initialize_basic_fields(resume)

st.subheader("Basics")

st.text_input("Name", key="basic_name")
st.text_input("Display Name", key="basic_display_name")
st.text_input("Title", key="basic_title")
st.text_input("Email", key="basic_email")
st.text_input("Phone", key="basic_phone")

st.markdown("## Sections")

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
        response = requests.put(
            f"http://127.0.0.1:8000/resumes/{current_resume.id}",
            json=get_resume_with_current_data().model_dump(mode="json"),
        )
        if response.status_code == 204:
            st.success("Resume saved successfully!")
        else:
            st.error("Failed to save resume.")

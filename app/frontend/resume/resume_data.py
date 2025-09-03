import streamlit as st
from app.models.resume import Resume
from app.frontend.dependencies import get_storage, get_yaml_manager
from datetime import date
from app.models.experience import Experience
from app.models.education import Education
from app.models.link import Link
from app.models.skill import Skill
from app.frontend.renderer import render_pydantic_section


def load_default_resume() -> Resume:
    return Resume(name="Your Name", date_of_birth=date(2000, 1, 1))


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
            st.rerun()

    elif resume_source == "Select existing":
        selected = st.selectbox(
            "Choose from your resumes", options=storage.list_resumes()
        )
        if selected and st.button("Load selected"):
            st.session_state["resume"] = storage.get_resume(resume_name=selected)
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
            st.rerun()

else:
    resume = st.session_state["resume"]
    st.subheader("Basics")
    resume.name = st.text_input("Name", resume.name or "")
    resume.title = st.text_input("Title", resume.title or "")
    resume.email = st.text_input("Email", resume.email or "")
    resume.phone = st.text_input("Phone", resume.phone or "")

    render_pydantic_section("Experience", Experience, resume, section_key="experience")
    render_pydantic_section("Education", Education, resume, section_key="education")
    render_pydantic_section("Links", Link, resume, section_key="links")
    render_pydantic_section("Skills", Skill, resume, section_key="skills")

    st.subheader("YAML Preview")
    yaml_string = yaml_manager.dump_resume_to_yaml_string(resume)
    st.code(yaml_string, language="yaml")

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("💾 Save Resume"):
            storage.save_resume(yaml_string, resume.name + ".yaml")
            st.success("Resume saved successfully!")

    with col2:
        if st.button("↩ Back to source selection"):
            st.session_state["resume"] = None
            st.rerun()

import streamlit as st
from app.models.resume import Resume
from app.frontend.dependencies import get_storage, get_yaml_manager
from datetime import date
from app.models.experience import Experience
from app.models.education import Education
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

    st.subheader("Experience")
    if "experience" not in st.session_state:
        st.session_state.experience = resume.experience or []

    if st.button("➕ Add Experience"):
        st.session_state.experience.append(Experience(company="", role=""))

    for i, exp in enumerate(st.session_state.experience):
        with st.expander(f"Experience {i+1}: {exp.company or 'New'}"):
            exp.company = st.text_input(
                "Company", exp.company, key=f"experience_{i}_company"
            )
            exp.location = st.text_input(
                "Location", exp.location, key=f"experience_{i}_location"
            )
            exp.role = st.text_input("Role", exp.role, key=f"experience_{i}_role")
            exp.start = st.date_input(
                "Start Date", exp.start, key=f"experience_{i}_start"
            )
            exp.end = st.date_input("End Date", exp.end, key=f"experience_{i}_end")
            exp.summary = st.text_area(
                "Summary", exp.summary, key=f"experience_{i}_summary"
            )
            if f"experience_{i}_bullets" not in st.session_state:
                st.session_state[f"experience_{i}_bullets"] = exp.bullets or []
            if st.button("➕ Add Bullet Point", key=f"experience_{i}_add_bullet"):
                st.session_state[f"experience_{i}_bullets"].append("")

            for j, bullet in enumerate(st.session_state[f"experience_{i}_bullets"]):
                col1, col2 = st.columns([5, 1], vertical_alignment="center")
                with col1:
                    st.session_state[f"experience_{i}_bullets"][j] = st.text_input(
                        "Bullet", bullet, key=f"experience_{i}_bullet_{j}"
                    )
                with col2:
                    if st.button(
                        "🗑️ Delete bullet", key=f"experience_{i}_delete_bullet_{j}"
                    ):
                        st.session_state[f"experience_{i}_bullets"].pop(j)
                        st.rerun()

            exp.bullets = st.session_state[f"experience_{i}_bullets"]

            if st.button(
                "🗑️ Delete experience", key=f"experience_{i}_delete_experience"
            ):
                st.session_state.experience.pop(i)
                st.rerun()

    resume.experience = st.session_state.experience

    render_pydantic_section("Education", Education, resume, section_key="education")

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

import streamlit as st
from app.models.resume import Resume
from datetime import date, datetime
import requests

# TODO: delete a resume
# TODO: rename a resume


def load_default_resume() -> Resume:
    return Resume(
        name="Your Name", display_name="Your Resume", date_of_birth=date(2000, 1, 1)
    )


st.markdown("# Manage Resumes")

col1, col2 = st.columns([1, 1])
with col1:
    if st.button("➕ Create New Resume", key="new_resume_button"):
        new_resume = load_default_resume()
        response = requests.post(
            "http://127.0.0.1:8000/resumes/",
            json=new_resume.model_dump(mode="json"),
        )
        if response.status_code == 201:
            st.switch_page("resume/edit.py", query_params={"resume_id": new_resume.id})
        else:
            st.error("Failed to save resume.")

with col2:
    uploaded_file = st.file_uploader("Upload YAML", type=["yml", "yaml"])
    if uploaded_file and st.button("Load uploaded file"):
        response = requests.post(
            "http://127.0.0.1:8000/resumes/", files={"file": uploaded_file}
        )
        if response.status_code != 201:
            st.error("Failed to upload resume.")

options = requests.get("http://127.0.0.1:8000/resumes").json()


for resume_info in options:
    with st.container(border=True):
        col1, col2 = st.columns([4, 2])
        with col1:
            title = (
                resume_info["display_name"]
                if resume_info.get("display_name")
                else "Unnamed resume"
            )
            st.subheader(title)
        with col2:
            updated_at = resume_info.get("updated_at", "")
            updated_at = datetime.fromisoformat(updated_at)
            st.caption(f"Last updated: {updated_at.strftime('%Y-%m-%d %H:%M:%S')}")
        col3, col4 = st.columns([4, 2])
        with col3:
            st.caption(resume_info.get("id", "No id available."))
        with col4:
            if st.button(
                "Delete",
                key=f"delete_{resume_info['id']}",
                use_container_width=True,
            ):
                requests.delete(f"http://127.0.0.1:8000/resumes/{resume_info['id']}")
                st.rerun()
        if st.button(
            "Edit resume",
            key=resume_info["id"],
            use_container_width=True,
        ):
            st.switch_page(
                "resume/edit.py",
                query_params={"resume_id": resume_info["id"]},
            )

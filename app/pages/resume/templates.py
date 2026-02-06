import streamlit as st
import requests

from app.models.template import Template

st.markdown("# Manage Templates")

col1, col2 = st.columns([1, 1])
with col1:
    if st.button("➕ Create New Template", key="new_template_button"):
        # TODO: this should probably be done in the template edit page, which should create a default template if no id is provided
        new_template = Template(
            name="New Template",
            description="Describe your template here.",
            variables=[],
            display_name="Template Preview",
            author="Author Name",
            version=1,
            html_content="<h1>Template Preview</h1><p>This is a preview of your template.</p>",
        )
        response = requests.post(
            "http://127.0.0.1:8000/templates/",
            json=new_template.model_dump(mode="json"),
        )
        if response.status_code == 201:
            st.switch_page(
                "resume/template.py", query_params={"template_id": new_template.id}
            )
        else:
            st.error("Failed to save template.")


with col2:
    uploaded_file = st.file_uploader("Upload HTML Template", type=["html.j2"])
    if uploaded_file and st.button("Load uploaded file"):
        response = requests.post(
            "http://127.0.0.1:8000/templates/", files={"file": uploaded_file}
        )
        if response.status_code != 201:
            st.error("Failed to upload template.")

options = requests.get("http://127.0.0.1:8000/templates/").json()

for template_info in options:
    with st.container(border=True):
        # TODO: add template preview thumbnail if available
        col1, col2 = st.columns([4, 2])
        with col1:
            title = (
                template_info["name"]
                if template_info.get("name")
                else "Unnamed template"
            )
            st.subheader(title)
            description = (
                template_info["description"]
                if template_info.get("description")
                else "No description available."
            )
            st.caption(description)
            author = (
                template_info["author"]
                if template_info.get("author")
                else "No author available."
            )
            st.caption(author)
        with col2:
            version = template_info.get("version", "")
            st.caption(f"Version: {version}")
        col3, col4 = st.columns([4, 2])
        with col3:
            st.caption(template_info.get("id", "No id available."))
        with col4:
            if st.button("Delete", key=f"delete_template_{template_info['id']}"):
                requests.delete(
                    f"http://127.0.0.1:8000/templates/{template_info['id']}"
                )
                st.rerun()
        if st.button("Edit", key=f"edit_template_{template_info['id']}"):
            st.switch_page(
                "resume/template.py", query_params={"template_id": template_info["id"]}
            )
        if st.button("Render", key=f"render_template_{template_info['id']}"):
            st.switch_page(
                "resume/render.py", query_params={"template_id": template_info["id"]}
            )

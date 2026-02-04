import streamlit as st
import requests

st.markdown("# Manage Templates")

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
                st.info("Template deletion not yet implemented.")
        if st.button("Preview", key=f"preview_template_{template_info['id']}"):
            st.switch_page(
                "resume/template.py", query_params={"template_id": template_info["id"]}
            )

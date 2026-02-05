import streamlit as st
from app.models.template import Template
import requests
from typing import Dict, Any

st.markdown("# Edit Template")

if st.query_params.get("template_id"):
    template_id = st.query_params["template_id"]
    response = requests.get(f"http://127.0.0.1:8000/templates/{template_id}")
    if response.status_code == 200:
        template = Template(**response.json())
    else:
        st.error("Failed to load template.")
else:
    template = Template(
        name="New Template",
        description="Describe your template here.",
        variables={},
        display_name="Template Preview",
        author="Author Name",
        version=1,
        html_content="<h1>Template Preview</h1><p>This is a preview of your template.</p>",
    )
    st.experimental_set_query_params(template_id=template.id)
    response = requests.post(
        "http://127.0.0.1:8000/templates/",
        json=template.model_dump(mode="json"),
        headers={"Content-Type": "application/json"},
    )

st.subheader("Template Details")

st.text_input("Name", key="template_name", value=template.name)
st.text_input("Display Name", key="template_display_name", value=template.display_name)
st.text_area(
    "Description", key="template_description", value=template.description, height=100
)
st.text_input("Author", key="template_author", value=template.author)
st.number_input("Version", key="template_version", value=template.version, min_value=1)
st.text_area(
    "HTML Content", key="template_html_content", value=template.html_content, height=500
)

with st.expander("Variables"):
    pass


if st.button("Save Template"):
    template_data: Dict[str, Any] = {
        "id": template.id,
        "name": st.session_state["template_name"],
        "display_name": st.session_state["template_display_name"],
        "description": st.session_state["template_description"],
        "author": st.session_state["template_author"],
        "version": st.session_state["template_version"],
        "html_content": st.session_state["template_html_content"],
    }
    response = requests.put(
        f"http://127.0.0.1:8000/templates/{template.id}",
        json=template_data,
        headers={"Content-Type": "application/json"},
    )
    if response.status_code == 204:
        st.success("Template saved successfully.")
    else:
        st.error("Failed to save template.")

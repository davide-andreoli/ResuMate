import streamlit as st
import asyncio
import sys
import io
from typing import Dict, Any
import requests
from app.models.template import Template, TemplateVariable


if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

if st.query_params.get("template_id"):
    template_id = st.query_params["template_id"]
else:
    # Should not happen as we redirect from conversations page
    raise ValueError("No template_id provided in query parameters")

if "template" not in st.session_state:
    response = requests.get(f"http://127.0.0.1:8000/templates/{template_id}")
    if response.status_code == 200:
        st.session_state["template"] = Template(**response.json())
    else:
        st.error("Failed to load template.")


def create_input_widget(key: str, definition: TemplateVariable):
    """
    Accept a VariableDefinition and render the appropriate Streamlit widget.
    Returns the actual value chosen by the user.
    """
    label = definition.label or key
    vtype = definition.type
    default = definition.default
    options = definition.options or []

    if vtype == "multiselect":
        return st.multiselect(label, options, default=default or [])
    if vtype == "select":
        default_index = options.index(default) if (default in options) else 0
        return st.selectbox(label, options, index=default_index)
    if vtype in ("checkbox", "bool"):
        return st.checkbox(label, value=bool(default))
    if vtype == "number":
        if isinstance(default, int):
            return st.number_input(label, value=default, step=1)
        if isinstance(default, float):
            return st.number_input(label, value=default, format="%.2f")
        return st.number_input(label, value=0)
    if vtype == "textarea":
        return st.text_area(label, value=str(default or ""))
    if vtype == "color":
        return st.color_picker(label, value=str(default or "#000000"))
    # fallback to text input
    return st.text_input(label, value=str(default or ""))


st.title("Templates & Export")

st.subheader("Provide Resume YAML")
resume_options = requests.get("http://127.0.0.1:8000/resumes").json()
selected_resume = st.selectbox("Choose from your resumes", options=resume_options)

selected_template = st.session_state["template"]


template_variable_definitions = selected_template.variables

template_variable_values: Dict[str, Any] = {}
if template_variable_definitions:
    st.subheader("Template Options")
    for variable_key, variable_definition in template_variable_definitions.items():
        template_variable_values[variable_key] = create_input_widget(
            variable_key, variable_definition
        )

st.subheader("Preview")

if st.button("Render Preview"):
    with st.spinner("Rendering template and generating PDF..."):
        render_request_payload = {
            "resume_id": selected_resume["id"],
            "template_variables": template_variable_values,
        }
        render_request_url = (
            f"http://127.0.0.1:8000/templates/{selected_template.id}/renders"
        )
        render_html_request_headers = {"Accept": "text/html"}
        render_pdf_request_headers = {"Accept": "application/pdf"}

        render_html = requests.post(
            render_request_url,
            json=render_request_payload,
            headers=render_html_request_headers,
        ).content

        pdf_bytes = requests.post(
            render_request_url,
            json=render_request_payload,
            headers=render_pdf_request_headers,
        ).content

        st.pdf(io.BytesIO(pdf_bytes))
        st.download_button(
            "Download PDF",
            data=io.BytesIO(pdf_bytes),
            file_name=selected_resume["id"] + ".pdf",
            mime="application/pdf",
        )
        st.download_button(
            "Download HTML",
            data=render_html,
            file_name=selected_resume["id"] + ".html",
            mime="text/html",
        )
else:
    st.info(
        "Click 'Render Preview' to generate HTML/PDF. This avoids blocking the UI during initial page build."
    )

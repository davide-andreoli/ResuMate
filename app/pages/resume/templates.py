import streamlit as st
import asyncio
import sys
import io
from typing import Dict, Optional, Any, List, Literal
from pydantic import BaseModel
import requests


if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())


class TemplateVariable(BaseModel):
    type: Literal[
        "text",
        "select",
        "multiselect",
        "checkbox",
        "bool",
        "number",
        "textarea",
        "color",
    ] = "text"
    default: Optional[Any] = None
    options: Optional[List[Any]] = None
    label: Optional[str] = None
    description: Optional[str] = None


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
resume_options = requests.get("http://127.0.0.1:8000/resume/list").json()
selected_resume = st.selectbox("Choose from your resumes", options=resume_options)

st.subheader("Select Template")
template_options = requests.get("http://127.0.0.1:8000/template/list").json()
selected_template = st.selectbox("Choose from your templates", options=template_options)

template_variable_definitions = requests.get(
    f"http://127.0.0.1:8000/template/{selected_template}/variables"
).json()
template_variable_definitions = {
    key: TemplateVariable.model_validate(value)
    for key, value in template_variable_definitions.items()
    if isinstance(value, dict)
}
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
        html = requests.post(
            f"http://127.0.0.1:8000/template/{selected_template}/render/{selected_resume}",
            json={"template_variables": template_variable_values},
        ).json()["html"]

        pdf_bytes = requests.post(
            f"http://127.0.0.1:8000/template/{selected_template}/render/{selected_resume}/pdf",
            json={"template_variables": template_variable_values},
        ).content

        st.pdf(io.BytesIO(pdf_bytes))
        st.download_button(
            "Download PDF",
            data=io.BytesIO(pdf_bytes),
            file_name=selected_resume + ".pdf",
            mime="application/pdf",
        )
        st.download_button(
            "Download HTML",
            data=html,
            file_name=selected_resume + ".html",
            mime="text/html",
        )
else:
    st.info(
        "Click 'Render Preview' to generate HTML/PDF. This avoids blocking the UI during initial page build."
    )

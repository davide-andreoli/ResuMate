import streamlit as st
from app.api.deps import get_storage, get_yaml_manager
from jinja2 import Environment, FileSystemLoader, select_autoescape
import asyncio
import sys
from playwright.sync_api import sync_playwright
import io
import os
import re
import yaml
from typing import Dict, Optional, Any, List, Literal
from pydantic import BaseModel, ValidationError

if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

storage = get_storage()
yaml_manager = get_yaml_manager()


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


def parse_template_variables(template_name: str) -> Dict[str, TemplateVariable]:
    """
    Look for a YAML front-matter block at the top of the template and load variable
    declarations from key 'variables'. Returns a dict of TemplateVariable instances.
    """
    path = os.path.join(storage.template_folder, template_name)
    try:
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
    except FileNotFoundError:
        return {}

    front_matter_match = re.match(r"\s*---\s*\n(.*?)\n---\s*\n", text, re.S)
    if not front_matter_match:
        return {}
    try:
        front_matter: Dict[str, Any] = yaml.safe_load(front_matter_match.group(1)) or {}
        raw_vars: Dict[str, Any] = front_matter.get("variables", {})

        normalized: Dict[str, TemplateVariable] = {}
        for name, definition in raw_vars.items():
            if not isinstance(definition, dict):
                continue
            try:
                normalized[name] = TemplateVariable.model_validate(definition)
            except ValidationError:
                continue

        return normalized
    except Exception:
        return {}


def _load_template_without_front_matter(template_name: str) -> str:
    path = os.path.join(storage.template_folder, template_name)
    try:
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
    except FileNotFoundError:
        return ""
    # remove leading YAML front-matter block between the first two --- lines
    cleaned = re.sub(r"^\s*---\s*\n(.*?)\n---\s*\n", "", text, flags=re.S)
    return cleaned


def render_template(
    resume_name: str,
    template_name: str,
    template_variables: Optional[Dict[str, Any]] = None,
):
    resume = storage.get_resume(resume_name).visible_only()
    env = Environment(
        loader=FileSystemLoader(storage.template_folder),
        autoescape=select_autoescape(["html", "xml"]),
    )
    template_source = _load_template_without_front_matter(template_name)
    if not template_source:
        template = env.get_template(template_name)
    else:
        template = env.from_string(template_source)
    render_context: Dict[str, Any] = {"resume": resume}
    if template_variables:
        render_context["variables"] = template_variables
    return template.render(**render_context)


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


def html_to_pdf_bytes(html: str) -> bytes:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.set_content(html, wait_until="networkidle")  # allow CSS/fonts to load
        pdf_bytes = page.pdf(format="A4", print_background=True)  # keep colors
        browser.close()
        return pdf_bytes


st.title("Templates & Export")

st.subheader("Provide Resume YAML")

selected_resume = st.selectbox(
    "Choose from your resumes", options=storage.list_resumes()
)

st.subheader("Select Template")
selected_template = st.selectbox(
    "Choose from your resumes", options=storage.list_templates()
)

template_variable_definitions = parse_template_variables(selected_template)
template_variable_values: Dict[str, Any] = {}
if template_variable_definitions:
    st.subheader("Template Options")
    for variable_key, variable_definition in template_variable_definitions.items():
        template_variable_values[variable_key] = create_input_widget(
            variable_key, variable_definition
        )

html = render_template(
    selected_resume, selected_template, template_variables=template_variable_values
)

st.subheader("Preview")

pdf_bytes = html_to_pdf_bytes(html)

st.pdf(io.BytesIO(pdf_bytes))
st.download_button(
    "Download PDF",
    data=io.BytesIO(pdf_bytes),
    file_name=selected_resume + ".pdf",
    mime="application/pdf",
)
st.download_button(
    "Download HTML", data=html, file_name=selected_resume + ".html", mime="text/html"
)

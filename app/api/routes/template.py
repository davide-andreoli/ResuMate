import asyncio
from fastapi.responses import JSONResponse
from fastapi import APIRouter, Depends, Body, Response
from jinja2 import Environment, FileSystemLoader, select_autoescape
from pydantic import BaseModel, ValidationError
from app.api.dependencies.dependencies import get_storage
from app.core.storage import LocalDocumentStorage
from typing import Dict, Literal, Optional, Any, List
import os
import re
import yaml
import logging
from playwright.async_api import async_playwright
import sys

logger = logging.getLogger(__name__)

template_router = APIRouter(prefix="/template", tags=["template"])


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


class ListTemplatesResponse(BaseModel):
    templates: list[str]


class RenderRequest(BaseModel):
    template_variables: Optional[Dict[str, Any]] = None


@template_router.get("/list", response_model=List[str])
async def list_templates(storage: LocalDocumentStorage = Depends(get_storage)):
    templates = storage.list_templates()
    return templates


@template_router.get(
    "/{template_name}/variables", response_model=Dict[str, TemplateVariable]
)
async def get_template_variables(
    template_name: str, storage: LocalDocumentStorage = Depends(get_storage)
):
    path = os.path.join(storage.template_folder, template_name)
    try:
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
    except FileNotFoundError:
        return dict[str, TemplateVariable]()

    front_matter_match = re.match(r"\s*---\s*\n(.*?)\n---\s*\n", text, re.S)
    if not front_matter_match:
        return dict[str, TemplateVariable]()
    try:
        front_matter: dict[str, Any] = yaml.safe_load(front_matter_match.group(1)) or {}
        raw_vars: dict[str, Any] = front_matter.get("variables", {})

        normalized: dict[str, TemplateVariable] = {}
        for name, definition in raw_vars.items():
            if not isinstance(definition, dict):
                continue
            try:
                normalized[name] = TemplateVariable.model_validate(definition)
            except ValidationError:
                continue

        return normalized
    except Exception:
        return dict[str, TemplateVariable]()


def _render_template_to_html(
    template_name: str,
    resume_name: str,
    template_variables: Optional[Dict[str, Any]],
    storage: LocalDocumentStorage,
) -> str:
    resume = storage.get_resume(resume_name=resume_name)
    if not resume:
        return ""

    env = Environment(
        loader=FileSystemLoader(storage.template_folder),
        autoescape=select_autoescape(["html", "xml"]),
    )

    path = os.path.join(storage.template_folder, template_name)
    try:
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
    except FileNotFoundError:
        return ""
    # remove leading YAML front-matter block between the first two --- lines
    template_source = re.sub(r"^\s*---\s*\n(.*?)\n---\s*\n", "", text, flags=re.S)

    if not template_source:
        template = env.get_template(template_name)
    else:
        template = env.from_string(template_source)
    render_context: Dict[str, Any] = {"resume": resume}
    render_context["variables"] = template_variables or {}
    return template.render(**render_context)


@template_router.post("/{template_name}/render/{resume_name}")
async def render_template_endpoint(
    resume_name: str,
    template_name: str,
    payload: RenderRequest = Body(default=None),
    storage: LocalDocumentStorage = Depends(get_storage),
):
    resume = storage.get_resume(resume_name=resume_name)
    if not resume:
        return JSONResponse(status_code=404, content={"message": "Resume not found"})

    html = _render_template_to_html(
        template_name,
        resume_name,
        payload.template_variables,
        storage,
    )
    return JSONResponse(content={"html": html})


# TODO: it might make sense to implement an endpoint that returns both HTML and PDF together
@template_router.post("/{template_name}/render/{resume_name}/pdf")
async def render_template_pdf_endpoint(
    resume_name: str,
    template_name: str,
    payload: RenderRequest = Body(default=None),
    storage: LocalDocumentStorage = Depends(get_storage),
):
    if sys.platform.startswith("win"):
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

    resume = storage.get_resume(resume_name=resume_name)
    if not resume:
        return JSONResponse(status_code=404, content={"message": "Resume not found"})

    html_content = _render_template_to_html(
        template_name,
        resume_name,
        payload.template_variables,
        storage,
    )

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.set_content(
            html_content, wait_until="networkidle"
        )  # allow CSS/fonts to load
        pdf_bytes = await page.pdf(format="A4", print_background=True)  # keep colors
        await browser.close()

    return Response(content=pdf_bytes, media_type="application/pdf")

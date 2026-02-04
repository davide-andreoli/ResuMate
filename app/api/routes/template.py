import asyncio
from fastapi import APIRouter, Depends, Body, HTTPException, Request, Response
from jinja2 import Environment, FileSystemLoader, select_autoescape
from pydantic import BaseModel
from app.api.dependencies.dependencies import get_storage
from app.core.storage import LocalDocumentStorage
from app.models.template import Template, TemplateDetails
from typing import Dict, Optional, Any, List
import os
import re
import logging
from playwright.async_api import async_playwright
import sys

logger = logging.getLogger(__name__)

template_router = APIRouter(prefix="/templates", tags=["template"])


class ListTemplatesResponse(BaseModel):
    templates: list[str]


class RenderRequest(BaseModel):
    resume_id: str
    template_variables: Optional[Dict[str, Any]] = None


@template_router.get("/", response_model=List[TemplateDetails])
async def list_templates(
    storage: LocalDocumentStorage = Depends(get_storage),
) -> List[TemplateDetails]:
    templates = storage.list_templates()
    template_details = [template.get_details() for template in templates]
    return template_details


@template_router.get("/{template_id}", response_model=Template)
async def get_template(
    template_id: str, storage: LocalDocumentStorage = Depends(get_storage)
) -> Template:
    template = storage.get_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template


@template_router.post("/{template_id}/renders", status_code=201)
async def render_template_endpoint(
    template_id: str,
    request: Request,
    payload: RenderRequest = Body(default=None),
    storage: LocalDocumentStorage = Depends(get_storage),
):
    accept_header = request.headers.get("accept", "")
    if sys.platform.startswith("win"):
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

    resume = storage.get_resume(resume_id=payload.resume_id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    env = Environment(
        loader=FileSystemLoader(storage.template_folder),
        autoescape=select_autoescape(["html", "xml"]),
    )

    path = os.path.join(storage.template_folder, template_id + ".html.j2")
    try:
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Template not found")
    # remove leading YAML front-matter block between the first two --- lines
    template_source = re.sub(r"^\s*---\s*\n(.*?)\n---\s*\n", "", text, flags=re.S)

    if not template_source:
        template = env.get_template(template_id)
    else:
        template = env.from_string(template_source)
    render_context: Dict[str, Any] = {"resume": resume}
    render_context["variables"] = payload.template_variables or {}
    html_content = template.render(**render_context)

    if not html_content:
        raise HTTPException(status_code=404, detail="Template rendering failed")

    if "text/html" in accept_header:
        storage.save_rendered_html(
            html_content, render_id=f"{payload.resume_id}_{template_id}"
        )
        location_url = f"/renders/htmls/{payload.resume_id}_{template_id}.html"
        headers = {"Location": location_url}
        return Response(content=html_content, media_type="text/html", headers=headers)

    if "application/pdf" in accept_header:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.set_content(
                html_content, wait_until="networkidle"
            )  # allow CSS/fonts to load
            pdf_bytes = await page.pdf(
                format="A4", print_background=True
            )  # keep colors
            await browser.close()
        storage.save_rendered_pdf(
            pdf_bytes, render_id=f"{payload.resume_id}_{template_id}"
        )
        location_url = f"/renders/pdfs/{payload.resume_id}_{template_id}.pdf"
        headers = {"Location": location_url}
        return Response(
            content=pdf_bytes, media_type="application/pdf", headers=headers
        )

    raise HTTPException(status_code=406, detail="Not Acceptable")

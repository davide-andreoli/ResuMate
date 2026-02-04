import asyncio
import sys
from typing import Dict, Optional, Any, List, Literal
from pydantic import BaseModel, Field, ValidationError
import re

import yaml

from app.models.cv_item import short_id


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


class TemplateDetails(BaseModel):
    id: str
    name: str
    display_name: str
    author: Optional[str] = None
    description: Optional[str] = None
    version: int


class Template(BaseModel):
    id: str = Field(default_factory=lambda: short_id("tmp_"))
    name: str
    display_name: str
    description: Optional[str] = None
    author: Optional[str] = None
    version: int = 1
    variables: Dict[str, TemplateVariable] = Field(default_factory=dict)
    html_content: str

    def get_details(self) -> TemplateDetails:
        return TemplateDetails(
            id=self.id,
            name=self.name,
            display_name=self.display_name,
            author=self.author,
            description=self.description,
            version=self.version,
        )

    @classmethod
    def load_from_file_content(cls, file_content: str) -> "Template":
        front_matter_match = re.match(r"\s*---\s*\n(.*?)\n---\s*\n", file_content, re.S)
        if not front_matter_match:
            return cls(
                name="Unnamed",
                display_name="Unnamed Template",
                html_content=file_content,
            )

        try:
            front_matter: dict[str, Any] = (
                yaml.safe_load(front_matter_match.group(1)) or {}
            )
        except Exception:
            return cls(
                name="Unnamed",
                display_name="Unnamed Template",
                html_content=file_content,
            )
        if front_matter:
            front_matter_vars: dict[str, Any] = front_matter.get("variables", {})
            front_matter_details: dict[str, Any] = front_matter.get("details", {})

            template_name = front_matter_details.get("name", "Unnamed")
            display_name = front_matter_details.get("display_name", "Unnamed Template")
            id = front_matter_details.get("id", short_id("tmp_"))
            description = front_matter_details.get("description", None)

            variables: Dict[str, TemplateVariable] = {}

            for name, definition in front_matter_vars.items():
                if not isinstance(definition, dict):
                    continue
                try:
                    variables[name] = TemplateVariable.model_validate(definition)
                except ValidationError:
                    continue

            return cls(
                id=id,
                name=template_name,
                display_name=display_name,
                description=description,
                variables=variables,
                html_content=re.sub(
                    r"\s*---\s*\n(.*?)\n---\s*\n", "", file_content, count=1, flags=re.S
                ),
            )
        else:
            return cls(
                name="Unnamed",
                display_name="Unnamed Template",
                html_content=file_content,
            )

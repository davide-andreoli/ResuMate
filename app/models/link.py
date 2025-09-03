from enum import StrEnum
from pydantic import BaseModel, HttpUrl, model_validator
from typing import Optional, Literal, Self


class LinkType(StrEnum):
    WEBSITE = "website"
    GITHUB = "github"
    LINKEDIN = "linkedin"


DEFAULT_ICONS = {
    "website": "icons/website.png",
    "github": "icons/github.png",
    "linkedin": "icons/linkedin.png",
}


class Link(BaseModel):
    label: str = ""
    url: HttpUrl = HttpUrl("https://example.com")
    link_type: Literal["website", "github", "linkedin"] = "website"
    link_icon: Optional[str] = None
    schema_version: int = 1

    @model_validator(mode="after")
    def insert_icon_path(self) -> Self:
        if self.link_icon is None:
            self.link_icon = DEFAULT_ICONS[self.link_type]
        return self

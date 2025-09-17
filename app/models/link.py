from pydantic import BaseModel, HttpUrl
from typing import Optional, Literal


class Link(BaseModel):
    label: str = ""
    url: HttpUrl = HttpUrl("https://example.com")
    link_type: Literal["website", "github", "linkedin"] = "website"
    visible: bool = True
    schema_version: int = 1

    @property
    def link_icon(self) -> Optional[str]:
        default_icons = {
            "website": "icons/website.png",
            "github": "icons/github.png",
            "linkedin": "icons/linkedin.png",
        }
        return default_icons.get(self.link_type)

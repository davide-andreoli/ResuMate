from pydantic import BaseModel, HttpUrl
from typing import Optional, Literal
import os
import base64
import mimetypes


class Link(BaseModel):
    label: str = ""
    url: HttpUrl = HttpUrl("https://example.com")
    link_type: Literal["website", "github", "linkedin"] = "website"
    visible: bool = True
    schema_version: int = 1

    @property
    def link_icon(self) -> Optional[str]:
        """
        Return a data URI for the icon if the corresponding file exists under the
        repository's `documents` folder. Falls back to the relative path (e.g.
        `icons/github.png`) if the file can't be read. This keeps templates
        unchanged while making icons renderable even when no static server is
        available.
        """
        default_icons = {
            "website": "icons/website.png",
            "github": "icons/github.png",
            "linkedin": "icons/linkedin.png",
        }
        rel_path = default_icons.get(self.link_type)
        if not rel_path:
            return None

        candidate = os.path.abspath(os.path.join("documents", rel_path))
        try:
            if os.path.exists(candidate) and os.path.isfile(candidate):
                mime, _ = mimetypes.guess_type(candidate)
                if not mime:
                    mime = "application/octet-stream"
                with open(candidate, "rb") as f:
                    data = f.read()
                b64 = base64.b64encode(data).decode("ascii")
                return f"data:{mime};base64,{b64}"
        except Exception:
            pass

        return rel_path

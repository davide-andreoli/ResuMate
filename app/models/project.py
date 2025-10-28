from pydantic import Field, HttpUrl
from typing import Optional, List
from app.models.cv_item import CvItem


class Project(CvItem):
    name: str = ""
    description: Optional[str] = None
    technologies: List[str] = Field(default_factory=list[str])
    link: Optional[HttpUrl] = None

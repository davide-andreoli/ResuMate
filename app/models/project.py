from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List


class Project(BaseModel):
    name: str = ""
    description: Optional[str] = None
    technologies: List[str] = Field(default_factory=list[str])
    link: Optional[HttpUrl] = None
    visible: bool = True
    schema_version: int = 1

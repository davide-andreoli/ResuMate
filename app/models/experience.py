from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date


class Experience(BaseModel):
    company: str = ""
    role: str = ""
    start: Optional[date] = None
    end: Optional[date] = None
    location: Optional[str] = None
    summary: Optional[str] = None
    bullets: List[str] = Field(default_factory=list)
    schema_version: int = 1

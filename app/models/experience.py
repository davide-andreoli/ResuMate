from pydantic import Field
from typing import List, Optional
from datetime import date
from app.models.cv_item import CvItem


class Experience(CvItem):
    company: str = ""
    role: str = ""
    start: Optional[date] = None
    end: Optional[date] = None
    location: Optional[str] = None
    summary: Optional[str] = None
    bullets: List[str] = Field(default_factory=list)

from pydantic import BaseModel
from typing import Optional
from datetime import date


class Education(BaseModel):
    institution: str = ""
    degree: str = ""
    start: Optional[date] = None
    end: Optional[date] = None
    details: Optional[str] = None
    location: Optional[str] = None
    schema_version: int = 1

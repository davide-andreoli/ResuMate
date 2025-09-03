from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from datetime import date
from app.models.education import Education
from app.models.experience import Experience
from app.models.link import Link
from app.models.skill import Skill


class Resume(BaseModel):
    name: str
    date_of_birth: date
    title: Optional[str] = None
    email: Optional[EmailStr] = "mail@example.com"
    phone: Optional[str] = None
    location: Optional[str] = None
    summary: Optional[str] = None
    links: List[Link] = Field(default_factory=list[Link])
    skills: List[Skill] = Field(default_factory=list[Skill])
    experience: List[Experience] = Field(default_factory=list[Experience])
    education: List[Education] = Field(default_factory=list[Education])
    # schema versioning for future migrations
    schema_version: int = 1

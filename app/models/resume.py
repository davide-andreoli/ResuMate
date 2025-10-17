from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from datetime import date
from app.models.education import Education
from app.models.experience import Experience
from app.models.link import Link
from app.models.skill import Skill
from app.models.certification import Certification
from app.models.project import Project
from app.models.langauge import Language


class Resume(BaseModel):
    name: str
    date_of_birth: date
    title: Optional[str] = None
    email: Optional[EmailStr] = "mail@example.com"
    phone: Optional[str] = None
    location: Optional[str] = None
    summary: Optional[str] = None
    created_at: date = Field(default_factory=date.today)
    updated_at: date = Field(default_factory=date.today)
    links: List[Link] = Field(default_factory=list[Link])
    skills: List[Skill] = Field(default_factory=list[Skill])
    experience: List[Experience] = Field(default_factory=list[Experience])
    education: List[Education] = Field(default_factory=list[Education])
    certifications: List[Certification] = Field(default_factory=list[Certification])
    projects: List[Project] = Field(default_factory=list[Project])
    languages: List[Language] = Field(default_factory=list[Language])
    # schema versioning for future migrations
    schema_version: int = 1

    def visible_only(self) -> "Resume":
        """
        Return a deep copy of this Resume where each top-level collection
        contains only items with is_visible == True.
        Items without an is_visible attribute are kept by default.
        """
        filtered = self.model_copy(deep=True)
        filtered.links = [
            link for link in filtered.links if getattr(link, "is_visible", True)
        ]
        filtered.skills = [
            skill for skill in filtered.skills if getattr(skill, "is_visible", True)
        ]
        filtered.experience = [
            experience_item
            for experience_item in filtered.experience
            if getattr(experience_item, "is_visible", True)
        ]
        filtered.education = [
            education_item
            for education_item in filtered.education
            if getattr(education_item, "is_visible", True)
        ]
        filtered.certifications = [
            certification
            for certification in filtered.certifications
            if getattr(certification, "is_visible", True)
        ]
        filtered.projects = [
            project
            for project in filtered.projects
            if getattr(project, "is_visible", True)
        ]
        filtered.languages = [
            language
            for language in filtered.languages
            if getattr(language, "is_visible", True)
        ]
        return filtered

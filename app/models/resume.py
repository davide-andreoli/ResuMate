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
from app.models.cv_item import short_id
from typing import TypeAlias, Union

ResumeElement: TypeAlias = Union[
    Link, Skill, Experience, Education, Certification, Project, Language
]


class Resume(BaseModel):
    id: str = Field(default_factory=lambda: short_id("res_"))
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
    schema_version: int = 1

    def visible_only(self) -> "Resume":
        """
        Return a deep copy of this Resume where each top-level collection
        contains only items with visible == True.
        Items without an visible attribute are kept by default.
        """
        filtered = self.model_copy(deep=True)
        filtered.links = [
            link for link in filtered.links if getattr(link, "visible", True)
        ]
        filtered.skills = [
            skill for skill in filtered.skills if getattr(skill, "visible", True)
        ]
        filtered.experience = [
            experience_item
            for experience_item in filtered.experience
            if getattr(experience_item, "visible", True)
        ]
        filtered.education = [
            education_item
            for education_item in filtered.education
            if getattr(education_item, "visible", True)
        ]
        filtered.certifications = [
            certification
            for certification in filtered.certifications
            if getattr(certification, "visible", True)
        ]
        filtered.projects = [
            project
            for project in filtered.projects
            if getattr(project, "visible", True)
        ]
        filtered.languages = [
            language
            for language in filtered.languages
            if getattr(language, "visible", True)
        ]
        return filtered

    def update_element_by_id(self, element_id: str, new_element: ResumeElement) -> bool:
        """
        Update an element in the resume by its ID.
        Returns True if the element was found and updated, False otherwise.
        """
        collections = [
            self.links,
            self.skills,
            self.experience,
            self.education,
            self.certifications,
            self.projects,
            self.languages,
        ]

        for collection in collections:
            for idx, element in enumerate(collection):
                if getattr(element, "id", None) == element_id:
                    collection[idx] = new_element
                    self.updated_at = date.today()
                    return True
        return False

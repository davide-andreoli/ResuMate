from app.core.agents.builder import get_model, ModelConfig
from app.core.agents.common import (
    ModelHandoff,
    ResumateAgentProvider,
    SupervisorRuntimeContext,
)
from app.models.resume import Resume
from app.models.education import Education
from app.models.experience import Experience
from app.models.link import Link
from app.models.skill import Skill
from app.models.certification import Certification
from app.models.project import Project
from app.models.langauge import Language
from pydantic_ai import Agent, RunContext, Tool
from typing import List, Optional, Literal
from datetime import date

RESUME_CREATOR_AGENT_PROMPT = """
    Your name is resume_creator, you are part of an agent team called ResuMate.
    Here is the list of agents you have access to:
    {agents_list}
    Your job is to help users create their resumes by gathering necessary information and structuring it in a clear and professional format. You should ask clarifying questions to gather all relevant details about the user's work experience, education, skills, and other pertinent information. Always confirm the information with the user before finalizing the resume content. If the user asks for help that is outside your scope, hand off the request to the appropriate agent.
    """


def create_starting_resume(
    context: RunContext[SupervisorRuntimeContext],
    name: str,
    display_name: str,
    date_of_birth: date,
    title: Optional[str] = None,
    email: Optional[str] = None,
    phone: Optional[str] = None,
    location: Optional[str] = None,
    summary: Optional[str] = None,
) -> str:
    """
    Create a starting resume for the user. The resume should include the user's name, contact information, and a brief summary if available. This will serve as the initial content that the user can then edit and expand upon with your guidance. You should try to gather as much information as possible to create a comprehensive starting point for the user's resume. Always confirm the details with the user before finalizing the resume content.
    Args:
        name: str
        display_name: str
        date_of_birth: date
        title: Optional[str] = None
        email: Optional[str] = None
        phone: Optional[str] = None
        location: Optional[str] = None
        summary: Optional[str] = None
    """
    resume = Resume(
        name=name,
        display_name=display_name,
        date_of_birth=date_of_birth,
        title=title,
        email=email,
        phone=phone,
        location=location,
        summary=summary,
    )
    context.deps.document_storage.save_resume(resume.dump_to_yaml_string(), resume.id)
    context.deps.resume_id = resume.id
    return "Resume created successfully, please remember to select it in the context."


def add_resume_experience(
    context: RunContext[SupervisorRuntimeContext],
    company: str,
    role: str,
    start: Optional[date] = None,
    end: Optional[date] = None,
    location: Optional[str] = None,
    summary: Optional[str] = None,
    bullets: Optional[List[str]] = None,
) -> str:
    """
    Add a work experience entry to the user's resume. This should include details about the company, role, duration of employment, location, and a summary of responsibilities and achievements. You should ask the user for all relevant information to create a comprehensive experience entry. Always confirm the details with the user before adding the experience to the resume.
    Args:
        company: str = ""
        role: str = ""
        start: Optional[date] in YYYY-MM-DD format
        end: Optional[date] in YYYY-MM-DD format
        location: Optional[str] = None
        summary: Optional[str] = None
        bullets: List[str] = Field(default_factory=list)
    """
    if not context.deps.resume_id:
        return "No resume selected."
    resume = context.deps.document_storage.get_resume(context.deps.resume_id)
    experience_entry = Experience(
        company=company,
        role=role,
        start=start,
        end=end,
        location=location,
        summary=summary,
        bullets=bullets or [],
    )
    resume.experience.append(experience_entry)
    context.deps.document_storage.save_resume(
        resume.dump_to_yaml_string(), context.deps.resume_id
    )
    return "Experience added successfully."


def add_resume_education(
    context: RunContext[SupervisorRuntimeContext],
    institution: str,
    degree: str,
    start: Optional[date] = None,
    end: Optional[date] = None,
    details: Optional[str] = None,
    location: Optional[str] = None,
) -> str:
    """
    Add an education entry to the user's resume. This should include details about the institution, degree, duration of study, location, and any additional details. You should ask the user for all relevant information to create a comprehensive education entry. Always confirm the details with the user before adding the education to the resume.
    Args:
        institution: str = ""
        degree: str = ""
        start: Optional[date] in YYYY-MM-DD format
        end: Optional[date] in YYYY-MM-DD format
        details: Optional[str] = None
        location: Optional[str] = None
    """
    if not context.deps.resume_id:
        return "No resume selected."
    resume = context.deps.document_storage.get_resume(context.deps.resume_id)
    education_entry = Education(
        institution=institution,
        degree=degree,
        start=start,
        end=end,
        details=details,
        location=location,
    )
    resume.education.append(education_entry)
    context.deps.document_storage.save_resume(
        resume.dump_to_yaml_string(), context.deps.resume_id
    )
    return "Education added successfully."


def add_resume_link(
    context: RunContext[SupervisorRuntimeContext],
    name: str,
    url: str,
    link_type: Literal["website", "github", "linkedin"] = "website",
) -> str:
    """
    Add a link to the user's resume. This should include details about the link's name, URL, and type. You should ask the user for all relevant information to create a comprehensive link entry. Always confirm the details with the user before adding the link to the resume.
    Args:
        name: str = ""
        url: HttpUrl = HttpUrl("https://example.com")
        link_type: Literal["website", "github", "linkedin"] = "website"
    """
    if not context.deps.resume_id:
        return "No resume selected."
    resume = context.deps.document_storage.get_resume(context.deps.resume_id)
    link_entry = Link(
        label=name,
        url=url,
        link_type=link_type,
    )
    resume.links.append(link_entry)
    context.deps.document_storage.save_resume(
        resume.dump_to_yaml_string(), context.deps.resume_id
    )
    return "Link added successfully."


def add_resume_skill(
    context: RunContext[SupervisorRuntimeContext],
    name: str,
    level: Optional[
        Literal["Beginner", "Intermediate", "Advanced", "Expert"]
    ] = "Beginner",
) -> str:
    """
    Add a skill to the user's resume. This should include details about the skill's name and proficiency level. You should ask the user for all relevant information to create a comprehensive skill entry. Always confirm the details with the user before adding the skill to the resume.
    Args:
        name: str = ""
        level: Optional[Literal["Beginner", "Intermediate", "Advanced", "Expert"]] = (
            "Beginner"
        )
    """
    if not context.deps.resume_id:
        return "No resume selected."
    resume = context.deps.document_storage.get_resume(context.deps.resume_id)
    skill_entry = Skill(
        name=name,
        level=level,
    )
    resume.skills.append(skill_entry)
    context.deps.document_storage.save_resume(
        resume.dump_to_yaml_string(), context.deps.resume_id
    )
    return "Skill added successfully."


def add_resume_certification(
    context: RunContext[SupervisorRuntimeContext],
    name: str,
    issuer: Optional[str] = None,
    certification_date: Optional[date] = None,
    credential_id: Optional[str] = None,
    link: Optional[str] = None,
) -> str:
    """
    Add a certification to the user's resume. This should include details about the certification's name, issuer, date, credential ID, and link. You should ask the user for all relevant information to create a comprehensive certification entry. Always confirm the details with the user before adding the certification to the resume.
    Args:
        name: str = ""
        issuer: Optional[str] = None
        certification_date: Optional[date] in YYYY-MM-DD format
        credential_id: Optional[str] = None
        link: Optional[str] = None
    """
    if not context.deps.resume_id:
        return "No resume selected."
    resume = context.deps.document_storage.get_resume(context.deps.resume_id)
    certification_entry = Certification(
        name=name,
        issuer=issuer,
        certification_date=certification_date,
        credential_id=credential_id,
        link=link,
    )
    resume.certifications.append(certification_entry)
    context.deps.document_storage.save_resume(
        resume.dump_to_yaml_string(), context.deps.resume_id
    )
    return "Certification added successfully."


def add_resume_project(
    context: RunContext[SupervisorRuntimeContext],
    name: str,
    description: Optional[str] = None,
    technologies: List[str] = [],
    link: Optional[str] = None,
) -> str:
    """
    Add a project to the user's resume. This should include details about the project's name, description, and link. You should ask the user for all relevant information to create a comprehensive project entry. Always confirm the details with the user before adding the project to the resume.
    Args:
        name: str = ""
        description: Optional[str] = None
        technologies: List[str] = Field(default_factory=list[str])
        link: Optional[HttpUrl] = None
    """
    if not context.deps.resume_id:
        return "No resume selected."
    resume = context.deps.document_storage.get_resume(context.deps.resume_id)
    project_entry = Project(
        name=name,
        description=description,
        technologies=technologies,
        link=link,
    )
    resume.projects.append(project_entry)
    context.deps.document_storage.save_resume(
        resume.dump_to_yaml_string(), context.deps.resume_id
    )
    return "Project added successfully."


def add_resume_language(
    context: RunContext[SupervisorRuntimeContext],
    name: str,
    proficiency: Literal["Basic", "Conversational", "Fluent", "Native"] = "Basic",
) -> str:
    """
    Add a language to the user's resume. This should include details about the language's name and proficiency level. You should ask the user for all relevant information to create a comprehensive language entry. Always confirm the details with the user before adding the language to the resume.
    Args:
        name: str = ""
        proficiency: Literal["Basic", "Conversational", "Fluent", "Native"] = "Basic"
    """
    if not context.deps.resume_id:
        return "No resume selected."
    resume = context.deps.document_storage.get_resume(context.deps.resume_id)
    language_entry = Language(
        name=name,
        proficiency=proficiency,
    )
    resume.languages.append(language_entry)
    context.deps.document_storage.save_resume(
        resume.dump_to_yaml_string(), context.deps.resume_id
    )
    return "Language added successfully."


class ResumeCreatorAgentProvider(ResumateAgentProvider):
    name = "resume_creator"
    description = "A specialized agent that helps users create their resumes by gathering necessary information and structuring it in a clear and professional format. It can also add new elements to an existing resume."

    def build(
        self, config: ModelConfig, agents_list: str
    ) -> Agent[SupervisorRuntimeContext, str | ModelHandoff]:
        return Agent(
            get_model(config),
            deps_type=SupervisorRuntimeContext,
            tools=[
                Tool(create_starting_resume, takes_ctx=True),
                Tool(add_resume_experience, takes_ctx=True),
                Tool(add_resume_education, takes_ctx=True),
                Tool(add_resume_link, takes_ctx=True),
                Tool(add_resume_skill, takes_ctx=True),
                Tool(add_resume_certification, takes_ctx=True),
                Tool(add_resume_project, takes_ctx=True),
                Tool(add_resume_language, takes_ctx=True),
            ],
            system_prompt=RESUME_CREATOR_AGENT_PROMPT.format(agents_list=agents_list),
        )

from datetime import date

import yaml
from app.models.resume import Resume, ResumeDetails
from app.models.skill import Skill
from typing import cast


def test_load_resume_from_yaml(test_resume_file: str):
    resume = Resume.load_from_yaml_string(test_resume_file)
    assert resume.name == "Jane Doe"
    assert resume.email == "jane.doe@example.com"
    assert resume.phone == "+1-555-123-4567"
    assert resume.id == "res_ndzi76id"
    assert resume.date_of_birth == date(2000, 1, 1)
    assert resume.display_name == "Jane Doe Resume"
    assert len(resume.links) == 3


def test_resume_dumps_to_yaml(test_resume_file: str):
    resume = Resume.load_from_yaml_string(test_resume_file)
    yaml_output = resume.dump_to_yaml_string()
    assert isinstance(yaml_output, str)
    assert "Jane Doe" in yaml_output
    assert yaml.safe_load(yaml_output) == yaml.safe_load(test_resume_file)


def test_resume_details(test_resume_file: str):
    resume = Resume.load_from_yaml_string(test_resume_file)
    details = resume.get_details()
    assert isinstance(details, ResumeDetails)
    assert details.name == "Jane Doe"
    assert details.id == "res_ndzi76id"
    assert details.display_name == "Jane Doe Resume"
    assert (
        str(details) == "Jane Doe Resume (ID: res_ndzi76id, Last Updated: 2025-10-01)"
    )


def test_resume_visible_only(test_resume_file: str):
    resume = Resume.load_from_yaml_string(test_resume_file)
    visible_resume = resume.visible_only()
    assert isinstance(visible_resume, Resume)
    assert len(visible_resume.links) == 0


def test_get_element_by_id(test_resume_file: str):
    resume = Resume.load_from_yaml_string(test_resume_file)
    element: Skill = cast(Skill, resume.get_element_by_id("ski_pjfqsp7a"))
    assert element is not None
    assert element.id == "ski_pjfqsp7a"
    assert element.name == "Python"
    assert element.level == "Advanced"


def test_get_element_by_id_not_found(test_resume_file: str):
    resume = Resume.load_from_yaml_string(test_resume_file)
    element = resume.get_element_by_id("non_existent_id")
    assert element is None


def test_update_element_by_id(test_resume_file: str):
    resume = Resume.load_from_yaml_string(test_resume_file)
    resume.update_element_by_id("ski_pjfqsp7a", {"name": "Python", "level": "Expert"})
    updated_skill: Skill = cast(Skill, resume.get_element_by_id("ski_pjfqsp7a"))
    assert updated_skill.name == "Python"
    assert updated_skill.level == "Expert"


def test_update_element_by_id_not_found(test_resume_file: str):
    resume = Resume.load_from_yaml_string(test_resume_file)
    result = resume.update_element_by_id(
        "non_existent_id", {"name": "Python", "level": "Expert"}
    )
    assert result is False

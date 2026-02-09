from datetime import date

import yaml
from app.models.resume import Resume, ResumeDetails


def test_load_resume_from_yaml(test_resume_file: str):
    resume = Resume.load_from_yaml_string(test_resume_file)
    assert resume.name == "Jane Doe"
    assert resume.email == "jane.doe@example.com"
    assert resume.phone == "+1-555-123-4567"
    assert resume.id == "res_ndzi76id"
    assert resume.date_of_birth == date(2000, 1, 1)
    assert resume.display_name == "Jane Doe Resume"


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

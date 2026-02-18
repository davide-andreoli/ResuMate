from app.models.template import Template, TemplateDetails


def test_load_template_from_file_content(test_template_file: str):
    template = Template.load_from_file_content(test_template_file)
    assert template.name == "modern_resume"
    assert template.display_name == "Modern Resume"
    assert (
        template.description
        == "A sleek and contemporary resume template with a modern design."
    )
    assert template.author == "Resumate"
    assert template.version == 1
    assert len(template.variables) == 1
    assert template.html_content.strip().startswith("<!doctype html>")


def test_template_to_file_content(test_template_file: str):
    template = Template.load_from_file_content(test_template_file)
    file_content = template.to_file_content()
    assert isinstance(file_content, str)
    assert test_template_file == file_content


def test_template_details(test_template_file: str):
    template = Template.load_from_file_content(test_template_file)
    details = template.get_details()
    assert isinstance(details, TemplateDetails)
    assert details.name == "modern_resume"
    assert details.display_name == "Modern Resume"
    assert (
        details.description
        == "A sleek and contemporary resume template with a modern design."
    )
    assert details.author == "Resumate"
    assert details.version == 1


def test_template_load_no_front_matter(test_template_no_front_matter_file: str):
    template = Template.load_from_file_content(test_template_no_front_matter_file)
    assert template.name == "Unnamed"
    assert template.display_name == "Unnamed Template"
    assert template.description is None
    assert template.author is None
    assert template.version == 1
    assert len(template.variables) == 0
    assert template.html_content.strip().startswith("<!doctype html>")


def test_template_load_invalid_front_matter(
    test_template_invalid_front_matter_file: str,
):
    template = Template.load_from_file_content(test_template_invalid_front_matter_file)
    assert template.name == "Unnamed"
    assert template.display_name == "Unnamed Template"
    assert template.description is None
    assert template.author is None
    assert template.version == 1
    assert len(template.variables) == 0
    assert template.html_content.strip().startswith("<!doctype html>")


def test_template_load_empty_front_matter(test_template_empty_front_matter_file: str):
    template = Template.load_from_file_content(test_template_empty_front_matter_file)
    assert template.name == "Unnamed"
    assert template.display_name == "Unnamed Template"
    assert template.description is None
    assert template.author is None
    assert template.version == 1
    assert len(template.variables) == 0
    assert template.html_content.strip().startswith("<!doctype html>")


def test_template_with_invalid_variable(
    test_template_invalid_variable_front_matter_file: str,
):
    template = Template.load_from_file_content(
        test_template_invalid_variable_front_matter_file
    )
    assert len(template.variables) == 0
    assert template.html_content.strip().startswith("<!doctype html>")

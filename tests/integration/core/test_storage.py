import os
from app.core.storage import LocalDocumentStorage
from app.models.resume import Resume
from app.models.template import Template
from pathlib import Path


def test_create_get_delete_resume(tmp_path: Path, test_resume_file: str):
    storage = LocalDocumentStorage(str(tmp_path))
    resume_id = "res_ndzi76id"
    storage.save_resume(test_resume_file, resume_id)
    extracted_resume = storage.get_resume(resume_id)
    assert extracted_resume is not None
    assert isinstance(extracted_resume, Resume)
    assert extracted_resume.id == resume_id
    deleted = storage.delete_resume(resume_id)
    assert deleted is None


def test_list_resumes(tmp_path: Path, test_resume_file: str):
    storage = LocalDocumentStorage(str(tmp_path))
    resume_id = "res_ndzi76id"
    storage.save_resume(test_resume_file, resume_id)
    resumes = storage.list_resumes()
    assert len(resumes) == 1
    assert isinstance(resumes[0], Resume)
    assert resumes[0].id == resume_id


def test_create_get_delete_template(tmp_path: Path, test_template_file: str):
    storage = LocalDocumentStorage(str(tmp_path))
    template = Template.load_from_file_content(test_template_file)
    storage.save_template(template)
    extracted_template = storage.get_template(template.id)
    assert extracted_template is not None
    assert isinstance(extracted_template, Template)
    assert extracted_template.id == template.id
    deleted = storage.delete_template(template.id)
    assert deleted is None


def test_list_templates(tmp_path: Path, test_template_file: str):
    storage = LocalDocumentStorage(str(tmp_path))
    template = Template.load_from_file_content(test_template_file)
    storage.save_template(template)
    templates = storage.list_templates()
    assert len(templates) == 1
    assert isinstance(templates[0], Template)
    assert templates[0].id == template.id


def test_save_rendered_resume(
    tmp_path: Path, test_template_rendered_html: str, test_template_rendered_pdf: bytes
):
    storage = LocalDocumentStorage(str(tmp_path))
    render_id = "res_ndzi76id_tmp_lreszfi9"
    storage.save_rendered_html(test_template_rendered_html, render_id)
    html_path = os.path.join(storage.html_folder, render_id + ".html")
    assert os.path.exists(html_path)
    with open(html_path, "r") as f:
        content = f.read()
        assert content == test_template_rendered_html
    storage.save_rendered_pdf(test_template_rendered_pdf, render_id)
    pdf_path = os.path.join(storage.pdf_folder, render_id + ".pdf")
    assert os.path.exists(pdf_path)
    with open(pdf_path, "rb") as f:
        content = f.read()
        assert content == test_template_rendered_pdf

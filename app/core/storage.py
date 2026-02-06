from app.models.resume import Resume
from app.models.template import Template
from typing import List
import os


class LocalDocumentStorage:
    def __init__(self, base_folder: str = "documents"):
        self.base_folder = base_folder
        self.resume_folder = os.path.join(base_folder, "resumes")
        self.template_folder = os.path.join(base_folder, "templates")
        self.render_folder = os.path.join(base_folder, "renders")
        self.pdf_folder = os.path.join(self.render_folder, "pdfs")
        self.html_folder = os.path.join(self.render_folder, "htmls")

        self.create_folders()

    def create_folders(self):
        os.makedirs(self.base_folder, exist_ok=True)
        os.makedirs(self.resume_folder, exist_ok=True)
        os.makedirs(self.template_folder, exist_ok=True)
        os.makedirs(self.render_folder, exist_ok=True)
        os.makedirs(self.pdf_folder, exist_ok=True)
        os.makedirs(self.html_folder, exist_ok=True)

    def list_resumes(self) -> List[Resume]:
        resumes: List[Resume] = []
        for filename in os.listdir(self.resume_folder):
            if filename.endswith(".yaml") or filename.endswith(".yml"):
                with open(os.path.join(self.resume_folder, filename), "r") as f:
                    resume = Resume.load_from_yaml_string(f.read())
                    resumes.append(resume)
        return resumes

    def list_templates(self) -> List[Template]:
        templates: List[Template] = []
        for filename in os.listdir(self.template_folder):
            if filename.endswith(".html.j2") or filename.endswith(".htm.j2"):
                with open(os.path.join(self.template_folder, filename), "r") as f:
                    template = Template.load_from_file_content(f.read())
                    templates.append(template)
        return templates

    def get_template(self, template_id: str) -> Template:
        template_path = os.path.join(self.template_folder, template_id + ".html.j2")
        with open(template_path, "r") as f:
            return Template.load_from_file_content(f.read())

    def save_template(self, template: Template):
        template_path = os.path.join(self.template_folder, template.id + ".html.j2")
        with open(template_path, "w") as f:
            f.write(template.to_file_content())

    def delete_template(self, template_id: str):
        template_path = os.path.join(self.template_folder, template_id + ".html.j2")
        os.remove(template_path)

    def save_resume(self, resume_content: str, resume_id: str):
        resume_path = os.path.join(self.resume_folder, resume_id + ".yaml")
        with open(resume_path, "w") as f:
            f.write(resume_content)

    def get_resume(self, resume_id: str) -> Resume:
        resume_path = os.path.join(self.resume_folder, resume_id + ".yaml")
        with open(resume_path, "r") as f:
            return Resume.load_from_yaml_string(f.read())

    def delete_resume(self, resume_id: str):
        resume_path = os.path.join(self.resume_folder, resume_id + ".yaml")
        os.remove(resume_path)

    def save_rendered_html(self, html_content: str, render_id: str):
        html_path = os.path.join(self.html_folder, render_id + ".html")
        with open(html_path, "w") as f:
            f.write(html_content)

    def save_rendered_pdf(self, pdf_bytes: bytes, render_id: str):
        pdf_path = os.path.join(self.pdf_folder, render_id + ".pdf")
        with open(pdf_path, "wb") as f:
            f.write(pdf_bytes)

from app.models.resume import Resume
import os


class LocalDocumentStorage:
    def __init__(self, base_folder: str = "documents"):
        self.base_folder = base_folder
        self.resume_folder = os.path.join(base_folder, "resumes")
        self.template_folder = os.path.join(base_folder, "templates")
        self.create_folders()

    def create_folders(self):
        os.makedirs(self.base_folder, exist_ok=True)
        os.makedirs(self.resume_folder, exist_ok=True)
        os.makedirs(self.template_folder, exist_ok=True)

    def list_resumes(self):
        return os.listdir(self.resume_folder)

    def list_templates(self):
        return os.listdir(self.template_folder)

    def save_resume(self, resume_content: str, resume_name: str):
        resume_path = os.path.join(self.resume_folder, resume_name)
        with open(resume_path, "w") as f:
            f.write(resume_content)

    def get_resume(self, resume_name: str) -> Resume:
        resume_path = os.path.join(self.resume_folder, resume_name)
        with open(resume_path, "r") as f:
            return Resume.load_from_yaml_string(f.read())

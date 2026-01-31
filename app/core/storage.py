from app.models.resume import Resume
from typing import List
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

    def list_resumes(self) -> List[Resume]:
        resumes: List[Resume] = []
        for filename in os.listdir(self.resume_folder):
            if filename.endswith(".yaml") or filename.endswith(".yml"):
                with open(os.path.join(self.resume_folder, filename), "r") as f:
                    resume = Resume.load_from_yaml_string(f.read())
                    resumes.append(resume)
        return resumes

    def list_templates(self) -> List[str]:
        return os.listdir(self.template_folder)

    def save_resume(self, resume_content: str, resume_id: str):
        resume_path = os.path.join(self.resume_folder, resume_id + ".yaml")
        with open(resume_path, "w") as f:
            f.write(resume_content)

    def get_resume(self, resume_id: str) -> Resume:
        resume_path = os.path.join(self.resume_folder, resume_id + ".yaml")
        with open(resume_path, "r") as f:
            return Resume.load_from_yaml_string(f.read())

import yaml
from app.models.resume import Resume


class YamlManager:
    def __init__(self) -> None:
        pass

    def load_resume_from_yaml_string(self, yaml_sting: str) -> Resume:
        data = yaml.safe_load(yaml_sting) or {}
        return Resume.model_validate(data)

    def load_resume_from_yaml_file(self, path: str) -> Resume:
        with open(path, "r", encoding="utf-8") as f:
            return self.load_resume_from_yaml_string(f.read())

    def dump_resume_to_yaml_string(self, resume: Resume) -> str:
        data = resume.model_dump(mode="json", exclude_none=True)
        return yaml.safe_dump(data, sort_keys=False, allow_unicode=True)

    def save_resume_to_yaml_file(self, resume: Resume, path: str):
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.dump_resume_to_yaml_string(resume))

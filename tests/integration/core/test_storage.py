from app.core.storage import LocalDocumentStorage
from pathlib import Path


def test_create_get_delete_resume(tmp_path: Path, test_resume_file: str):
    storage = LocalDocumentStorage()
    resume_id = "test_resume"
    storage.save_resume(test_resume_file, resume_id)

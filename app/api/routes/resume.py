from fastapi.responses import JSONResponse
from fastapi import APIRouter, Depends, UploadFile, File
from pydantic import BaseModel
from app.api.dependencies.dependencies import get_storage
from app.core.storage import LocalDocumentStorage
from app.models.resume import Resume
from typing import List

resume_router = APIRouter(prefix="/resume", tags=["resume"])


class ResumeUploadResponse(BaseModel):
    filename: str
    status: str


@resume_router.get("/list", response_model=List[str])
async def list_resumes(storage: LocalDocumentStorage = Depends(get_storage)):
    resumes = storage.list_resumes()
    return resumes


@resume_router.post("/save", response_model=ResumeUploadResponse)
async def save_resume(
    resume: Resume,
    storage: LocalDocumentStorage = Depends(get_storage),
):
    final_yaml = resume.dump_to_yaml_string()
    storage.save_resume(final_yaml, resume.name + ".yaml")
    return ResumeUploadResponse(filename=resume.name + ".yaml", status="saved")


@resume_router.get("/{resume_name}", response_model=Resume)
async def get_resume(
    resume_name: str, storage: LocalDocumentStorage = Depends(get_storage)
):
    resume = storage.get_resume(resume_name=resume_name)
    if not resume:
        return JSONResponse(status_code=404, content={"message": "Resume not found"})
    return resume


@resume_router.post("/upload", response_model=ResumeUploadResponse)
async def upload_resume(
    file: UploadFile = File(...), storage: LocalDocumentStorage = Depends(get_storage)
):
    content = await file.read()
    storage.save_resume(content.decode("utf-8"), file.filename)
    return ResumeUploadResponse(filename=file.filename, status="uploaded")

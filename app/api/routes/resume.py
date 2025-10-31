from fastapi.responses import JSONResponse
from fastapi import APIRouter, Depends, UploadFile, File
from pydantic import BaseModel
from app.api.dependencies.dependencies import get_storage, get_yaml_manager
from app.core.storage import LocalDocumentStorage
from app.core.yaml_manager import YamlManager
from app.models.resume import Resume

resume_router = APIRouter(prefix="/resume", tags=["resume"])


class ListResumesResponse(BaseModel):
    resumes: list[str]


class ListTemplatesResponse(BaseModel):
    templates: list[str]


class ResumeUploadResponse(BaseModel):
    filename: str
    status: str


@resume_router.get("/list", response_model=ListResumesResponse)
async def list_resumes(storage: LocalDocumentStorage = Depends(get_storage)):
    resumes = storage.list_resumes()
    return ListResumesResponse(resumes=resumes)


@resume_router.get("/templates", response_model=ListTemplatesResponse)
async def list_templates(storage: LocalDocumentStorage = Depends(get_storage)):
    templates = storage.list_templates()
    return ListTemplatesResponse(templates=templates)


@resume_router.post("/save", response_model=ResumeUploadResponse)
async def save_resume(
    resume: Resume,
    storage: LocalDocumentStorage = Depends(get_storage),
    yaml_manager: YamlManager = Depends(get_yaml_manager),
):
    final_yaml = yaml_manager.dump_resume_to_yaml_string(resume)
    storage.save_resume(final_yaml, resume.name + ".yaml")
    return ResumeUploadResponse(filename=resume.name + ".yaml", status="uploaded")


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

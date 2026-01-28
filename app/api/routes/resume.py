from fastapi import APIRouter, Depends, HTTPException, Request
from app.api.dependencies.dependencies import get_storage
from app.core.storage import LocalDocumentStorage
from app.models.resume import ResumeDetails, Resume
from typing import List

resume_router = APIRouter(prefix="/resumes", tags=["resume"])


@resume_router.get("/", response_model=List[ResumeDetails])
async def list_resumes(
    storage: LocalDocumentStorage = Depends(get_storage),
) -> List[ResumeDetails]:
    resumes = storage.list_resumes()
    return [resume.get_details() for resume in resumes]


@resume_router.get("/{resume_id}", response_model=Resume)
async def get_resume(
    resume_id: str, storage: LocalDocumentStorage = Depends(get_storage)
) -> Resume:
    try:
        resume = storage.get_resume(resume_id=resume_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Resume not found")
    return resume


@resume_router.post("/", status_code=201)
async def create_resume(
    request: Request, storage: LocalDocumentStorage = Depends(get_storage)
):
    content_type = request.headers.get("content-type", "")
    if content_type.startswith("application/json"):
        resume_data = await request.json()
        resume = Resume(**resume_data)
        content = resume.dump_to_yaml_string()
    elif content_type.startswith(("application/yaml", "text/yaml", "text/plain")):
        content = await request.body()
        content = content.decode("utf-8")
    else:
        raise HTTPException(status_code=415, detail="Unsupported content type")
    resume = Resume.load_from_yaml_string(content)
    storage.save_resume(content, resume.id + ".yaml")
    return {"id": resume.id}


@resume_router.delete("/{resume_id}", status_code=204)
async def delete_resume(
    resume_id: str, storage: LocalDocumentStorage = Depends(get_storage)
):
    # TODO: Implement delete functionality
    pass


@resume_router.put("/{resume_id}", status_code=204)
async def update_resume(
    resume_id: str,
    request: Request,
    storage: LocalDocumentStorage = Depends(get_storage),
):
    content_type = request.headers.get("content-type", "")
    if content_type.startswith("application/json"):
        resume_data = await request.json()
        resume = Resume(**resume_data)
        content = resume.dump_to_yaml_string()
    elif content_type.startswith(("application/yaml", "text/yaml", "text/plain")):
        content = await request.body()
        content = content.decode("utf-8")
    else:
        raise HTTPException(status_code=415, detail="Unsupported content type")
    storage.save_resume(content, resume_id + ".yaml")

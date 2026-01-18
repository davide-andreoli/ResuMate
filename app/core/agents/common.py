from dataclasses import dataclass
from app.core.storage import LocalDocumentStorage
from typing import Optional
from pydantic import BaseModel


@dataclass
class SupervisorRuntimeContext:
    """
    Context class for the ResuMate Supervisor agent runtime.
    """

    document_storage: LocalDocumentStorage
    resume_name: Optional[str] = None


class ModelHandoff(BaseModel):
    """
    Model handoff information, used to transfer context between different agents.
    """

    target_agent: str

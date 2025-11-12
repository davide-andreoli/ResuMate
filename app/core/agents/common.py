from dataclasses import dataclass
from app.core.storage import LocalDocumentStorage
from typing import Optional


@dataclass
class SupervisorRuntimeContext:
    """
    Context class for the ResuMate Supervisor agent runtime.
    """

    document_storage: LocalDocumentStorage
    resume_name: Optional[str] = None

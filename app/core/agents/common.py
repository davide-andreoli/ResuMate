from dataclasses import dataclass
from app.core.storage import LocalDocumentStorage


@dataclass
class SupervisorRuntimeContext:
    """
    Context class for the ApplAI Supervisor agent runtime.
    """

    document_storage: LocalDocumentStorage

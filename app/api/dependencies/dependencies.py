from functools import lru_cache
from app.core.agents.supervisor import ApplAISupervisor
from app.core.agents.builder import ModelConfig
from app.core.memory import LocalMemory
from app.core.storage import LocalDocumentStorage


@lru_cache()
def get_memory():
    return LocalMemory()


@lru_cache()
def get_storage():
    return LocalDocumentStorage()


@lru_cache()
def get_assistant() -> ApplAISupervisor:
    return ApplAISupervisor(config=ModelConfig(), document_storage=get_storage())

from functools import lru_cache
from app.core.agents.agent_runner import ResumateAgentRunner
from app.core.agents.builder import ModelConfig
from app.core.memory import LocalFileMemory
from app.core.storage import LocalDocumentStorage


@lru_cache()
def get_memory():
    return LocalFileMemory(memory_folder="memory")


@lru_cache()
def get_storage():
    return LocalDocumentStorage()


@lru_cache()
def get_assistant() -> ResumateAgentRunner:
    return ResumateAgentRunner(config=ModelConfig(), document_storage=get_storage())

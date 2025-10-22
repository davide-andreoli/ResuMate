from functools import lru_cache
from app.core.agents.supervisor import ApplAISupervisor
from app.core.agents.builder import ModelConfig
from app.core.yaml_manager import YamlManager
from app.core.storage import LocalDocumentStorage


@lru_cache()
def get_yaml_manager():
    return YamlManager()


@lru_cache()
def get_storage():
    return LocalDocumentStorage()


@lru_cache()
def get_assistant() -> ApplAISupervisor:
    return ApplAISupervisor(config=ModelConfig(), document_storage=get_storage())

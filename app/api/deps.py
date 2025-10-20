from functools import lru_cache
from app.core.agents.supervisor import ApplAISupervisor
from app.core.agents.builder import ModelConfig


@lru_cache()
def get_assistant() -> ApplAISupervisor:
    return ApplAISupervisor(config=ModelConfig())

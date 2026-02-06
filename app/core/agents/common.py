from abc import ABC, abstractmethod
from dataclasses import dataclass
from app.core.agents.builder import ModelConfig
from app.core.storage import LocalDocumentStorage
from typing import Optional
from pydantic import BaseModel
from pydantic_ai import Agent


@dataclass
class SupervisorRuntimeContext:
    """
    Context class for the ResuMate Supervisor agent runtime.
    """

    document_storage: LocalDocumentStorage
    resume_id: Optional[str] = None


class ModelHandoff(BaseModel):
    """
    Model handoff information, used to transfer context between different agents.
    """

    target_agent: str


class HandoffInformation(BaseModel):
    """
    Information about an agent for handoff purposes.
    """

    agent_name: str
    description: str


class ResumateAgentProvider(ABC):
    """
    Abstract base class for ResuMate agent providers.
    """

    name: str
    description: str

    @abstractmethod
    def build(
        self, config: ModelConfig, agents_list: str
    ) -> Agent[SupervisorRuntimeContext, str | ModelHandoff]:
        pass

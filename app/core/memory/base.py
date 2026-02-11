from abc import ABC, abstractmethod
from typing import List, Optional

from pydantic_ai import ModelMessage
from app.core.types import Conversation


class BaseMemory(ABC):
    @abstractmethod
    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        pass  # pragma: no cover

    @abstractmethod
    def create_conversation(self, conversation_id: str) -> Conversation:
        pass  # pragma: no cover

    @abstractmethod
    def delete_conversation(self, conversation_id: str) -> bool:
        pass  # pragma: no cover

    @abstractmethod
    def add_message(self, conversation_id: str, message: ModelMessage):
        pass  # pragma: no cover

    @abstractmethod
    def add_messages(self, conversation_id: str, messages: List[ModelMessage]):
        pass  # pragma: no cover

    @abstractmethod
    def get_all_conversations(self) -> List[Conversation]:
        pass  # pragma: no cover


class ConversationNotFoundError(Exception):
    pass  # pragma: no cover

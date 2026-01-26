from abc import ABC, abstractmethod
from typing import List, Optional

from pydantic_ai import ModelMessage
from app.core.types import Conversation


class BaseMemory(ABC):
    @abstractmethod
    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        pass

    @abstractmethod
    def create_conversation(self, conversation_id: str) -> Conversation:
        pass

    @abstractmethod
    def delete_conversation(self, conversation_id: str) -> bool:
        pass

    @abstractmethod
    def list_conversations(self) -> List[Conversation]:
        pass

    @abstractmethod
    def add_message(self, conversation_id: str, message: ModelMessage):
        pass

    @abstractmethod
    def add_messages(self, conversation_id: str, messages: List[ModelMessage]):
        pass

    @abstractmethod
    def get_all_conversations(self) -> List[Conversation]:
        pass


class ConversationNotFoundError(Exception):
    pass

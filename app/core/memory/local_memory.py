from typing import Dict, List
from app.core.types import Conversation
from typing import Optional
from datetime import datetime
from pydantic_ai import ModelMessage
from app.core.memory.base import BaseMemory, ConversationNotFoundError


class LocalMemory(BaseMemory):
    def __init__(self):
        self.storage: Dict[str, Conversation] = {}

    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        return self.storage.get(conversation_id)

    def create_conversation(self, conversation_id: str) -> Conversation:
        conversation = Conversation(
            conversation_id=conversation_id,
            messages=[],
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
        )
        self.storage[conversation_id] = conversation
        return conversation

    def add_message(self, conversation_id: str, message: ModelMessage):
        if conversation_id not in self.storage:
            raise ConversationNotFoundError(
                f"Conversation with ID {conversation_id} not found"
            )
        self.storage[conversation_id].messages.append(message)
        self.storage[conversation_id].updated_at = datetime.now().isoformat()

    def add_messages(self, conversation_id: str, messages: List[ModelMessage]):
        if conversation_id not in self.storage:
            raise ConversationNotFoundError(
                f"Conversation with ID {conversation_id} not found"
            )
        self.storage[conversation_id].messages.extend(messages)
        self.storage[conversation_id].updated_at = datetime.now().isoformat()

    def get_all_conversations(self) -> List[Conversation]:
        return list(self.storage.values())

    def delete_conversation(self, conversation_id: str) -> bool:
        if conversation_id in self.storage:
            del self.storage[conversation_id]
            return True
        return False

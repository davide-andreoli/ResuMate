import json
from typing import List
from app.core.types import Conversation
from typing import Optional
from datetime import datetime
import os
from pydantic_ai import ModelMessage
from app.core.memory.base import BaseMemory, ConversationNotFoundError


class LocalFileMemory(BaseMemory):
    def __init__(self, memory_folder: str):
        os.makedirs(memory_folder, exist_ok=True)
        self.memory_folder = memory_folder

    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        try:
            with open(f"{self.memory_folder}/{conversation_id}.json", "r") as f:
                data = json.load(f)
                return Conversation(**data)
        except FileNotFoundError:
            return None

    def create_conversation(self, conversation_id: str) -> Conversation:
        conversation = Conversation(
            conversation_id=conversation_id,
            messages=[],
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
        )
        with open(f"{self.memory_folder}/{conversation_id}.json", "w") as f:
            json.dump(conversation.model_dump(mode="json"), f)
        return conversation

    def add_message(self, conversation_id: str, message: ModelMessage):
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            raise ConversationNotFoundError(
                f"Conversation with ID {conversation_id} not found"
            )
        conversation.messages.append(message)
        conversation.updated_at = datetime.now().isoformat()
        with open(f"{self.memory_folder}/{conversation_id}.json", "w") as f:
            json.dump(conversation.model_dump(mode="json"), f)

    def add_messages(self, conversation_id: str, messages: List[ModelMessage]):
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            raise ConversationNotFoundError(
                f"Conversation with ID {conversation_id} not found"
            )
        conversation.messages.extend(messages)
        conversation.updated_at = datetime.now().isoformat()
        with open(f"{self.memory_folder}/{conversation_id}.json", "w") as f:
            json.dump(conversation.model_dump(mode="json"), f)

    def get_all_conversations(self) -> List[Conversation]:
        conversations: List[Conversation] = []
        for filename in os.listdir(self.memory_folder):
            if filename.endswith(".json"):
                with open(f"{self.memory_folder}/{filename}", "r") as f:
                    data = json.load(f)
                    conversations.append(Conversation(**data))
        return conversations

    def delete_conversation(self, conversation_id: str) -> bool:
        file_path = f"{self.memory_folder}/{conversation_id}.json"
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False

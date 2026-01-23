import json
from typing import Dict, List
from app.core.types import Conversation
from typing import Optional
from datetime import datetime
import os


class LocalMemory:
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

    def add_message(self, conversation_id: str, message: Dict[str, str]):
        if conversation_id not in self.storage:
            self.create_conversation(conversation_id)
        self.storage[conversation_id].messages.append(message)

    def add_messages(self, conversation_id: str, messages: List[Dict[str, str]]):
        if conversation_id not in self.storage:
            self.create_conversation(conversation_id)
        self.storage[conversation_id].messages.extend(messages)
        self.storage[conversation_id].updated_at = datetime.now().isoformat()

    def get_all_conversations(self) -> List[Conversation]:
        return list(self.storage.values())


class LocalFileMemory:
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
            json.dump(conversation.model_dump(), f)
        return conversation

    def add_message(self, conversation_id: str, message: Dict[str, str]):
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            conversation = self.create_conversation(conversation_id)
        conversation.messages.append(message)
        conversation.updated_at = datetime.now().isoformat()
        with open(f"{self.memory_folder}/{conversation_id}.json", "w") as f:
            json.dump(conversation.model_dump(), f)

    def add_messages(self, conversation_id: str, messages: List[Dict[str, str]]):
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            conversation = self.create_conversation(conversation_id)
        conversation.messages.extend(messages)
        conversation.updated_at = datetime.now().isoformat()
        with open(f"{self.memory_folder}/{conversation_id}.json", "w") as f:
            json.dump(conversation.model_dump(), f)

    def get_all_conversations(self) -> List[Conversation]:
        conversations: List[Conversation] = []
        for filename in os.listdir(self.memory_folder):
            if filename.endswith(".json"):
                with open(f"{self.memory_folder}/{filename}", "r") as f:
                    data = json.load(f)
                    conversations.append(Conversation(**data))
        return conversations

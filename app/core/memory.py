from typing import Dict, List


class LocalMemory:
    def __init__(self):
        self.storage: Dict[str, List[Dict[str, str]]] = {}

    def get_conversation(self, conversation_id: str) -> List[Dict[str, str]]:
        return self.storage.get(conversation_id, [])

    def add_message(self, conversation_id: str, message: Dict[str, str]):
        if conversation_id not in self.storage:
            self.storage[conversation_id] = []
        self.storage[conversation_id].append(message)

    def set_conversation(self, conversation_id: str, messages: List[Dict[str, str]]):
        self.storage[conversation_id] = messages

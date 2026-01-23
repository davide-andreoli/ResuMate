from pydantic import BaseModel
from typing import List, Optional
from pydantic_ai import ModelMessage


class Conversation(BaseModel):
    conversation_id: str
    messages: List[ModelMessage]
    title: Optional[str] = None
    brief: Optional[str] = None
    created_at: str
    updated_at: str

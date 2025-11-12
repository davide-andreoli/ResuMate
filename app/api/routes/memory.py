from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.api.dependencies.dependencies import get_memory
from app.core.memory import LocalMemory
from typing import Any, Dict, List, Optional

memory_router = APIRouter(prefix="/memory", tags=["memory"])


class MessagePart(BaseModel):
    content: Optional[str] = None
    timestamp: Optional[str] = None
    part_kind: Optional[str] = None
    provider_name: Optional[str] = None
    tool_name: Optional[str] = None
    args: Optional[Dict[str, Any]] = None
    tool_call_id: Optional[str] = None
    id: Optional[str] = None
    signature: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        extra = "allow"


class Message(BaseModel):
    parts: List[MessagePart]
    instructions: Optional[str] = None
    usage: Optional[Dict[str, Any]] = None
    provider_details: Optional[Dict[str, Any]] = None

    class Config:
        extra = "allow"


class StatusResponse(BaseModel):
    status: str


class AddUserMessageRequest(BaseModel):
    conversation_id: str
    message: str


@memory_router.get(
    "/conversations/{conversation_id}/messages", response_model=List[Message]
)
async def chat_history_endpoint(
    conversation_id: str, memory: LocalMemory = Depends(get_memory)
) -> List[Message]:
    message_history = memory.get_conversation(conversation_id)
    return message_history


@memory_router.post("/add_user_message", response_model=StatusResponse)
async def add_user_message_endpoint(
    request: AddUserMessageRequest, memory: LocalMemory = Depends(get_memory)
) -> StatusResponse:
    memory.add_message(
        request.conversation_id, {"role": "user", "content": request.message}
    )
    return StatusResponse(status="message added")

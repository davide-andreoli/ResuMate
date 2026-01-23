from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.api.dependencies.dependencies import get_memory
from app.core.memory import Conversation, LocalMemory
from typing import List
from pydantic_ai import ModelMessage

memory_router = APIRouter(prefix="/memory", tags=["memory"])


class StatusResponse(BaseModel):
    status: str


class AddUserMessageRequest(BaseModel):
    conversation_id: str
    message: str


@memory_router.get("/conversations", response_model=List[Conversation])
async def get_conversations_endpoint(
    memory: LocalMemory = Depends(get_memory),
) -> List[Conversation]:
    return memory.get_all_conversations()


@memory_router.get("/conversations/{conversation_id}", response_model=Conversation)
async def get_conversation_endpoint(
    conversation_id: str, memory: LocalMemory = Depends(get_memory)
) -> Conversation:
    conversation = memory.get_conversation(conversation_id)
    if conversation is None:
        conversation = memory.create_conversation(conversation_id)
    return conversation


@memory_router.get(
    "/conversations/{conversation_id}/messages", response_model=List[ModelMessage]
)
async def chat_history_endpoint(
    conversation_id: str, memory: LocalMemory = Depends(get_memory)
) -> List[ModelMessage]:
    conversation = memory.get_conversation(conversation_id)
    if conversation is None:
        conversation = memory.create_conversation(conversation_id)
    return conversation.messages


@memory_router.post("/add_user_message", response_model=StatusResponse)
async def add_user_message_endpoint(
    request: AddUserMessageRequest, memory: LocalMemory = Depends(get_memory)
) -> StatusResponse:
    memory.add_message(
        request.conversation_id, {"role": "user", "content": request.message}
    )
    return StatusResponse(status="message added")

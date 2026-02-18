from fastapi import APIRouter, Depends, HTTPException
from app.api.dependencies.dependencies import get_memory
from app.core.memory.local_file_memory import (
    Conversation,
    ConversationNotFoundError,
    LocalFileMemory,
)
from typing import List
from pydantic_ai import ModelMessage
from fastapi.responses import JSONResponse

memory_router = APIRouter(prefix="/conversations", tags=["memory"])


@memory_router.get("/", response_model=List[Conversation])
async def get_conversations_endpoint(
    memory: LocalFileMemory = Depends(get_memory),
) -> List[Conversation]:
    conversations = memory.get_all_conversations()
    sorted_conversations = sorted(
        conversations,
        key=lambda conv: conv.updated_at,
        reverse=True,
    )
    return sorted_conversations


@memory_router.get("/{conversation_id}", response_model=Conversation)
async def get_conversation_endpoint(
    conversation_id: str, memory: LocalFileMemory = Depends(get_memory)
) -> Conversation:
    conversation = memory.get_conversation(conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation


@memory_router.post("/{conversation_id}", response_model=Conversation, status_code=201)
async def create_conversation_endpoint(
    conversation_id: str, memory: LocalFileMemory = Depends(get_memory)
) -> Conversation:
    conversation = memory.get_conversation(conversation_id)
    if conversation is not None:
        raise HTTPException(status_code=400, detail="Conversation already exists")
    conversation = memory.create_conversation(conversation_id)
    return conversation


@memory_router.delete("/{conversation_id}")
async def delete_conversation_endpoint(
    conversation_id: str, memory: LocalFileMemory = Depends(get_memory)
) -> JSONResponse:
    success = memory.delete_conversation(conversation_id)
    if success:
        return JSONResponse(status_code=200, content={"status": "conversation deleted"})
    else:
        raise HTTPException(status_code=404, detail="Conversation not found")


@memory_router.get("/{conversation_id}/messages", response_model=List[ModelMessage])
async def chat_history_endpoint(
    conversation_id: str, memory: LocalFileMemory = Depends(get_memory)
) -> List[ModelMessage]:
    conversation = memory.get_conversation(conversation_id)
    if conversation is None:
        conversation = memory.create_conversation(conversation_id)
    return conversation.messages


@memory_router.post("/{conversation_id}/messages", status_code=201)
async def add_user_message_endpoint(
    conversation_id: str, message: str, memory: LocalFileMemory = Depends(get_memory)
) -> JSONResponse:
    try:
        memory.add_message(conversation_id, {"role": "user", "content": message})
    except ConversationNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return JSONResponse(status_code=201, content={"status": "message added"})

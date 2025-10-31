from fastapi.responses import JSONResponse
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.api.dependencies.dependencies import get_memory
from app.core.memory import LocalMemory

memory_router = APIRouter(prefix="/memory", tags=["memory"])


class Message(BaseModel):
    role: str
    content: str


class ChatHistoryResponse(BaseModel):
    messages: list[Message]


class StatusResponse(BaseModel):
    status: str


class AddUserMessageRequest(BaseModel):
    conversation_id: str
    message: str


@memory_router.get(
    "/conversations/{conversation_id}/messages", response_class=JSONResponse
)
async def chat_history_endpoint(
    conversation_id: str, memory: LocalMemory = Depends(get_memory)
) -> ChatHistoryResponse:
    message_history = memory.get_conversation(conversation_id)
    return ChatHistoryResponse(messages=message_history)


@memory_router.post("/add_user_message", response_class=JSONResponse)
async def add_user_message_endpoint(
    request: AddUserMessageRequest, memory: LocalMemory = Depends(get_memory)
) -> StatusResponse:
    memory.add_message(
        request.conversation_id, {"role": "user", "content": request.message}
    )
    return StatusResponse(status="message added")

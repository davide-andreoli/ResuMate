from fastapi.responses import JSONResponse
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.api.dependencies.dependencies import get_memory
from app.core.memory import LocalMemory

memory_router = APIRouter(prefix="/memory", tags=["memory"])


@memory_router.get(
    "/conversations/{conversation_id}/messages", response_class=JSONResponse
)
async def chat_history_endpoint(
    conversation_id: str, memory: LocalMemory = Depends(get_memory)
) -> JSONResponse:
    message_history = memory.get_conversation(conversation_id)
    return JSONResponse(content=message_history)


class AddUserMessageRequest(BaseModel):
    conversation_id: str
    message: str


@memory_router.post("/add_user_message", response_class=JSONResponse)
async def add_user_message_endpoint(
    request: AddUserMessageRequest, memory: LocalMemory = Depends(get_memory)
) -> JSONResponse:
    memory.add_message(
        request.conversation_id, {"role": "user", "content": request.message}
    )
    return JSONResponse(content={"status": "message added"})

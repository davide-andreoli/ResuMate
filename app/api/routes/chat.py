from fastapi.responses import StreamingResponse
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.api.dependencies.dependencies import get_assistant, get_memory
from app.core.agents.supervisor import ResuMateSupervisore
from typing import Optional
from app.core.memory import LocalMemory

chat_router = APIRouter(prefix="/chat", tags=["chat"])


class ChatRequest(BaseModel):
    request: str
    conversation_id: str
    resume_name: Optional[str] = None


@chat_router.post("/", response_class=StreamingResponse)
async def chat_endpoint(
    chat_request: ChatRequest,
    assistant: ResuMateSupervisore = Depends(get_assistant),
    memory: LocalMemory = Depends(get_memory),
):
    message_history = memory.get_conversation(chat_request.conversation_id)

    return StreamingResponse(
        assistant.stream(
            user_prompt=chat_request.request,
            message_history=message_history,
            memory=memory,
            conversation_id=chat_request.conversation_id,
            resume_name=chat_request.resume_name,
        )
    )

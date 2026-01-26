from fastapi.responses import StreamingResponse
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.api.dependencies.dependencies import get_assistant, get_memory
from app.core.agents.agent_runner import ResumateAgentRunner
from typing import Optional
from app.core.memory.base import BaseMemory

chat_router = APIRouter(prefix="/chat", tags=["chat"])


class ChatRequest(BaseModel):
    request: str
    conversation_id: str
    resume_name: Optional[str] = None


@chat_router.post("/", response_class=StreamingResponse)
async def chat_endpoint(
    chat_request: ChatRequest,
    assistant: ResumateAgentRunner = Depends(get_assistant),
    memory: BaseMemory = Depends(get_memory),
):
    conversation = memory.get_conversation(chat_request.conversation_id)
    message_history = conversation.messages if conversation else []

    return StreamingResponse(
        assistant.run_conversation(
            user_prompt=chat_request.request,
            message_history=message_history,
            memory=memory,
            conversation_id=chat_request.conversation_id,
            resume_name=chat_request.resume_name,
        )
    )

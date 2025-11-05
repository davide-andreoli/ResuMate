from fastapi.responses import StreamingResponse
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.api.dependencies.dependencies import get_assistant, get_memory
from app.core.agents.supervisor import ApplAISupervisor
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
    assistant: ApplAISupervisor = Depends(get_assistant),
    memory: LocalMemory = Depends(get_memory),
):
    memory.add_message(
        chat_request.conversation_id, {"role": "user", "content": chat_request.request}
    )
    message_history = memory.get_conversation(chat_request.conversation_id)
    stream = assistant.stream(
        message_history=message_history, resume_name=chat_request.resume_name
    )

    async def wrapper():
        full_text = ""
        async for chunk in stream:
            full_text += chunk
            yield chunk

        memory.add_message(
            chat_request.conversation_id, {"role": "assistant", "content": full_text}
        )

    return StreamingResponse(wrapper())

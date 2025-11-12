from app.core.agents.builder import get_model, ModelConfig
from pydantic_ai import Agent, RunContext, Tool, ModelMessagesTypeAdapter
from pydantic_core import to_jsonable_python
from app.core.memory import LocalMemory
from app.core.storage import LocalDocumentStorage
from app.core.agents.common import SupervisorRuntimeContext
from app.core.agents.resume_content_editor import resume_content_editor_tool
from typing import AsyncGenerator, List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

SUPERVISOR_AGENT_PROMPT = (
    "You are ResuMate Supervisor, an advanced AI assistant designed to help users with all "
    "aspects of resume creation and improvement. You have access to a variety of specialized "
    "agents to assist with this process. Each agent has a specific role and expertise, and you "
    "should delegate tasks to them as needed to provide the best possible assistance to the user."
    "When delegating tasks, ensure that you provide clear instructions and context to the agents, "
    "do not assume that an agent has prior knowledge of the user's requests or history. "
    "The user can select a resume and once they do it'll be available in the context. "
    "Always assume that the user has a resume, if no resume is selected your agents will alert you; in this case, ask the user to create a resume. "
    "This process should be transparent to the user; always communicate with the user directly."
)


def list_resumes_tool(context: RunContext[SupervisorRuntimeContext]) -> str:
    """
    Tool to list all resumes available in the system.

    Returns:
        str: A formatted string listing all resumes.
    """
    resumes = context.deps.document_storage.list_resumes()
    return "\n".join(resumes)


class ResuMateSupervisore:
    def __init__(
        self,
        config: ModelConfig | None = None,
        document_storage: LocalDocumentStorage | None = None,
    ):
        self.model = get_model(config)
        self.document_storage = document_storage
        self.agent: Agent[SupervisorRuntimeContext] = Agent(
            self.model,
            deps_type=SupervisorRuntimeContext,
            system_prompt=SUPERVISOR_AGENT_PROMPT,
            tools=[
                Tool(resume_content_editor_tool, takes_ctx=True),
                Tool(list_resumes_tool, takes_ctx=True),
            ],
        )

    # TODO: Handle message chunks properly instead of yielding raw strings
    async def stream(
        self,
        user_prompt: str,
        message_history: List[Dict[str, str]],
        memory: LocalMemory,
        conversation_id: str,
        resume_name: Optional[str] = None,
    ) -> AsyncGenerator[str, None]:
        message_history_adapter = ModelMessagesTypeAdapter.validate_python(
            message_history
        )
        async with self.agent.run_stream(
            user_prompt=user_prompt,
            message_history=message_history_adapter,
            deps=SupervisorRuntimeContext(
                document_storage=self.document_storage, resume_name=resume_name
            ),
        ) as response:
            async for text in response.stream_text(delta=True):
                yield text
            messages = response.new_messages()
            messages_python = to_jsonable_python(messages)
            memory.add_messages(
                conversation_id=conversation_id, messages=messages_python
            )

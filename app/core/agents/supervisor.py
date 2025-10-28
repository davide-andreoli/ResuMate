from typing import Iterator, Any
from app.core.agents.builder import get_model, ModelConfig
from langchain.tools import tool, ToolRuntime
from langchain.agents import create_agent
from langgraph.types import StreamMode
from app.core.storage import LocalDocumentStorage
from app.core.agents.common import SupervisorRuntimeContext
from app.core.agents.resume_content_editor import resume_content_editor_tool
from langchain.messages import AIMessageChunk
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

SUPERVISOR_AGENT_PROMPT = (
    "You are ApplAI Supervisor, an advanced AI assistant designed to help users with all "
    "aspects of resume creation and improvement. You have access to a variety of specialized "
    "agents to assist with this process. Each agent has a specific role and expertise, and you "
    "should delegate tasks to them as needed to provide the best possible assistance to the user."
    "When delegating tasks, ensure that you provide clear instructions and context to the agents, "
    "do not assume that an agent has prior knowledge of the user's requests or history. "
    "If a resume is not specified in the context it means that the user has not created one yet, so ask them to create one using the menu on the side. "
    "This process should be transparent to the user; always communicate with the user directly."
)


@tool
def list_resumes_tool(runtime: ToolRuntime[SupervisorRuntimeContext]) -> str:
    """
    Tool to list all resumes available in the system.

    Returns:
        str: A formatted string listing all resumes.
    """
    resumes = runtime.context.document_storage.list_resumes()
    return "\n".join(resumes)


class ApplAISupervisor:
    def __init__(
        self,
        config: ModelConfig | None = None,
        document_storage: LocalDocumentStorage | None = None,
    ):
        self.model = get_model(config)
        self.document_storage = document_storage
        self.agent = create_agent(
            get_model(ModelConfig()),
            tools=[resume_content_editor_tool],
            system_prompt=SUPERVISOR_AGENT_PROMPT,
            context_schema=SupervisorRuntimeContext,
        )

    # TODO: Update this to be a better generator
    def stream(
        self,
        request: str,
        message_history: List[Dict[str, str]],
        resume_name: Optional[str] = None,
        stream_mode: StreamMode = "messages",
    ) -> Iterator[dict[str, Any] | Any]:
        prompt = f"Context: The resume this request refers to is: '{resume_name}'.\n\nRequest: {request}"
        message_history.append({"role": "user", "content": prompt})
        stream = self.agent.stream(
            input={
                "messages": message_history,
            },
            stream_mode=stream_mode,
            context=SupervisorRuntimeContext(
                document_storage=self.document_storage, resume_name=resume_name
            ),
        )

        for chunk in stream:
            logger.debug(f"Stream chunk: {chunk}")
            if stream_mode == "messages":
                if isinstance(chunk[0], AIMessageChunk):
                    yield chunk[0].content
            else:
                yield chunk

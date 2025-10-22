from typing import Iterator, Any
from app.core.agents.builder import get_model, ModelConfig
from langchain.tools import tool, ToolRuntime
from langchain.agents import create_agent
from app.core.storage import LocalDocumentStorage
from app.core.agents.common import SupervisorRuntimeContext
from app.core.agents.resume_content_editor import resume_content_editor_tool


SUPERVISOR_AGENT_PROMPT = (
    "You are ApplAI Supervisor, an advanced AI assistant designed to help users with all "
    "aspects of resume creation and improvement. You have access to a variety of specialized "
    "agents to assist with this process. Each agent has a specific role and expertise, and you "
    "should delegate tasks to them as needed to provide the best possible assistance to the user."
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
            tools=[resume_content_editor_tool, list_resumes_tool],
            system_prompt=SUPERVISOR_AGENT_PROMPT,
            context_schema=SupervisorRuntimeContext,
        )

    # TODO: Update this to be a better generator
    def stream(
        self, prompt: str, stream_mode: str = "messages"
    ) -> Iterator[dict[str, Any] | Any]:
        return self.agent.stream(
            input={
                "messages": [{"role": "user", "content": prompt}],
            },
            context=SupervisorRuntimeContext(document_storage=self.document_storage),
        )

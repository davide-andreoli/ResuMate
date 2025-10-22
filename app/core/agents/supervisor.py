from typing import Iterator, Any
from app.core.agents.builder import get_model, ModelConfig
from app.core.agents.resume_content_editor import resume_content_editor_agent
from langchain.tools import tool, ToolRuntime
from langchain.agents import create_agent
from dataclasses import dataclass
from app.core.storage import LocalDocumentStorage


@dataclass
class SupervisorRuntimeContext:
    """
    Context class for the ApplAI Supervisor agent runtime.
    """

    document_storage: LocalDocumentStorage


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


@tool
def resume_content_editor_tool(
    runtime: ToolRuntime[SupervisorRuntimeContext], request: str
) -> str:
    """
    Resume Content Editor specialist tool to help users improve their resume content.
    Here is some example requests this tool can help with:
    - Analyzing and improving existing resume content
    - Suggesting new sections or bullet points to enhance the resume
    - Tailoring resume content for specific job descriptions
    - Providing feedback on clarity, conciseness, and impact of resume language

    Args:
        request (str): The user's request for resume content editing.

    Returns:
        str: The output from the resume content editor agent, it can either be confirmation, questions, etc.
    """
    result = resume_content_editor_agent.invoke(
        {"messages": [{"role": "user", "content": request}]}
    )

    return result["messages"][-1].text


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

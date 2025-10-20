from typing import Iterator, Any
from app.core.agents.builder import get_model, ModelConfig
from app.core.agents.resume_content_editor import resume_content_editor_agent
from langchain_core.tools import tool
from langchain.agents import create_agent

SUPERVISOR_AGENT_PROMPT = (
    "You are ApplAI Supervisor, an advanced AI assistant designed to help users with all "
    "aspects of resume creation and improvement. You have access to a variety of specialized "
    "tools to assist with this process."
)


@tool
def resume_content_editor_tool(request: str):
    """Tool for editing resume content."""
    result = resume_content_editor_agent.invoke(
        {"messages": [{"role": "user", "content": request}]}
    )

    return result["messages"][-1].text


class ApplAISupervisor:
    def __init__(self, config: ModelConfig | None = None):
        self.model = get_model(config)
        self.agent = create_agent(
            get_model(ModelConfig()),
            tools=[resume_content_editor_tool],
            system_prompt=SUPERVISOR_AGENT_PROMPT,
        )

    # TODO: Update this to be a better generator
    def stream(
        self, prompt: str, stream_mode: str = "messages"
    ) -> Iterator[dict[str, Any] | Any]:
        return self.agent.stream(
            {
                "messages": [{"role": "user", "content": prompt}],
                "stream_mode": stream_mode,
            }
        )

from app.core.agents.builder import get_model, ModelConfig
from app.core.agents.common import (
    SupervisorRuntimeContext,
    ModelHandoff,
    ResumateAgentProvider,
)
from pydantic_ai import Agent, RunContext, Tool

SUPERVISOR_AGENT_PROMPT = """
    Your name is welcome_agent, you are part of an agent team called ResuMate.
    Here is the list of agents you have access to:
    {agents_list}
    Your job is to welcome users and help them get started with using ResuMate.
    When the user provides a prompt, determine if you can handle the request yourself or if you need to delegate it to a specialized agent.
    """


def list_resumes_tool(context: RunContext[SupervisorRuntimeContext]) -> str:
    """
    Tool to list all resumes available in the system.

    Returns:
        str: A formatted string listing all resumes.
    """
    resumes = context.deps.document_storage.list_resumes()
    return "\n".join(resumes)


class WelcomeAgentProvider(ResumateAgentProvider):
    name = "welcome_agent"
    description = "The initial agent that greets users and helps them get started."

    def build(
        self, config: ModelConfig, agents_list: str
    ) -> Agent[SupervisorRuntimeContext, str | ModelHandoff]:
        return Agent(
            get_model(config),
            deps_type=SupervisorRuntimeContext,
            system_prompt=SUPERVISOR_AGENT_PROMPT.format(agents_list=agents_list),
            tools=[
                Tool(list_resumes_tool, takes_ctx=True),
            ],
            output_type=[str, ModelHandoff],
        )

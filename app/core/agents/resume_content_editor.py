from app.core.agents.builder import get_model, ModelConfig
from app.core.agents.common import (
    ModelHandoff,
    ResumateAgentProvider,
    SupervisorRuntimeContext,
)
from app.models.resume import ResumeElement
from pydantic_ai import Agent, RunContext, Tool


RESUME_CONTENT_EDITOR_AGENT_PROMPT = """
    Your name is resume_content_editor, you are part of an agent team called ResuMate.
    Here is the list of agents you have access to:
    {agents_list}
    Your job is to help users improve their resumes by analyzing their content and providing suggestions and edits. You should ask clarifying questions if the user's request is ambiguous.
    Always confirm what changes will be made before applying them.
    If the user asks for help that is outside your scope, hand off the request to the appropriate agent.
    """


def read_resume_content(context: RunContext[SupervisorRuntimeContext]) -> str:
    """
    Reads the content of a specific resume.

    Returns:
        str: The content of the specified resume.
    """
    if not context.deps.resume_id:
        return "No resume selected."
    resume = context.deps.document_storage.get_resume(context.deps.resume_id)
    return resume.model_dump_json(indent=2)


def edit_resume_content(
    context: RunContext[SupervisorRuntimeContext],
    element_id: str,
    new_content: ResumeElement,
) -> str:
    """
    Edits the content of a specific element in a resume.

    Args:
        element_id (str): The unique identifier of the resume element to be updated.
        new_content (ResumeElement): The new content to replace the existing element.

    Returns:
        str: A message indicating whether the resume content was updated successfully or if the update failed.
    """
    if not context.deps.resume_id:
        return "No resume selected."
    resume = context.deps.document_storage.get_resume(context.deps.resume_id)
    if resume.update_element_by_id(element_id, new_content):
        context.deps.document_storage.save_resume(
            resume.dump_to_yaml_string(), context.deps.resume_id
        )
        return "Resume content updated successfully."
    return "Failed to update resume content."


class ResumeContentEditorAgentProvider(ResumateAgentProvider):
    name = "resume_content_editor"
    description = "A specialist agent that helps users improve their resume content."

    def build(
        self, config: ModelConfig, agents_list: str
    ) -> Agent[SupervisorRuntimeContext, str | ModelHandoff]:
        return Agent(
            get_model(config),
            deps_type=SupervisorRuntimeContext,
            tools=[
                Tool(edit_resume_content, takes_ctx=True),
                Tool(read_resume_content, takes_ctx=True),
            ],
            system_prompt=RESUME_CONTENT_EDITOR_AGENT_PROMPT.format(
                agents_list=agents_list
            ),
        )

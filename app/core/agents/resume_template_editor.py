from app.core.agents.builder import get_model, ModelConfig
from app.core.agents.common import (
    ModelHandoff,
    ResumateAgentProvider,
    SupervisorRuntimeContext,
)
from pydantic_ai import Agent, RunContext, Tool


RESUME_TEMPLATE_EDITOR_AGENT_PROMPT = """
    Your name is resume_template_editor, you are part of an agent team called ResuMate.
    Here is the list of agents you have access to:
    {agents_list}
    You are a design specialist agent that helps users improve the structure and format of their resumes by modifying existing elements and improving them. You should ask clarifying questions if the user's request is ambiguous.
    Always confirm what changes will be made before applying them.
    """


def read_template_content(context: RunContext[SupervisorRuntimeContext]) -> str:
    """
    Reads the content of a specific resume template.

    Returns:
        str: The content of the specified resume template.
    """
    if not context.deps.template_id:
        return "No resume template selected."
    template = context.deps.document_storage.get_template(context.deps.template_id)
    return template.model_dump_json(indent=2)


def edit_template_html_content(
    context: RunContext[SupervisorRuntimeContext],
    new_content: str,
) -> str:
    """
    Edits the HTML content of a specific resume template.

    Args:
        new_content (str): The new HTML content for the resume template.

    Returns:
        str: A message indicating whether the resume template content was updated successfully or if the update failed.
    """
    if not context.deps.template_id:
        return "No resume template selected."
    template = context.deps.document_storage.get_template(context.deps.template_id)
    template.html_content = new_content
    context.deps.document_storage.save_template(template)
    return "Resume template content updated successfully."


class ResumeTemplateEditorAgentProvider(ResumateAgentProvider):
    name = "resume_template_editor"
    description = "A specialist agent that helps users improve their resume templates by modifying their design and layout."

    def build(
        self, config: ModelConfig, agents_list: str
    ) -> Agent[SupervisorRuntimeContext, str | ModelHandoff]:
        return Agent(
            get_model(config),
            deps_type=SupervisorRuntimeContext,
            tools=[
                Tool(edit_template_html_content, takes_ctx=True),
                Tool(read_template_content, takes_ctx=True),
            ],
            system_prompt=RESUME_TEMPLATE_EDITOR_AGENT_PROMPT.format(
                agents_list=agents_list
            ),
        )

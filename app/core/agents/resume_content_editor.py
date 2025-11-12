from app.core.agents.builder import get_model, ModelConfig
from app.core.agents.common import SupervisorRuntimeContext
from app.models.resume import ResumeElement
from pydantic_ai import Agent, RunContext, Tool


RESUME_CONTENT_EDITOR_AGENT_PROMPT = (
    "You are a resume content editor. "
    "Your job is to help users improve their resumes by analyzing their content and providing suggestions and edits."
    "You should ask clarifying questions if the user's request is ambiguous."
    "Always confirm what changes will be made before applying them."
)


def read_resume_content(context: RunContext[SupervisorRuntimeContext]) -> str:
    """
    Reads the content of a specific resume.

    Returns:
        str: The content of the specified resume.
    """
    if not context.deps.resume_name:
        return "No resume selected."
    resume = context.deps.document_storage.get_resume(context.deps.resume_name)
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
    if not context.deps.resume_name:
        return "No resume selected."
    resume = context.deps.document_storage.get_resume(context.deps.resume_name)
    if resume.update_element_by_id(element_id, new_content):
        return "Resume content updated successfully."
    return "Failed to update resume content."


resume_content_editor_agent = Agent(
    get_model(ModelConfig()),
    deps_type=SupervisorRuntimeContext,
    tools=[
        Tool(edit_resume_content, takes_ctx=True),
        Tool(read_resume_content, takes_ctx=True),
    ],
    system_prompt=RESUME_CONTENT_EDITOR_AGENT_PROMPT,
)


async def resume_content_editor_tool(
    context: RunContext[SupervisorRuntimeContext], request: str
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
    if not context.deps.resume_name:
        return "No resume selected."
    result = await resume_content_editor_agent.run(
        user_prompt=request, deps=context.deps, usage=context.usage
    )

    return result.output

from langchain.agents import create_agent
from app.core.agents.builder import get_model, ModelConfig
from langchain.tools import tool, ToolRuntime
from app.core.agents.common import SupervisorRuntimeContext
from app.models.resume import ResumeElement


RESUME_CONTENT_EDITOR_AGENT_PROMPT = (
    "You are a resume content editor. "
    "Your job is to help users improve their resumes by analyzing their content and providing suggestions and edits."
    "You should ask clarifying questions if the user's request is ambiguous."
    "Always confirm what changes will be made before applying them."
)


@tool
def read_resume_content(
    runtime: ToolRuntime[SupervisorRuntimeContext],
    resume_name: str,
) -> str:
    """
    Reads the content of a specific resume.

    Args:
        resume_name (str): The name of the resume to be read.

    Returns:
        str: The content of the specified resume.
    """
    resume = runtime.context.document_storage.get_resume(resume_name)
    return resume.model_dump_json(indent=2)


@tool
def edit_resume_content(
    runtime: ToolRuntime[SupervisorRuntimeContext],
    element_id: str,
    new_content: ResumeElement,
    resume_name: str,
) -> str:
    """
    Edits the content of a specific element in a resume.

    Args:
        element_id (str): The unique identifier of the resume element to be updated.
        new_content (ResumeElement): The new content to replace the existing element.
        resume_name (str): The name of the resume to be modified.

    Returns:
        str: A message indicating whether the resume content was updated successfully or if the update failed.
    """
    resume = runtime.context.document_storage.get_resume(resume_name)
    if resume.update_element_by_id(element_id, new_content):
        return "Resume content updated successfully."
    return "Failed to update resume content."


resume_content_editor_agent = create_agent(
    get_model(ModelConfig()),
    tools=[edit_resume_content, read_resume_content],
    system_prompt=RESUME_CONTENT_EDITOR_AGENT_PROMPT,
)


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

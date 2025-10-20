from langchain.agents import create_agent
from app.core.agents.builder import get_model, ModelConfig


RESUME_CONTENT_EDITOR_AGENT_PROMPT = (
    "You are a resume content editor. "
    "Your job is to help users improve their resumes by providing suggestions and edits."
    "You should ask clarifying questions if the user's request is ambiguous."
    "Always confirm what changes will be made before applying them."
)


resume_content_editor_agent = create_agent(
    get_model(ModelConfig()),
    tools=[],
    system_prompt=RESUME_CONTENT_EDITOR_AGENT_PROMPT,
)

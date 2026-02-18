from app.core.agents.common import SupervisorRuntimeContext
from app.core.agents.resume_content_editor import ResumeContentEditorAgentProvider
from pydantic_ai import Agent
from app.core.agents.builder import ModelConfig
from unittest.mock import MagicMock, patch, Mock
from google.oauth2 import service_account
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.providers.google import GoogleProvider


@patch("app.core.agents.builder.GoogleModel")
@patch("app.core.agents.builder.GoogleProvider")
@patch("app.core.agents.builder.service_account.Credentials.from_service_account_file")
def test_resume_content_editor_agent_provider(
    mock_from_file: MagicMock,
    mock_google_provider: MagicMock,
    mock_google_model: MagicMock,
    default_model_config: ModelConfig,
):
    mock_from_file.return_value = Mock(spec=service_account.Credentials)
    mock_google_provider.return_value = Mock(spec=GoogleProvider)
    mock_google_model.return_value = Mock(spec=GoogleModel)

    provider = ResumeContentEditorAgentProvider()
    assert provider.name == "resume_content_editor"
    assert (
        provider.description
        == "A specialist agent that helps users improve their resume content by modifying existing elements and improving them."
    )

    agent = provider.build(default_model_config, "agents_list")
    assert isinstance(agent, Agent)
    assert agent.deps_type == SupervisorRuntimeContext
    assert agent.model == mock_google_model.return_value

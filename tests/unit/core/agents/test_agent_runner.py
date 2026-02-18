from app.core.agents.agent_runner import ResumateAgentRunner
from app.core.agents.builder import ModelConfig
from app.core.agents.common import ModelHandoff
from unittest.mock import MagicMock, patch, Mock
from google.oauth2 import service_account
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.providers.google import GoogleProvider


@patch("app.core.agents.builder.GoogleModel")
@patch("app.core.agents.builder.GoogleProvider")
@patch("app.core.agents.builder.service_account.Credentials.from_service_account_file")
def test_resumate_agent_runner_initialization(
    mock_from_file: MagicMock,
    mock_google_provider: MagicMock,
    mock_google_model: MagicMock,
    default_model_config: ModelConfig,
):
    mock_from_file.return_value = Mock(spec=service_account.Credentials)
    mock_google_provider.return_value = Mock(spec=GoogleProvider)
    mock_google_model.return_value = Mock(spec=GoogleModel)

    runner = ResumateAgentRunner(config=default_model_config)
    assert runner.config == default_model_config
    assert len(runner.registered_agents_providers) == 4
    assert runner.current_agent is not None
    assert runner.pending_handoff is None


@patch("app.core.agents.builder.GoogleModel")
@patch("app.core.agents.builder.GoogleProvider")
@patch("app.core.agents.builder.service_account.Credentials.from_service_account_file")
def test_apply_handoff(
    mock_from_file: MagicMock,
    mock_google_provider: MagicMock,
    mock_google_model: MagicMock,
    default_model_config: ModelConfig,
):
    mock_from_file.return_value = Mock(spec=service_account.Credentials)
    mock_google_provider.return_value = Mock(spec=GoogleProvider)
    mock_google_model.return_value = Mock(spec=GoogleModel)

    runner = ResumateAgentRunner(config=default_model_config)
    handoff = ModelHandoff(target_agent="resume_content_editor")

    result = runner.apply_handoff()
    assert result is False
    runner.pending_handoff = handoff
    result = runner.apply_handoff()
    assert result is True
    assert runner.pending_handoff is None

    handoff = ModelHandoff(target_agent="not_a_real_agent")
    runner.pending_handoff = handoff
    result = runner.apply_handoff()
    assert result is False

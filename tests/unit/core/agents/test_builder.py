from app.core.agents.builder import ModelConfig, get_model
from pytest import MonkeyPatch
from pathlib import Path
from google.oauth2 import service_account
from unittest.mock import MagicMock, patch, Mock
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.providers.google import GoogleProvider


def test_model_config_environment_variables(monkeypatch: MonkeyPatch):
    monkeypatch.setenv("AGENT_PROVIDER", "google-vertex")
    monkeypatch.setenv("AGENT_CREDENTIALS_FILE", "test_credentials.json")
    monkeypatch.setenv("AGENT_PROJECT_ID", "test_project")
    monkeypatch.setenv("AGENT_MODEL_NAME", "test-model")
    monkeypatch.setenv("AGENT_MODEL_LOCATION", "test-location")

    config = ModelConfig()
    assert config.provider == "google-vertex"
    assert config.credentials_file == Path("test_credentials.json")
    assert config.project_id == "test_project"
    assert config.model_name == "test-model"
    assert config.model_location == "test-location"


@patch("app.core.agents.builder.GoogleModel")
@patch("app.core.agents.builder.GoogleProvider")
@patch("app.core.agents.builder.service_account.Credentials.from_service_account_file")
def test_get_model_with_credentials(
    mock_from_file: MagicMock,
    mock_google_provider: MagicMock,
    mock_google_model: MagicMock,
    default_model_config: ModelConfig,
):
    mock_from_file.return_value = Mock(spec=service_account.Credentials)
    mock_google_provider.return_value = Mock(spec=GoogleProvider)
    mock_google_model.return_value = Mock(spec=GoogleModel)

    result = get_model(default_model_config)

    mock_from_file.assert_called_once_with(
        "test_credentials.json",
        scopes=["https://www.googleapis.com/auth/cloud-platform"],
    )

    mock_google_provider.assert_called_once_with(
        credentials=mock_from_file.return_value,
        project=default_model_config.project_id,
        location=default_model_config.model_location,
    )

    mock_google_model.assert_called_once_with(
        default_model_config.model_name, provider=mock_google_provider.return_value
    )

    assert result == mock_google_model.return_value

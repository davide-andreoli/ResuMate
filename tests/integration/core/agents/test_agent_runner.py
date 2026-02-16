from app.core.agents.agent_runner import ResumateAgentRunner
from app.core.agents.builder import ModelConfig
from app.core.agents.common import ModelHandoff
from unittest.mock import MagicMock, patch, Mock
from google.oauth2 import service_account
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.providers.google import GoogleProvider
from app.core.memory.local_file_memory import LocalFileMemory
from pathlib import Path


@patch("app.core.agents.builder.GoogleModel")
@patch("app.core.agents.builder.GoogleProvider")
@patch("app.core.agents.builder.service_account.Credentials.from_service_account_file")
def test_record_handoff(
    mock_from_file: MagicMock,
    mock_google_provider: MagicMock,
    mock_google_model: MagicMock,
    default_model_config: ModelConfig,
    tmp_path: Path,
):
    mock_from_file.return_value = Mock(spec=service_account.Credentials)
    mock_google_provider.return_value = Mock(spec=GoogleProvider)
    mock_google_model.return_value = Mock(spec=GoogleModel)

    memory = LocalFileMemory(str(tmp_path))
    memory.create_conversation("test_conversation")

    runner = ResumateAgentRunner(config=default_model_config)
    handoff = ModelHandoff(target_agent="resume_content_editor")
    runner.record_handoff(handoff, memory=memory, conversation_id="test_conversation")

    retrieved_conversation = memory.get_conversation("test_conversation")
    assert retrieved_conversation is not None

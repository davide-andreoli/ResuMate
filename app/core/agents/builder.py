from enum import Enum
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
from google.oauth2 import service_account
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.providers.google import GoogleProvider
from pydantic_ai.models import Model


class ProviderName(str, Enum):
    google_vertex = "google-vertex"


class ModelConfig(BaseSettings):
    provider: ProviderName = ProviderName.google_vertex
    credentials_file: Optional[Path] = Path("credentials.json")
    project_id: Optional[str] = None
    model_name: str = "gemini-2.5-flash"

    class Config:
        env_prefix = "AGENT_"
        env_file = ".env"


def get_model(config: Optional[ModelConfig] = None) -> Model:
    config = config or ModelConfig()
    if config.provider == ProviderName.google_vertex:
        credentials = None
        if config.credentials_file:
            credentials = service_account.Credentials.from_service_account_file(
                str(config.credentials_file),
                scopes=["https://www.googleapis.com/auth/cloud-platform"],
            )
        provider = GoogleProvider(credentials=credentials, project=config.project_id)
        model = GoogleModel(config.model_name, provider=provider)
        return model

    raise ValueError(f"Unsupported provider: {config.provider}")

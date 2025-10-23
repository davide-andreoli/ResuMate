from pydantic import BaseModel, Field, model_validator
import secrets
import string
from typing import Any


def short_id(prefix: str = "", length: int = 8) -> str:
    """Generate a short random string ID with optional prefix."""
    alphabet = string.ascii_lowercase + string.digits
    return prefix + "".join(secrets.choice(alphabet) for _ in range(length))


class CvItem(BaseModel):
    id: str = Field(default_factory=lambda: short_id("cv_"))
    visible: bool = True
    schema_version: int = 1

    @model_validator(mode="before")
    def ensure_id(cls, data: Any) -> Any:
        """Ensure an id exists; compute prefix from the actual model class name."""
        if not isinstance(data, dict):
            return data
        if data.get("id"):
            return data
        prefix = cls.__name__.lower()[:3] + "_"
        data["id"] = short_id(prefix)
        return data

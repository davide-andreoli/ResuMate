from pydantic import BaseModel, Field, model_validator
from typing import Any, Dict, cast
from app.models.utils import short_id


class CvItem(BaseModel):
    id: str = Field(default_factory=lambda: short_id("cv_"))
    visible: bool = True
    schema_version: int = 1

    @model_validator(mode="before")
    def ensure_id(cls, data: Any) -> Any | Dict[str, Any]:
        """Ensure an id exists; compute prefix from the actual model class name."""
        if not isinstance(data, dict):
            return data
        if "id" in data and data["id"]:
            return cast(Dict[str, Any], data)
        prefix = cls.__name__.lower()[:3] + "_"
        data["id"] = short_id(prefix)
        return cast(Dict[str, Any], data)

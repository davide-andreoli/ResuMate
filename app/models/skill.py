from pydantic import BaseModel, Field


class Skill(BaseModel):
    name: str = ""
    level: int = Field(1, ge=1, le=5)
    schema_version: int = 1

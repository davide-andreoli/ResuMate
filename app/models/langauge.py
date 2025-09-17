from typing import Literal
from pydantic import BaseModel


class Language(BaseModel):
    name: str = ""
    proficiency: Literal["Basic", "Conversational", "Fluent", "Native"] = "Basic"
    visible: bool = True
    schema_version: int = 1

from pydantic import BaseModel
from typing import Literal, Optional


class Skill(BaseModel):
    name: str = ""
    level: Optional[Literal["Beginner", "Intermediate", "Advanced", "Expert"]] = (
        "Beginner"
    )
    visible: bool = True
    schema_version: int = 1

    @property
    def level_number(self) -> int:
        level_map = {
            "Beginner": 1,
            "Intermediate": 2,
            "Advanced": 3,
            "Expert": 4,
        }
        return level_map[str(self.level)]

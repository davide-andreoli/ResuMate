from typing import Literal, Optional
from app.models.cv_item import CvItem


class Skill(CvItem):
    name: str = ""
    level: Optional[Literal["Beginner", "Intermediate", "Advanced", "Expert"]] = (
        "Beginner"
    )

    @property
    def level_number(self) -> int:
        level_map = {
            "Beginner": 1,
            "Intermediate": 2,
            "Advanced": 3,
            "Expert": 4,
        }
        return level_map[str(self.level)]

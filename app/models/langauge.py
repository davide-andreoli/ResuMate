from typing import Literal
from app.models.cv_item import CvItem


class Language(CvItem):
    name: str = ""
    proficiency: Literal["Basic", "Conversational", "Fluent", "Native"] = "Basic"

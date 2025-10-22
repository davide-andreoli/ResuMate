from typing import Literal
from app.models.cv_item import CvItem


class Language(CvItem):
    id: str = CvItem.id_field()
    name: str = ""
    proficiency: Literal["Basic", "Conversational", "Fluent", "Native"] = "Basic"

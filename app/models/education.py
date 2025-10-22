from typing import Optional
from datetime import date
from app.models.cv_item import CvItem


class Education(CvItem):
    id: str = CvItem.id_field()
    institution: str = ""
    degree: str = ""
    start: Optional[date] = None
    end: Optional[date] = None
    details: Optional[str] = None
    location: Optional[str] = None
    visible: bool = True
    schema_version: int = 1

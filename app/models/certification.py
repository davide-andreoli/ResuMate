from pydantic import HttpUrl
from typing import Optional
from datetime import date
from app.models.cv_item import CvItem


class Certification(CvItem):
    id: str = CvItem.id_field()
    name: str = ""
    issuer: Optional[str] = None
    certification_date: Optional[date] = None
    credential_id: Optional[str] = None
    link: Optional[HttpUrl] = None

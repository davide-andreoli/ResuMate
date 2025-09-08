from pydantic import BaseModel, HttpUrl
from typing import Optional
from datetime import date


class Certification(BaseModel):
    name: str = ""
    issuer: Optional[str] = None
    certification_date: Optional[date] = None
    credential_id: Optional[str] = None
    link: Optional[HttpUrl] = None
    schema_version: int = 1

from pydantic import BaseModel, Field
import secrets
import string


def short_id(prefix: str = "", length: int = 8) -> str:
    """Generate a short random string ID with optional prefix."""
    alphabet = string.ascii_lowercase + string.digits
    return prefix + "".join(secrets.choice(alphabet) for _ in range(length))


class CvItem(BaseModel):
    id: str = Field(default_factory=lambda: short_id("cv_"))
    visible: bool = True
    schema_version: int = 1

    @classmethod
    def id_field(cls):
        """Generate a default_factory for class-specific ID prefixes."""
        prefix = cls.__name__.lower()[:3] + "_"
        return Field(default_factory=lambda: short_id(prefix))

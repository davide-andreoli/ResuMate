import secrets
import string


def short_id(prefix: str = "", length: int = 8) -> str:
    """Generate a short random string ID with optional prefix."""
    alphabet = string.ascii_lowercase + string.digits
    return prefix + "".join(secrets.choice(alphabet) for _ in range(length))

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.app_setting import AppSetting

_settings = get_settings()


def get_default_lives(db: Session) -> int:
    """Reads `default_lives` from the AppSetting table (DB-editable), falling back to the
    hardcoded config default if no row is present. Lets difficulty be tuned without a deploy."""
    row = db.get(AppSetting, "default_lives")
    if row is None:
        return _settings.default_lives
    try:
        return int(row.value)
    except ValueError:
        return _settings.default_lives


def lives_for_challenge(db: Session, lives_override: int | None) -> int:
    if lives_override is not None:
        return lives_override
    return get_default_lives(db)

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import decode_access_token
from app.models.user import User

__all__ = ["get_db", "get_current_user"]


def get_current_user(
    db: Session = Depends(get_db),
    authorization: str | None = Header(default=None),
    x_device_id: str | None = Header(default=None, alias="X-Device-Id"),
) -> User:
    """Resolves the acting player: a logged-in account (Bearer JWT) takes priority,
    otherwise falls back to (and lazily creates) a guest identified by X-Device-Id."""
    if authorization and authorization.lower().startswith("bearer "):
        token = authorization.split(" ", 1)[1]
        user_id = decode_access_token(token)
        if user_id is not None:
            user = db.get(User, int(user_id))
            if user is not None:
                return user
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or expired token")

    if not x_device_id:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "Missing X-Device-Id header (or Authorization bearer token)",
        )

    user = db.query(User).filter(User.device_id == x_device_id).first()
    if user is None:
        user = User(device_id=x_device_id)
        db.add(user)
        db.commit()
        db.refresh(user)
    return user

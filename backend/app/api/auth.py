from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.core.security import create_access_token, hash_password, verify_password
from app.models.game_attempt import MODE_LIVES, GameAttempt
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest, TokenOut, UpgradeGuestRequest

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenOut)
def register(body: RegisterRequest, db: Session = Depends(get_db)) -> TokenOut:
    if db.query(User).filter(User.email == body.email).first() is not None:
        raise HTTPException(status.HTTP_409_CONFLICT, "Email already registered")

    user = None
    if body.device_id:
        user = db.query(User).filter(User.device_id == body.device_id).first()

    if user is not None:
        user.email = body.email
        user.password_hash = hash_password(body.password)
    else:
        user = User(email=body.email, password_hash=hash_password(body.password))
        db.add(user)

    db.commit()
    db.refresh(user)
    return TokenOut(access_token=create_access_token(str(user.id)))


@router.post("/login", response_model=TokenOut)
def login(body: LoginRequest, db: Session = Depends(get_db)) -> TokenOut:
    user = db.query(User).filter(User.email == body.email).first()
    if user is None or not user.password_hash or not verify_password(body.password, user.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid email or password")
    return TokenOut(access_token=create_access_token(str(user.id)))


@router.post("/upgrade-guest", response_model=TokenOut)
def upgrade_guest(body: UpgradeGuestRequest, db: Session = Depends(get_db)) -> TokenOut:
    """Turns an anonymous device_id's history into a real account, merging any
    game attempts already recorded under the guest identity."""
    if db.query(User).filter(User.email == body.email).first() is not None:
        raise HTTPException(status.HTTP_409_CONFLICT, "Email already registered")

    guest = db.query(User).filter(User.device_id == body.device_id).first()
    if guest is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No guest history found for this device")

    guest.email = body.email
    guest.password_hash = hash_password(body.password)
    db.commit()
    db.refresh(guest)
    return TokenOut(access_token=create_access_token(str(guest.id)))


@router.get("/me")
def me(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    # só o jogo diário (5 vidas) conta para o placar pessoal; o modo infinito é treino
    attempts = (
        db.query(GameAttempt)
        .filter(GameAttempt.user_id == user.id, GameAttempt.mode == MODE_LIVES)
        .all()
    )
    return {
        "id": user.id,
        "email": user.email,
        "is_guest": user.email is None,
        "games_played": sum(1 for a in attempts if a.is_over),
        "exact_hits": sum(1 for a in attempts if a.exact_hit),
    }

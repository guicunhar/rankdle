from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.theme import Theme
from app.schemas.theme import ThemeOut

router = APIRouter(prefix="/themes", tags=["themes"])


@router.get("", response_model=list[ThemeOut])
def list_themes(db: Session = Depends(get_db)) -> list[Theme]:
    stmt = select(Theme).where(Theme.active.is_(True)).order_by(Theme.id)
    return list(db.scalars(stmt).all())

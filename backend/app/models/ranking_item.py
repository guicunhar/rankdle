from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


class RankingItem(Base):
    __tablename__ = "ranking_items"
    __table_args__ = (
        UniqueConstraint("daily_challenge_id", "rank", name="uq_ranking_item_challenge_rank"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    daily_challenge_id: Mapped[int] = mapped_column(ForeignKey("daily_challenges.id"))
    rank: Mapped[int] = mapped_column(Integer, index=True)
    name: Mapped[str] = mapped_column(String(200), index=True)
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    daily_challenge: Mapped["DailyChallenge"] = relationship(back_populates="items")

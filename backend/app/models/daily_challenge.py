from datetime import date as date_type

from sqlalchemy import Date, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


class DailyChallenge(Base):
    __tablename__ = "daily_challenges"
    __table_args__ = (UniqueConstraint("date", "theme_id", name="uq_daily_challenge_date_theme"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    date: Mapped[date_type] = mapped_column(Date, index=True)
    theme_id: Mapped[int] = mapped_column(ForeignKey("themes.id"))
    subtheme_title: Mapped[str] = mapped_column(String(200))
    target_rank: Mapped[int] = mapped_column(Integer)
    lives_override: Mapped[int | None] = mapped_column(Integer, nullable=True)
    source_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    theme: Mapped["Theme"] = relationship(back_populates="daily_challenges")
    items: Mapped[list["RankingItem"]] = relationship(
        back_populates="daily_challenge", order_by="RankingItem.rank"
    )
    attempts: Mapped[list["GameAttempt"]] = relationship(back_populates="daily_challenge")

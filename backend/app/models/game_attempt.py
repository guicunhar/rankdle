from datetime import datetime, timezone

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


class GameAttempt(Base):
    __tablename__ = "game_attempts"
    __table_args__ = (
        UniqueConstraint("daily_challenge_id", "user_id", name="uq_attempt_challenge_user"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    daily_challenge_id: Mapped[int] = mapped_column(ForeignKey("daily_challenges.id"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)

    # list of {"rank_guessed": int, "item_name": str, "score": int, "diff": int, "timestamp": iso str}
    guesses: Mapped[list[dict]] = mapped_column(JSON, default=list)
    best_score: Mapped[int] = mapped_column(Integer, default=0)
    exact_hit: Mapped[bool] = mapped_column(Boolean, default=False)
    lives_total: Mapped[int] = mapped_column(Integer)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    daily_challenge: Mapped["DailyChallenge"] = relationship(back_populates="attempts")
    user: Mapped["User"] = relationship(back_populates="attempts")

    @property
    def attempts_used(self) -> int:
        return len(self.guesses)

    @property
    def lives_remaining(self) -> int:
        return max(0, self.lives_total - self.attempts_used)

    @property
    def is_over(self) -> bool:
        return self.exact_hit or self.lives_remaining <= 0

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.game_attempt import MODE_LIVES, GameAttempt


def compute_challenge_stats(db: Session, daily_challenge_id: int) -> dict:
    """Aggregates only over daily (5-lives) attempts that finished (exact hit or lives
    exhausted). Infinite-mode attempts are excluded so a player chasing the exact
    answer with unlimited guesses can't skew the community averages."""
    completed = select(GameAttempt).where(
        GameAttempt.daily_challenge_id == daily_challenge_id,
        GameAttempt.mode == MODE_LIVES,
        GameAttempt.completed_at.is_not(None),
    )
    attempts = list(db.scalars(completed).all())

    players_count = len(attempts)
    exact_hit_count = sum(1 for a in attempts if a.exact_hit)
    closest_score = max((a.best_score for a in attempts), default=None)
    average_score = (
        sum(a.best_score for a in attempts) / players_count if players_count else None
    )

    return {
        "players_count": players_count,
        "exact_hit_count": exact_hit_count,
        "closest_score": closest_score,
        "average_score": average_score,
    }

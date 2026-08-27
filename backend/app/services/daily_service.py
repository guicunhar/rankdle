from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.daily_challenge import DailyChallenge
from app.models.game_attempt import GameAttempt
from app.models.ranking_item import RankingItem
from app.models.user import User
from app.schemas.daily import DailyChallengeOut, GuessResultOut
from app.services.scoring import direction_for_guess, score_for_guess
from app.services.settings_service import lives_for_challenge


def get_or_create_attempt(db: Session, challenge: DailyChallenge, user: User) -> GameAttempt:
    attempt = (
        db.query(GameAttempt)
        .filter(
            GameAttempt.daily_challenge_id == challenge.id,
            GameAttempt.user_id == user.id,
        )
        .first()
    )
    if attempt is None:
        attempt = GameAttempt(
            daily_challenge_id=challenge.id,
            user_id=user.id,
            guesses=[],
            best_score=0,
            exact_hit=False,
            lives_total=lives_for_challenge(db, challenge.lives_override),
        )
        db.add(attempt)
        db.commit()
        db.refresh(attempt)
    return attempt


def guess_results_from_json(raw_guesses: list[dict]) -> list[GuessResultOut]:
    return [
        GuessResultOut(
            rank_guessed=g["rank_guessed"],
            item_name=g["item_name"],
            score=g["score"],
            diff=g["diff"],
            direction=g["direction"],
        )
        for g in raw_guesses
    ]


def build_daily_out(challenge: DailyChallenge, attempt: GameAttempt) -> DailyChallengeOut:
    return DailyChallengeOut(
        id=challenge.id,
        date=challenge.date,
        theme=challenge.theme.name,
        theme_icon=challenge.theme.icon,
        subtheme_title=challenge.subtheme_title,
        target_rank=challenge.target_rank,
        total_items=len(challenge.items),
        lives_total=attempt.lives_total,
        lives_remaining=attempt.lives_remaining,
        attempts_used=attempt.attempts_used,
        guesses=guess_results_from_json(attempt.guesses),
        is_over=attempt.is_over,
        best_score=attempt.best_score,
    )


def register_guess(
    db: Session, challenge: DailyChallenge, attempt: GameAttempt, item: RankingItem
) -> GuessResultOut:
    score = score_for_guess(item.rank, challenge.target_rank)
    direction = direction_for_guess(item.rank, challenge.target_rank)
    diff = abs(item.rank - challenge.target_rank)

    result = GuessResultOut(
        rank_guessed=item.rank,
        item_name=item.name,
        score=score,
        diff=diff,
        direction=direction,
    )

    attempt.guesses = [*attempt.guesses, result.model_dump()]
    attempt.best_score = max(attempt.best_score, score)
    if direction == "correct":
        attempt.exact_hit = True
    if attempt.is_over and attempt.completed_at is None:
        attempt.completed_at = datetime.now(timezone.utc)

    db.add(attempt)
    db.commit()
    db.refresh(attempt)
    return result

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.daily_challenge import DailyChallenge
from app.models.game_attempt import MODE_INFINITE, MODE_LIVES, GameAttempt
from app.models.ranking_item import RankingItem
from app.models.user import User
from app.schemas.daily import DailyChallengeOut, GuessResultOut
from app.services.scoring import direction_for_guess, score_for_guess
from app.services.settings_service import lives_for_challenge


def get_or_create_attempt(
    db: Session, challenge: DailyChallenge, user: User, mode: str = MODE_LIVES
) -> GameAttempt:
    attempt = (
        db.query(GameAttempt)
        .filter(
            GameAttempt.daily_challenge_id == challenge.id,
            GameAttempt.user_id == user.id,
            GameAttempt.mode == mode,
        )
        .first()
    )
    if attempt is None:
        attempt = GameAttempt(
            daily_challenge_id=challenge.id,
            user_id=user.id,
            mode=mode,
            guesses=[],
            best_score=0,
            exact_hit=False,
            # o modo infinito não usa vidas; 0 deixa isso explícito na coluna
            lives_total=0
            if mode == MODE_INFINITE
            else lives_for_challenge(db, challenge.lives_override),
        )
        if mode == MODE_INFINITE:
            _seed_infinite_from_lives(db, challenge, user, attempt)
        db.add(attempt)
        db.commit()
        db.refresh(attempt)
    return attempt


def _seed_infinite_from_lives(
    db: Session, challenge: DailyChallenge, user: User, attempt: GameAttempt
) -> None:
    """O modo infinito é uma continuação do jogo diário: começa já com os palpites
    que o jogador fez nas 5 vidas, para ele seguir tentando sem recomeçar do zero."""
    lives_attempt = (
        db.query(GameAttempt)
        .filter(
            GameAttempt.daily_challenge_id == challenge.id,
            GameAttempt.user_id == user.id,
            GameAttempt.mode == MODE_LIVES,
        )
        .first()
    )
    if lives_attempt is None:
        return
    attempt.guesses = list(lives_attempt.guesses)
    attempt.best_score = lives_attempt.best_score
    attempt.exact_hit = lives_attempt.exact_hit
    if attempt.exact_hit:
        attempt.completed_at = datetime.now(timezone.utc)


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
        mode=attempt.mode,
        lives_total=attempt.lives_total,
        lives_remaining=attempt.lives_remaining,
        attempts_used=attempt.attempts_used,
        guesses=guess_results_from_json(attempt.guesses),
        is_over=attempt.is_over,
        gave_up=attempt.gave_up,
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

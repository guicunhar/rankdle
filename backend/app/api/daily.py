from datetime import date as date_type

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.core.clock import game_today
from app.models.daily_challenge import DailyChallenge
from app.models.game_attempt import GameAttempt
from app.models.ranking_item import RankingItem
from app.models.theme import Theme
from app.models.user import User
from app.schemas.daily import (
    ArchiveEntryOut,
    DailyChallengeOut,
    DailyResultOut,
    GuessRequest,
    GuessResponseOut,
    RevealItemOut,
    SearchItemOut,
)
from app.services.daily_service import (
    build_daily_out,
    get_or_create_attempt,
    guess_results_from_json,
    register_guess,
)
from app.services.stats_service import compute_challenge_stats

router = APIRouter(tags=["daily"])


def _get_challenge_or_404(db: Session, challenge_id: int) -> DailyChallenge:
    challenge = db.get(DailyChallenge, challenge_id)
    if challenge is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Daily challenge not found")
    return challenge


@router.get("/daily", response_model=DailyChallengeOut)
def get_daily(
    theme: str,
    date: date_type | None = Query(default=None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> DailyChallengeOut:
    target_date = date or game_today()
    stmt = (
        select(DailyChallenge)
        .join(Theme)
        .where(Theme.slug == theme, DailyChallenge.date == target_date)
    )
    challenge = db.scalars(stmt).first()
    if challenge is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No challenge for this theme/date")

    attempt = get_or_create_attempt(db, challenge, user)
    return build_daily_out(challenge, attempt)


@router.get("/daily/{challenge_id}/search", response_model=list[SearchItemOut])
def search_items(
    challenge_id: int,
    q: str = Query(default="", min_length=0),
    limit: int = Query(default=10, le=200),
    db: Session = Depends(get_db),
) -> list[RankingItem]:
    """Lets the player browse candidate items (e.g. with an empty `q`, before typing
    anything) or filter by a substring. Always shuffled, never ordered by rank/id, so
    the option order itself can't leak anything about the real ranking."""
    challenge = _get_challenge_or_404(db, challenge_id)
    stmt = select(RankingItem).where(RankingItem.daily_challenge_id == challenge.id)
    if q:
        stmt = stmt.where(RankingItem.name.ilike(f"%{q}%"))
    stmt = stmt.order_by(func.random()).limit(limit)
    return list(db.scalars(stmt).all())


@router.post("/daily/{challenge_id}/guess", response_model=GuessResponseOut)
def submit_guess(
    challenge_id: int,
    body: GuessRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> GuessResponseOut:
    challenge = _get_challenge_or_404(db, challenge_id)
    attempt = get_or_create_attempt(db, challenge, user)

    if attempt.is_over:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Game already finished for this challenge")

    item = db.get(RankingItem, body.item_id)
    if item is None or item.daily_challenge_id != challenge.id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Item does not belong to this challenge")

    guess = register_guess(db, challenge, attempt, item)

    return GuessResponseOut(
        guess=guess,
        lives_remaining=attempt.lives_remaining,
        best_score=attempt.best_score,
        is_over=attempt.is_over,
        exact_hit=attempt.exact_hit,
    )


@router.get("/daily/{challenge_id}/result", response_model=DailyResultOut)
def get_result(
    challenge_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> DailyResultOut:
    challenge = _get_challenge_or_404(db, challenge_id)
    attempt = get_or_create_attempt(db, challenge, user)
    if not attempt.is_over:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Game is not finished yet")

    answer = next(item for item in challenge.items if item.rank == challenge.target_rank)
    stats = compute_challenge_stats(db, challenge.id)

    return DailyResultOut(
        daily_challenge_id=challenge.id,
        target_rank=challenge.target_rank,
        answer=RevealItemOut(rank=answer.rank, name=answer.name, image_url=answer.image_url),
        source_url=challenge.source_url,
        player_best_score=attempt.best_score,
        player_exact_hit=attempt.exact_hit,
        player_guesses=guess_results_from_json(attempt.guesses),
        players_count=stats["players_count"],
        exact_hit_count=stats["exact_hit_count"],
        closest_score=stats["closest_score"],
        average_score=stats["average_score"],
    )


@router.get("/archive", response_model=list[ArchiveEntryOut])
def get_archive(
    theme: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[ArchiveEntryOut]:
    stmt = (
        select(DailyChallenge)
        .join(Theme)
        .where(Theme.slug == theme, DailyChallenge.date <= game_today())
        .order_by(DailyChallenge.date.desc())
    )
    challenges = list(db.scalars(stmt).all())

    attempts = {
        a.daily_challenge_id: a
        for a in db.query(GameAttempt).filter(
            GameAttempt.user_id == user.id,
            GameAttempt.daily_challenge_id.in_([c.id for c in challenges]),
        )
    }

    return [
        ArchiveEntryOut(
            id=c.id,
            date=c.date,
            subtheme_title=c.subtheme_title,
            played=c.id in attempts and attempts[c.id].is_over,
            best_score=attempts[c.id].best_score if c.id in attempts else None,
        )
        for c in challenges
    ]

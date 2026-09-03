from datetime import date as date_type

from pydantic import BaseModel


class DailyChallengeOut(BaseModel):
    id: int
    date: date_type
    theme: str
    theme_icon: str
    subtheme_title: str
    target_rank: int
    total_items: int
    mode: str  # "lives" | "infinite"
    lives_total: int
    # progress for the requesting player, if a session already exists
    lives_remaining: int
    attempts_used: int
    guesses: list["GuessResultOut"]
    is_over: bool
    gave_up: bool
    best_score: int


class SearchItemOut(BaseModel):
    id: int
    name: str
    image_url: str | None = None


class GuessRequest(BaseModel):
    item_id: int


class GuessResultOut(BaseModel):
    rank_guessed: int
    item_name: str
    score: int
    diff: int
    direction: str  # "correct" | "higher" | "lower"


class GuessResponseOut(BaseModel):
    guess: GuessResultOut
    lives_remaining: int
    attempts_used: int
    best_score: int
    is_over: bool
    exact_hit: bool


class RevealItemOut(BaseModel):
    rank: int
    name: str
    image_url: str | None = None


class DailyResultOut(BaseModel):
    daily_challenge_id: int
    target_rank: int
    answer: RevealItemOut
    source_url: str | None
    mode: str  # "lives" | "infinite"
    player_best_score: int
    player_exact_hit: bool
    player_gave_up: bool
    player_attempts: int
    player_guesses: list[GuessResultOut]
    players_count: int
    exact_hit_count: int
    closest_score: int | None
    average_score: float | None


class ArchiveEntryOut(BaseModel):
    id: int
    date: date_type
    subtheme_title: str
    played: bool
    best_score: int | None

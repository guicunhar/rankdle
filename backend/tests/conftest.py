import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.db import Base, get_db
from app.main import app
from app.models.daily_challenge import DailyChallenge
from app.models.ranking_item import RankingItem
from app.models.theme import Theme

engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


@pytest.fixture(autouse=True)
def _reset_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def _override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = _override_get_db


@pytest.fixture
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def sample_challenge(db_session):
    """A theme + daily challenge with 50 ranking items, target rank 34."""
    theme = Theme(slug="musica", name="Música", icon="🎵", active=True)
    db_session.add(theme)
    db_session.commit()
    db_session.refresh(theme)

    challenge = DailyChallenge(
        date=date(2026, 8, 26),
        theme_id=theme.id,
        subtheme_title="Músicas mais ouvidas em 2010",
        target_rank=34,
    )
    db_session.add(challenge)
    db_session.commit()
    db_session.refresh(challenge)

    for rank in range(1, 51):
        db_session.add(
            RankingItem(daily_challenge_id=challenge.id, rank=rank, name=f"Item {rank}")
        )
    db_session.commit()

    return challenge

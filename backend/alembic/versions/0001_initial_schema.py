"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-08-26

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "themes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("slug", sa.String(50), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("icon", sa.String(10), nullable=False, server_default=""),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.create_index("ix_themes_slug", "themes", ["slug"], unique=True)

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("password_hash", sa.String(255), nullable=True),
        sa.Column("device_id", sa.String(64), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_device_id", "users", ["device_id"], unique=True)

    op.create_table(
        "app_settings",
        sa.Column("key", sa.String(100), primary_key=True),
        sa.Column("value", sa.String(500), nullable=False),
    )

    op.create_table(
        "daily_challenges",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("theme_id", sa.Integer(), sa.ForeignKey("themes.id"), nullable=False),
        sa.Column("subtheme_title", sa.String(200), nullable=False),
        sa.Column("target_rank", sa.Integer(), nullable=False),
        sa.Column("lives_override", sa.Integer(), nullable=True),
        sa.UniqueConstraint("date", "theme_id", name="uq_daily_challenge_date_theme"),
    )
    op.create_index("ix_daily_challenges_date", "daily_challenges", ["date"])

    op.create_table(
        "ranking_items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "daily_challenge_id",
            sa.Integer(),
            sa.ForeignKey("daily_challenges.id"),
            nullable=False,
        ),
        sa.Column("rank", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("image_url", sa.String(500), nullable=True),
        sa.UniqueConstraint(
            "daily_challenge_id", "rank", name="uq_ranking_item_challenge_rank"
        ),
    )
    op.create_index("ix_ranking_items_rank", "ranking_items", ["rank"])
    op.create_index("ix_ranking_items_name", "ranking_items", ["name"])

    op.create_table(
        "game_attempts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "daily_challenge_id",
            sa.Integer(),
            sa.ForeignKey("daily_challenges.id"),
            nullable=False,
        ),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("guesses", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("best_score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("exact_hit", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("lives_total", sa.Integer(), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.UniqueConstraint("daily_challenge_id", "user_id", name="uq_attempt_challenge_user"),
    )
    op.create_index("ix_game_attempts_daily_challenge_id", "game_attempts", ["daily_challenge_id"])
    op.create_index("ix_game_attempts_user_id", "game_attempts", ["user_id"])


def downgrade() -> None:
    op.drop_table("game_attempts")
    op.drop_table("ranking_items")
    op.drop_table("daily_challenges")
    op.drop_table("app_settings")
    op.drop_table("users")
    op.drop_table("themes")

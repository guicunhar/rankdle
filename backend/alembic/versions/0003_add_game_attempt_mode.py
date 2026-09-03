"""add game_attempts.mode + gave_up for infinite mode

Revision ID: 0003
Revises: 0002
Create Date: 2026-09-03

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("game_attempts") as batch_op:
        batch_op.add_column(
            sa.Column("mode", sa.String(20), nullable=False, server_default="lives")
        )
        batch_op.add_column(
            sa.Column("gave_up", sa.Boolean(), nullable=False, server_default=sa.false())
        )
        batch_op.drop_constraint("uq_attempt_challenge_user", type_="unique")
        batch_op.create_unique_constraint(
            "uq_attempt_challenge_user_mode",
            ["daily_challenge_id", "user_id", "mode"],
        )


def downgrade() -> None:
    with op.batch_alter_table("game_attempts") as batch_op:
        batch_op.drop_constraint("uq_attempt_challenge_user_mode", type_="unique")
        batch_op.create_unique_constraint(
            "uq_attempt_challenge_user",
            ["daily_challenge_id", "user_id"],
        )
        batch_op.drop_column("gave_up")
        batch_op.drop_column("mode")

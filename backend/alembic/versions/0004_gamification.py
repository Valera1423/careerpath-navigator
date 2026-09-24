"""gamification: user_progress, achievements

Revision ID: 0004
Revises: 0003
Create Date: 2026-01-03
"""
from alembic import op
import sqlalchemy as sa


revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "user_progress",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column("xp", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("level", sa.String(30), nullable=False, server_default="intern"),
        sa.Column("streak_days", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_activity", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "achievements",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("code", sa.String(60), nullable=False),
        sa.Column("unlocked_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_achievements_user_id", "achievements", ["user_id"])
    op.create_index("ix_achievements_code", "achievements", ["code"])


def downgrade() -> None:
    op.drop_table("achievements")
    op.drop_table("user_progress")
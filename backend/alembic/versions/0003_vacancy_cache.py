"""vacancy cache

Revision ID: 0003
Revises: 0002
Create Date: 2026-01-02
"""
from alembic import op
import sqlalchemy as sa


revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "vacancy_cache",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("cache_key", sa.String(300), nullable=False, unique=True),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("source", sa.String(20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_vacancy_cache_cache_key", "vacancy_cache", ["cache_key"])
    op.create_index("ix_vacancy_cache_created_at", "vacancy_cache", ["created_at"])


def downgrade() -> None:
    op.drop_table("vacancy_cache")
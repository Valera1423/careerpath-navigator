"""simulator sessions

Revision ID: 0007
Revises: 0006
Create Date: 2026-01-06
"""
from alembic import op
import sqlalchemy as sa


revision = "0007"
down_revision = "0006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Таблицы employer_accounts, student_verifications, employer_access_log
    # уже созданы миграцией 0002. Здесь добавляем только то, чего нет:
    # simulator_sessions.
    op.create_table(
        "simulator_sessions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("scenario_id", sa.String(80), nullable=False),
        sa.Column("current_node", sa.String(80), nullable=False),
        sa.Column("path_taken", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("skills_gained", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("gaps_found", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("xp_earned", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_finished", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_simulator_sessions_user_id", "simulator_sessions", ["user_id"]
    )


def downgrade() -> None:
    op.drop_index("ix_simulator_sessions_user_id", table_name="simulator_sessions")
    op.drop_table("simulator_sessions")
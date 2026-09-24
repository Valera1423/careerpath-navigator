"""applications, interview sessions, plan due_date

Revision ID: 0005
Revises: 0004
Create Date: 2026-01-04
"""
from alembic import op
import sqlalchemy as sa


revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "plan_steps",
        sa.Column("due_date", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "plan_steps",
        sa.Column("depends_on", sa.JSON(), nullable=False, server_default="[]"),
    )

    op.create_table(
        "applications",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("vacancy_id", sa.String(120), nullable=False),
        sa.Column("vacancy_title", sa.String(300), nullable=False),
        sa.Column("vacancy_url", sa.String(500), nullable=True),
        sa.Column("company", sa.String(200), nullable=True),
        sa.Column("status", sa.String(30), nullable=False, server_default="applied"),
        sa.Column("applied_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("remind_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_applications_user_id", "applications", ["user_id"])
    op.create_index("ix_applications_remind_at", "applications", ["remind_at"])

    op.create_table(
        "interview_sessions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("position", sa.String(200), nullable=False),
        sa.Column("questions", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("answers", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("total_score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_finished", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_interview_sessions_user_id", "interview_sessions", ["user_id"])


def downgrade() -> None:
    op.drop_table("interview_sessions")
    op.drop_table("applications")
    op.drop_column("plan_steps", "depends_on")
    op.drop_column("plan_steps", "due_date")
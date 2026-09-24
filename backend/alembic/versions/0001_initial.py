"""initial: users, plan_steps

Revision ID: 0001
Revises:
Create Date: 2026-01-01
"""
from alembic import op
import sqlalchemy as sa


revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("max_user_id", sa.String(64), nullable=False, unique=True),
        sa.Column("full_name", sa.String(200), nullable=True),
        sa.Column("desired_position", sa.String(200), nullable=False),
        sa.Column("region", sa.String(120), nullable=True),
        sa.Column("experience", sa.String(50), nullable=False, server_default="none"),
        sa.Column("skills", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_users_max_user_id", "users", ["max_user_id"])
    op.create_index("ix_users_desired_position", "users", ["desired_position"])

    op.create_table(
        "plan_steps",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("order_index", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("skill", sa.String(80), nullable=False),
        sa.Column("title", sa.String(300), nullable=False),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column("kind", sa.String(30), nullable=False, server_default="course"),
        sa.Column("resource_url", sa.String(500), nullable=True),
        sa.Column("is_done", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_plan_steps_user_id", "plan_steps", ["user_id"])
    op.create_index("ix_plan_steps_skill", "plan_steps", ["skill"])


def downgrade() -> None:
    op.drop_table("plan_steps")
    op.drop_table("users")
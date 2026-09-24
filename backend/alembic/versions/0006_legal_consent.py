"""legal consent: consent_pd, employer_opt_in

Revision ID: 0006
Revises: 0005
Create Date: 2026-01-05
"""
from alembic import op
import sqlalchemy as sa


revision = "0006"
down_revision = "0005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("consent_pd_given_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "users",
        sa.Column("employer_opt_in", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column(
        "users",
        sa.Column("employer_opt_in_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("users", "employer_opt_in_at")
    op.drop_column("users", "employer_opt_in")
    op.drop_column("users", "consent_pd_given_at")
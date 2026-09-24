"""guardian consent for minors (152-ФЗ)

Revision ID: 0008
Revises: 0007
Create Date: 2026-01-07
"""
from alembic import op
import sqlalchemy as sa


revision = "0008"
down_revision = "0007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Согласие законного представителя (родителя/опекуна) на обработку
    # ПДн несовершеннолетнего пользователя. Заполняется при первом
    # заходе в раздел «Школьникам» (SchoolMode).
    op.add_column(
        "users",
        sa.Column("consent_pd_guardian_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "users",
        sa.Column("age_confirmed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "users",
        sa.Column("is_minor", sa.Boolean(), nullable=False, server_default=sa.false()),
    )


def downgrade() -> None:
    op.drop_column("users", "is_minor")
    op.drop_column("users", "age_confirmed_at")
    op.drop_column("users", "consent_pd_guardian_at")
"""employer accounts, verifications, access log

Revision ID: 0002
Revises: 0001
Create Date: 2026-01-01
"""
from alembic import op
import sqlalchemy as sa


revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "employer_accounts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("company_name", sa.String(200), nullable=False),
        sa.Column("contact_email", sa.String(200), nullable=False, unique=True),
        sa.Column("api_key_hash", sa.String(128), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("rate_limit_per_hour", sa.Integer(), nullable=False, server_default="1000"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_employer_accounts_company_name", "employer_accounts", ["company_name"])

    op.create_table(
        "student_verifications",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("skill", sa.String(80), nullable=False),
        sa.Column("evidence_type", sa.String(40), nullable=False),
        sa.Column("evidence_url", sa.String(500), nullable=True),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("verified_by", sa.String(40), nullable=False, server_default="auto"),
    )
    op.create_index("ix_student_verifications_user_id", "student_verifications", ["user_id"])

    op.create_table(
        "employer_access_log",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("employer_id", sa.Integer(), sa.ForeignKey("employer_accounts.id"), nullable=False),
        sa.Column("student_user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("accessed_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_employer_access_log_employer_id", "employer_access_log", ["employer_id"])


def downgrade() -> None:
    op.drop_table("employer_access_log")
    op.drop_table("student_verifications")
    op.drop_table("employer_accounts")
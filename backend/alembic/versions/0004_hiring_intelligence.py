"""Add hiring intelligence run and prospect persistence.

Revision ID: 0004
Revises: 0003
Create Date: 2026-10-15
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "hiring_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("run_date", sa.Date(), nullable=False),
        sa.Column("status", sa.String(length=24), nullable=False, server_default="pending"),
        sa.Column("candidates_seen", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("candidates_qualified", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("run_date", name="uq_hiring_runs_run_date"),
    )

    op.create_table(
        "hiring_prospects",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("company_name", sa.String(length=255), nullable=False),
        sa.Column("company_domain", sa.String(length=255), nullable=True),
        sa.Column("company_website", sa.Text(), nullable=True),
        sa.Column("role_title", sa.String(length=255), nullable=False),
        sa.Column("job_url", sa.Text(), nullable=False),
        sa.Column("canonical_job_url", sa.Text(), nullable=False),
        sa.Column("role_location", sa.String(length=255), nullable=False),
        sa.Column("source_type", sa.String(length=64), nullable=False),
        sa.Column("evidence_verified_on", sa.Date(), nullable=False),
        sa.Column("direct_job_listing", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("expansion_signal", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("technical_fit", sa.Float(), nullable=False, server_default="0"),
        sa.Column("hiring_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("contact_relevance", sa.Float(), nullable=False, server_default="0"),
        sa.Column("total_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("score_breakdown", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("qualification_reasons", postgresql.JSONB(), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("contact_name", sa.String(length=255), nullable=True),
        sa.Column("contact_role", sa.String(length=255), nullable=True),
        sa.Column("contact_profile_url", sa.Text(), nullable=True),
        sa.Column("contact_email", sa.String(length=320), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="discovered"),
        sa.Column("last_verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("canonical_job_url", name="uq_hiring_prospects_canonical_job_url"),
    )
    op.create_index("ix_hiring_prospects_company_domain", "hiring_prospects", ["company_domain"])
    op.create_index("ix_hiring_prospects_status_score", "hiring_prospects", ["status", "total_score"])


def downgrade() -> None:
    op.drop_index("ix_hiring_prospects_status_score", table_name="hiring_prospects")
    op.drop_index("ix_hiring_prospects_company_domain", table_name="hiring_prospects")
    op.drop_table("hiring_prospects")
    op.drop_table("hiring_runs")

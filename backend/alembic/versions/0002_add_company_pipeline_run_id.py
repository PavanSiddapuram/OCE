"""add pipeline_run_id to companies

Revision ID: 0002
Revises: 0001
Create Date: 2026-07-08
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "companies",
        sa.Column("pipeline_run_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_foreign_key(
        "fk_companies_pipeline_run_id",
        "companies",
        "pipeline_runs",
        ["pipeline_run_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index("ix_companies_pipeline_run_id", "companies", ["pipeline_run_id"])


def downgrade() -> None:
    op.drop_index("ix_companies_pipeline_run_id", table_name="companies")
    op.drop_constraint("fk_companies_pipeline_run_id", "companies", type_="foreignkey")
    op.drop_column("companies", "pipeline_run_id")

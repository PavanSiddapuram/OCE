"""add pressure_test to opportunities

Revision ID: 0003
Revises: 0002
Create Date: 2026-07-10
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "opportunities",
        sa.Column("pressure_test", postgresql.JSONB(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("opportunities", "pressure_test")

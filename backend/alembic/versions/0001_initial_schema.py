"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-06-20
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "companies",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("website", sa.String()),
        sa.Column("description", sa.Text()),
        sa.Column("mission", sa.Text()),
        sa.Column("product_summary", sa.Text()),
        sa.Column("recent_launches", postgresql.ARRAY(sa.Text())),
        sa.Column("tech_stack", postgresql.ARRAY(sa.Text())),
        sa.Column("current_focus", sa.Text()),
        sa.Column("sector", sa.String()),
        sa.Column("city", sa.String()),
        sa.Column("stage", sa.String()),
        sa.Column("source", sa.String()),
        sa.Column("source_url", sa.String()),
        sa.Column("founded_year", sa.Integer()),
        sa.Column("employee_count", sa.String()),
        sa.Column("crunchbase_url", sa.String()),
        sa.Column("linkedin_url", sa.String()),
        sa.Column("twitter_url", sa.String()),
        sa.Column("raw_scrape_data", postgresql.JSONB()),
        sa.Column("status", sa.String(), nullable=False, server_default="discovered"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "founders",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("company_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("companies.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("role", sa.String()),
        sa.Column("linkedin_url", sa.String()),
        sa.Column("twitter_url", sa.String()),
        sa.Column("personal_blog", sa.String()),
        sa.Column("background", sa.Text()),
        sa.Column("complaints", postgresql.ARRAY(sa.Text())),
        sa.Column("podcast_links", postgresql.ARRAY(sa.Text())),
        sa.Column("interview_links", postgresql.ARRAY(sa.Text())),
        sa.Column("raw_research", postgresql.JSONB()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "opportunities",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("company_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("companies.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("category", sa.String()),
        sa.Column("description", sa.Text()),
        sa.Column("impact", sa.Text()),
        sa.Column("fit_score", sa.Integer()),
        sa.Column("fit_reasoning", sa.Text()),
        sa.Column("pow_idea", sa.Text()),
        sa.Column("pow_repo_url", sa.String()),
        sa.Column("skills_required", postgresql.ARRAY(sa.Text())),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "research",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("company_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("companies.id", ondelete="CASCADE"), nullable=False),
        sa.Column("agent_name", sa.String(), nullable=False),
        sa.Column("raw_input", postgresql.JSONB()),
        sa.Column("raw_output", postgresql.JSONB()),
        sa.Column("tokens_used", sa.Integer()),
        sa.Column("model_used", sa.String()),
        sa.Column("duration_ms", sa.Integer()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "contacts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("company_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("companies.id"), nullable=False),
        sa.Column("founder_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("founders.id"), nullable=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("email", sa.String()),
        sa.Column("linkedin_url", sa.String()),
        sa.Column("role", sa.String()),
        sa.Column("contact_type", sa.String()),
        sa.Column("status", sa.String(), nullable=False, server_default="not_contacted"),
        sa.Column("notes", sa.Text()),
        sa.Column("last_contacted", sa.DateTime(timezone=True)),
        sa.Column("next_followup", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "outreach",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("company_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("companies.id"), nullable=False),
        sa.Column("opportunity_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("opportunities.id"), nullable=True),
        sa.Column("contact_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("contacts.id"), nullable=True),
        sa.Column("channel", sa.String()),
        sa.Column("subject", sa.String()),
        sa.Column("body", sa.Text()),
        sa.Column("hook", sa.Text()),
        sa.Column("why_company", sa.Text()),
        sa.Column("why_problem", sa.Text()),
        sa.Column("why_me", sa.Text()),
        sa.Column("what_i_built", sa.Text()),
        sa.Column("call_to_action", sa.Text()),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "pipeline_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("filters", postgresql.JSONB()),
        sa.Column("status", sa.String(), nullable=False, server_default="pending"),
        sa.Column("current_agent", sa.String()),
        sa.Column("agents_done", postgresql.ARRAY(sa.Text())),
        sa.Column("total_companies", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("error_message", sa.Text()),
        sa.Column("started_at", sa.DateTime(timezone=True)),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_index("ix_companies_website", "companies", ["website"])
    op.create_index("ix_companies_status", "companies", ["status"])
    op.create_index("ix_opportunities_company_id", "opportunities", ["company_id"])
    op.create_index("ix_opportunities_fit_score", "opportunities", ["fit_score"])
    op.create_index("ix_contacts_status", "contacts", ["status"])
    op.create_index("ix_research_company_agent", "research", ["company_id", "agent_name"])


def downgrade() -> None:
    op.drop_table("outreach")
    op.drop_table("contacts")
    op.drop_table("research")
    op.drop_table("opportunities")
    op.drop_table("founders")
    op.drop_table("pipeline_runs")
    op.drop_table("companies")

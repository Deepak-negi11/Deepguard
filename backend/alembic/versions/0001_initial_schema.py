"""Initial DeepGuard schema

Revision ID: 0001_initial_schema
Revises: None
Create Date: 2026-03-14 00:00:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("tier", sa.String(length=20), nullable=False, server_default="free"),
        sa.Column("monthly_usage", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_id", "users", ["id"], unique=False)

    op.create_table(
        "verification_requests",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("request_type", sa.String(length=20), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="pending"),
        sa.Column("url", sa.Text(), nullable=True),
        sa.Column("file_name", sa.String(length=255), nullable=True),
        sa.Column("payload_excerpt", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_verification_requests_user_id", "verification_requests", ["user_id"], unique=False)
    op.create_index("ix_verification_requests_status", "verification_requests", ["status"], unique=False)

    op.create_table(
        "verification_results",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("request_id", sa.String(length=36), sa.ForeignKey("verification_requests.id", ondelete="CASCADE"), nullable=False),
        sa.Column("authenticity_score", sa.Float(), nullable=False),
        sa.Column("verdict", sa.String(length=32), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("evidence", sa.JSON(), nullable=False),
        sa.Column("breakdown", sa.JSON(), nullable=False),
        sa.Column("processing_time_seconds", sa.Float(), nullable=False),
        sa.Column("model_version", sa.String(length=32), nullable=False, server_default="prototype-v1"),
        sa.Column("completed_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("request_id"),
    )

    op.create_table(
        "evidence_items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("result_id", sa.Integer(), sa.ForeignKey("verification_results.id", ondelete="CASCADE"), nullable=False),
        sa.Column("category", sa.String(length=50), nullable=False),
        sa.Column("severity", sa.String(length=20), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("details", sa.JSON(), nullable=False),
        sa.Column("timestamp_in_media", sa.Float(), nullable=True),
        sa.Column("visualization_hint", sa.String(length=120), nullable=True),
    )
    op.create_index("ix_evidence_items_result_id", "evidence_items", ["result_id"], unique=False)

    op.create_table(
        "stored_analysis_payloads",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("request_id", sa.String(length=36), sa.ForeignKey("verification_requests.id", ondelete="CASCADE"), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("request_id"),
    )
    op.create_index("ix_stored_analysis_payloads_request_id", "stored_analysis_payloads", ["request_id"], unique=True)

    op.create_table(
        "api_usage",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("endpoint", sa.String(length=120), nullable=False),
        sa.Column("request_time", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("response_time_ms", sa.Float(), nullable=True),
        sa.Column("status_code", sa.Integer(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
    )
    op.create_index("ix_api_usage_user_id", "api_usage", ["user_id"], unique=False)
    op.create_index("ix_api_usage_request_time", "api_usage", ["request_time"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_api_usage_request_time", table_name="api_usage")
    op.drop_index("ix_api_usage_user_id", table_name="api_usage")
    op.drop_table("api_usage")

    op.drop_index("ix_stored_analysis_payloads_request_id", table_name="stored_analysis_payloads")
    op.drop_table("stored_analysis_payloads")

    op.drop_index("ix_evidence_items_result_id", table_name="evidence_items")
    op.drop_table("evidence_items")

    op.drop_table("verification_results")

    op.drop_index("ix_verification_requests_status", table_name="verification_requests")
    op.drop_index("ix_verification_requests_user_id", table_name="verification_requests")
    op.drop_table("verification_requests")

    op.drop_index("ix_users_id", table_name="users")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")

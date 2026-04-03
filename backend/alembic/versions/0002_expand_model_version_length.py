"""Expand model_version length for stored analysis results.

Revision ID: 0002_expand_model_version_length
Revises: 0001_initial_schema
Create Date: 2026-03-23 16:30:00
"""

from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision = "0002_expand_model_version_length"
down_revision = "0001_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "verification_results",
        "model_version",
        existing_type=sa.String(length=32),
        type_=sa.String(length=128),
        existing_nullable=False,
        existing_server_default="prototype-v1",
    )


def downgrade() -> None:
    op.alter_column(
        "verification_results",
        "model_version",
        existing_type=sa.String(length=128),
        type_=sa.String(length=32),
        existing_nullable=False,
        existing_server_default="prototype-v1",
    )

"""add team_era table

Revision ID: 002_add_team_era
Revises: 3303734b29d2
Create Date: 2025-11-26 17:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "002_add_team_era"
down_revision: Union[str, None] = "3303734b29d2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create team_era table
    op.create_table(
        "team_era",
        sa.Column("era_id", sa.UUID(), nullable=False),
        sa.Column("node_id", sa.UUID(), nullable=False),
        sa.Column("season_year", sa.Integer(), nullable=False),
        sa.Column("registered_name", sa.String(length=255), nullable=False),
        sa.Column("uci_code", sa.String(length=3), nullable=True),
        sa.Column("tier_level", sa.Integer(), nullable=True),
        sa.Column("source_origin", sa.String(length=100), nullable=True),
        sa.Column("is_manual_override", sa.Boolean(), nullable=False, server_default=sa.text("FALSE")),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["node_id"], ["team_node.node_id"], ondelete="CASCADE"),
        sa.UniqueConstraint("node_id", "season_year", name="uq_node_year"),
        sa.CheckConstraint(
            "season_year >= 1900 AND season_year <= 2100", name="check_season_year_range"
        ),
        sa.CheckConstraint("tier_level IN (1, 2, 3)", name="check_tier_level_values"),
        sa.PrimaryKeyConstraint("era_id"),
    )

    # Indexes to support common queries
    op.create_index("idx_team_era_node", "team_era", ["node_id"])
    op.create_index("idx_team_era_year", "team_era", ["season_year"])
    op.create_index("idx_team_era_manual", "team_era", ["is_manual_override"])


def downgrade() -> None:
    # Drop indexes first
    op.drop_index("idx_team_era_manual", table_name="team_era")
    op.drop_index("idx_team_era_year", table_name="team_era")
    op.drop_index("idx_team_era_node", table_name="team_era")
    # Drop table
    op.drop_table("team_era")

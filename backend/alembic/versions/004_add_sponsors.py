"""Add sponsor tables

Revision ID: 004_add_sponsors
Revises: 003_add_lineage_event
Create Date: 2025-11-26 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '004_add_sponsors'
down_revision = '003_add_lineage_event'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create sponsor_master table
    op.create_table(
        'sponsor_master',
        sa.Column('master_id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('legal_name', sa.String(length=255), nullable=False),
        sa.Column('industry_sector', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('NOW()'), nullable=False),
        sa.PrimaryKeyConstraint('master_id'),
        sa.UniqueConstraint('legal_name')
    )

    # Create sponsor_brand table
    op.create_table(
        'sponsor_brand',
        sa.Column('brand_id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('master_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('brand_name', sa.String(length=255), nullable=False),
        sa.Column('default_hex_color', sa.String(length=7), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('NOW()'), nullable=False),
        sa.CheckConstraint("default_hex_color ~ '^#[0-9A-Fa-f]{6}$'", name='check_hex_color_format'),
        sa.ForeignKeyConstraint(['master_id'], ['sponsor_master.master_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('brand_id'),
        sa.UniqueConstraint('master_id', 'brand_name', name='uq_master_brand')
    )
    op.create_index('idx_sponsor_brand_master', 'sponsor_brand', ['master_id'])

    # Create team_sponsor_link table
    op.create_table(
        'team_sponsor_link',
        sa.Column('link_id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('era_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('brand_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('rank_order', sa.Integer(), nullable=False),
        sa.Column('prominence_percent', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('NOW()'), nullable=False),
        sa.CheckConstraint('rank_order >= 1', name='check_rank_order_positive'),
        sa.CheckConstraint('prominence_percent > 0 AND prominence_percent <= 100', name='check_prominence_range'),
        sa.ForeignKeyConstraint(['era_id'], ['team_era.era_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['brand_id'], ['sponsor_brand.brand_id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('link_id'),
        sa.UniqueConstraint('era_id', 'brand_id', name='uq_era_brand'),
        sa.UniqueConstraint('era_id', 'rank_order', name='uq_era_rank')
    )
    op.create_index('idx_team_sponsor_era', 'team_sponsor_link', ['era_id'])
    op.create_index('idx_team_sponsor_brand', 'team_sponsor_link', ['brand_id'])


def downgrade() -> None:
    op.drop_index('idx_team_sponsor_brand', table_name='team_sponsor_link')
    op.drop_index('idx_team_sponsor_era', table_name='team_sponsor_link')
    op.drop_table('team_sponsor_link')
    op.drop_index('idx_sponsor_brand_master', table_name='sponsor_brand')
    op.drop_table('sponsor_brand')
    op.drop_table('sponsor_master')

"""
Alembic migration for lineage_event table and event_type_enum
"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as pg

# revision identifiers, used by Alembic.
revision = '003_add_lineage_event'
down_revision = '002_add_team_era'
branch_labels = None
depends_on = None

def upgrade():
    # Ensure pgcrypto is available for gen_random_uuid()
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto;")
    # Ensure ENUM type exists (guarded for Postgres CI re-runs)
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'event_type_enum') THEN
                CREATE TYPE event_type_enum AS ENUM ('LEGAL_TRANSFER', 'SPIRITUAL_SUCCESSION', 'MERGE', 'SPLIT');
            END IF;
        END$$;
        """
    )

    # Create lineage_event table
    op.create_table(
        'lineage_event',
        sa.Column('event_id', pg.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('previous_node_id', pg.UUID(as_uuid=True), sa.ForeignKey('team_node.node_id', ondelete='SET NULL'), nullable=True),
        sa.Column('next_node_id', pg.UUID(as_uuid=True), sa.ForeignKey('team_node.node_id', ondelete='SET NULL'), nullable=True),
        sa.Column('event_year', sa.Integer(), nullable=False),
        sa.Column('event_type', pg.ENUM(name='event_type_enum', create_type=False), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('NOW()')),
        sa.CheckConstraint('(previous_node_id IS NOT NULL OR next_node_id IS NOT NULL)', name='ck_lineage_event_node_not_null'),
        sa.CheckConstraint('event_year >= 1900', name='ck_lineage_event_year_min'),
    )
    op.create_index('idx_lineage_event_prev', 'lineage_event', ['previous_node_id'])
    op.create_index('idx_lineage_event_next', 'lineage_event', ['next_node_id'])
    op.create_index('idx_lineage_event_year', 'lineage_event', ['event_year'])
    op.create_index('idx_lineage_event_type', 'lineage_event', ['event_type'])

def downgrade():
    op.drop_index('idx_lineage_event_type', table_name='lineage_event')
    op.drop_index('idx_lineage_event_year', table_name='lineage_event')
    op.drop_index('idx_lineage_event_next', table_name='lineage_event')
    op.drop_index('idx_lineage_event_prev', table_name='lineage_event')
    op.drop_table('lineage_event')
    # Drop enum type only if it exists
    pg.ENUM(name='event_type_enum').drop(op.get_bind(), checkfirst=True)

"""add edits and moderation tables

Revision ID: 006_add_edits
Revises: 005_add_users
Create Date: 2025-12-05
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

# revision identifiers, used by Alembic.
revision = '006_add_edits'
down_revision = '005_add_users'
branch_labels = None
depends_on = None


def upgrade():
    # Safely create enums only if they do not already exist
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'edit_status_enum') THEN
                CREATE TYPE edit_status_enum AS ENUM ('PENDING', 'APPROVED', 'REJECTED');
            END IF;
        END$$;
        """
    )

    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'edit_type_enum') THEN
                CREATE TYPE edit_type_enum AS ENUM ('METADATA', 'MERGE', 'SPLIT', 'DISSOLVE');
            END IF;
        END$$;
        """
    )
    
    # Edits table
    op.create_table(
        'edits',
        sa.Column('edit_id', UUID, primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', UUID, sa.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False),
        sa.Column('edit_type', sa.Enum('METADATA', 'MERGE', 'SPLIT', 'DISSOLVE', name='edit_type_enum'), nullable=False),
        sa.Column('target_era_id', UUID, sa.ForeignKey('team_era.era_id', ondelete='CASCADE'), nullable=True),
        sa.Column('target_node_id', UUID, sa.ForeignKey('team_node.node_id', ondelete='CASCADE'), nullable=True),
        sa.Column('changes', JSONB, nullable=False),  # Store the changes
        sa.Column('reason', sa.Text, nullable=False),
        sa.Column('status', sa.Enum('PENDING', 'APPROVED', 'REJECTED', name='edit_status_enum'), default='PENDING'),
        sa.Column('reviewed_by', UUID, sa.ForeignKey('users.user_id', ondelete='SET NULL'), nullable=True),
        sa.Column('reviewed_at', sa.TIMESTAMP, nullable=True),
        sa.Column('review_notes', sa.Text, nullable=True),
        sa.Column('created_at', sa.TIMESTAMP, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP, server_default=sa.text('NOW()'))
    )
    
    op.create_index('idx_edits_user', 'edits', ['user_id'])
    op.create_index('idx_edits_status', 'edits', ['status'])
    op.create_index('idx_edits_type', 'edits', ['edit_type'])


def downgrade():
    op.drop_index('idx_edits_type', 'edits')
    op.drop_index('idx_edits_status', 'edits')
    op.drop_index('idx_edits_user', 'edits')
    op.drop_table('edits')
    op.execute("DROP TYPE IF EXISTS edit_status_enum")
    op.execute("DROP TYPE IF EXISTS edit_type_enum")

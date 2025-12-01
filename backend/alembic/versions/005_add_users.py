"""add users and auth tables

Revision ID: 005_add_users
Revises: 004_add_sponsors
Create Date: 2025-12-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision = '005_add_users'
down_revision = '004_add_sponsors'
branch_labels = None
depends_on = None


def upgrade():
    # Create enum type idempotently using DO block
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE user_role_enum AS ENUM ('GUEST', 'NEW_USER', 'TRUSTED_USER', 'ADMIN');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)

    # Users table
    op.create_table(
        'users',
        sa.Column('user_id', UUID, primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('google_id', sa.String(255), unique=True, nullable=False),
        sa.Column('email', sa.String(255), unique=True, nullable=False),
        sa.Column('display_name', sa.String(255)),
        sa.Column('avatar_url', sa.String(500)),
        sa.Column('role', sa.Enum('GUEST', 'NEW_USER', 'TRUSTED_USER', 'ADMIN', name='user_role_enum', create_type=False), server_default='NEW_USER'),
        sa.Column('approved_edits_count', sa.Integer, default=0),
        sa.Column('is_banned', sa.Boolean, default=False),
        sa.Column('banned_reason', sa.Text, nullable=True),
        sa.Column('created_at', sa.TIMESTAMP, server_default=sa.text('NOW()')),
        sa.Column('last_login_at', sa.TIMESTAMP, nullable=True),
        sa.Column('updated_at', sa.TIMESTAMP, server_default=sa.text('NOW()'))
    )
    
    # Refresh tokens table
    op.create_table(
        'refresh_tokens',
        sa.Column('token_id', UUID, primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', UUID, sa.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False),
        sa.Column('token_hash', sa.String(255), unique=True, nullable=False),
        sa.Column('expires_at', sa.TIMESTAMP, nullable=False),
        sa.Column('created_at', sa.TIMESTAMP, server_default=sa.text('NOW()'))
    )
    
    op.create_index('idx_users_google_id', 'users', ['google_id'])
    op.create_index('idx_users_email', 'users', ['email'])
    op.create_index('idx_refresh_tokens_user', 'refresh_tokens', ['user_id'])
    op.create_index('idx_refresh_tokens_hash', 'refresh_tokens', ['token_hash'])


def downgrade():
    op.drop_table('refresh_tokens')
    op.drop_table('users')
    # Drop enum type if no longer used
    op.execute('DROP TYPE IF EXISTS user_role_enum')

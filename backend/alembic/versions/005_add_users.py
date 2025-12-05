"""add users and auth tables

Revision ID: 005_add_users
Revises: 004_add_sponsors
Create Date: 2025-12-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

# revision identifiers, used by Alembic.
revision = '005_add_users'
down_revision = '004_add_sponsors'
branch_labels = None
depends_on = None


def upgrade():
    from sqlalchemy import inspect
    
    dialect = op.get_context().dialect
    conn = op.get_bind()
    inspector = inspect(conn)
    existing_tables = inspector.get_table_names()
    
    if dialect.name == 'postgresql':
        id_type = PG_UUID(as_uuid=True)
        server_default_arg = sa.text('gen_random_uuid()')
        created_at_default = sa.text('NOW()')
    else:
        # SQLite: use CHAR(36) for UUID
        id_type = sa.CHAR(36)
        server_default_arg = None
        created_at_default = None

    # Users table (role stored as VARCHAR with CHECK constraint for portability)
    # For SQLite, we include the check constraint in the table definition
    if 'users' not in existing_tables:
        op.create_table(
            'users',
            sa.Column('user_id', id_type, primary_key=True, server_default=server_default_arg),
            sa.Column('google_id', sa.String(255), unique=True, nullable=False),
            sa.Column('email', sa.String(255), unique=True, nullable=False),
            sa.Column('display_name', sa.String(255)),
            sa.Column('avatar_url', sa.String(500)),
            sa.Column('role', sa.String(20), server_default='NEW_USER', nullable=False),
            sa.Column('approved_edits_count', sa.Integer, default=0),
            sa.Column('is_banned', sa.Boolean, default=False),
            sa.Column('banned_reason', sa.Text, nullable=True),
            sa.Column('created_at', sa.TIMESTAMP, server_default=created_at_default),
            sa.Column('last_login_at', sa.TIMESTAMP, nullable=True),
            sa.Column('updated_at', sa.TIMESTAMP, server_default=created_at_default),
            sa.CheckConstraint("role IN ('GUEST','NEW_USER','TRUSTED_USER','ADMIN')", name='ck_users_role')
        )

    # Refresh tokens table
    if 'refresh_tokens' not in existing_tables:
        op.create_table(
            'refresh_tokens',
            sa.Column('token_id', id_type, primary_key=True, server_default=server_default_arg),
            sa.Column('user_id', id_type, sa.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False),
            sa.Column('token_hash', sa.String(255), unique=True, nullable=False),
            sa.Column('expires_at', sa.TIMESTAMP, nullable=False),
            sa.Column('created_at', sa.TIMESTAMP, server_default=created_at_default)
        )

    # Create indexes only if they don't exist
    existing_indexes = set()
    for table in ['users', 'refresh_tokens']:
        if table in existing_tables:
            existing_indexes.update([idx['name'] for idx in inspector.get_indexes(table)])
    
    if 'idx_users_google_id' not in existing_indexes:
        op.create_index('idx_users_google_id', 'users', ['google_id'])
    if 'idx_users_email' not in existing_indexes:
        op.create_index('idx_users_email', 'users', ['email'])
    if 'idx_refresh_tokens_user' not in existing_indexes:
        op.create_index('idx_refresh_tokens_user', 'refresh_tokens', ['user_id'])
    if 'idx_refresh_tokens_hash' not in existing_indexes:
        op.create_index('idx_refresh_tokens_hash', 'refresh_tokens', ['token_hash'])


def downgrade():
    op.drop_table('refresh_tokens')
    op.drop_table('users')

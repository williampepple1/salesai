"""Add Clerk authentication

Revision ID: 001_add_clerk_auth
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001_add_clerk_auth'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add clerk_user_id column
    op.add_column('users', sa.Column('clerk_user_id', sa.String(), nullable=True))
    op.create_unique_constraint('uq_users_clerk_user_id', 'users', ['clerk_user_id'])
    op.create_index('ix_users_clerk_user_id', 'users', ['clerk_user_id'])
    
    # Make hashed_password nullable (not needed with Clerk)
    op.alter_column('users', 'hashed_password', nullable=True)
    
    # Make full_name nullable
    op.alter_column('users', 'full_name', nullable=True)


def downgrade() -> None:
    # Remove clerk_user_id column and constraints
    op.drop_index('ix_users_clerk_user_id', 'users')
    op.drop_constraint('uq_users_clerk_user_id', 'users', type_='unique')
    op.drop_column('users', 'clerk_user_id')
    
    # Make hashed_password required again
    op.alter_column('users', 'hashed_password', nullable=False)

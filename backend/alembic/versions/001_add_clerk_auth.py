"""Initial production schema

Revision ID: 001_initial_schema
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('clerk_user_id', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('username', sa.String(), nullable=False),
        sa.Column('full_name', sa.String(), nullable=True),
        sa.Column('business_name', sa.String(), nullable=True),
        sa.Column('bank_name', sa.String(), nullable=True),
        sa.Column('account_name', sa.String(), nullable=True),
        sa.Column('account_number', sa.String(), nullable=True),
        sa.Column('telegram_bot_token', sa.String(), nullable=True),
        sa.Column('telegram_bot_username', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_clerk_user_id'), 'users', ['clerk_user_id'], unique=True)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    op.create_unique_constraint('uq_users_telegram_bot_token', 'users', ['telegram_bot_token'])

    op.create_table(
        'products',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('price', sa.Float(), nullable=False),
        sa.Column('currency', sa.String(), nullable=True),
        sa.Column('image_urls', sa.JSON(), nullable=True),
        sa.Column('stock_quantity', sa.Integer(), nullable=True),
        sa.Column('is_available', sa.Boolean(), nullable=True),
        sa.Column('category', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_products_id'), 'products', ['id'], unique=False)

    op.create_table(
        'conversations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('telegram_chat_id', sa.String(), nullable=False),
        sa.Column('customer_name', sa.String(), nullable=True),
        sa.Column('customer_phone', sa.String(), nullable=True),
        sa.Column('messages', sa.JSON(), nullable=True),
        sa.Column('context', sa.JSON(), nullable=True),
        sa.Column('status', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_conversations_id'), 'conversations', ['id'], unique=False)
    op.create_index(op.f('ix_conversations_telegram_chat_id'), 'conversations', ['telegram_chat_id'], unique=False)

    op.create_table(
        'discount_rules',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('rule_name', sa.String(), nullable=False),
        sa.Column('discount_type', sa.String(), nullable=False),
        sa.Column('quantity_threshold', sa.Integer(), nullable=False),
        sa.Column('discount_value', sa.Float(), nullable=False),
        sa.Column('free_quantity', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['product_id'], ['products.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_discount_rules_id'), 'discount_rules', ['id'], unique=False)

    op.create_table(
        'orders',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('conversation_id', sa.Integer(), nullable=True),
        sa.Column('customer_name', sa.String(), nullable=False),
        sa.Column('customer_phone', sa.String(), nullable=True),
        sa.Column('customer_address', sa.Text(), nullable=True),
        sa.Column('items', sa.JSON(), nullable=False),
        sa.Column('subtotal', sa.Float(), nullable=False),
        sa.Column('discount_amount', sa.Float(), nullable=True),
        sa.Column('total_amount', sa.Float(), nullable=False),
        sa.Column('currency', sa.String(), nullable=True),
        sa.Column('status', sa.String(), nullable=True),
        sa.Column('invoice_url', sa.String(), nullable=True),
        sa.Column('receipt_url', sa.String(), nullable=True),
        sa.Column('payment_status', sa.String(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id']),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_orders_id'), 'orders', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_orders_id'), table_name='orders')
    op.drop_table('orders')
    op.drop_index(op.f('ix_discount_rules_id'), table_name='discount_rules')
    op.drop_table('discount_rules')
    op.drop_index(op.f('ix_conversations_telegram_chat_id'), table_name='conversations')
    op.drop_index(op.f('ix_conversations_id'), table_name='conversations')
    op.drop_table('conversations')
    op.drop_index(op.f('ix_products_id'), table_name='products')
    op.drop_table('products')
    op.drop_constraint('uq_users_telegram_bot_token', 'users', type_='unique')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_index(op.f('ix_users_clerk_user_id'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_table('users')

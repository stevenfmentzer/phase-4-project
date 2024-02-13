"""Initial Migration

Revision ID: 2519ab6ddb3a
Revises: 
Create Date: 2024-02-12 20:44:50.073433

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2519ab6ddb3a'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('first_name', sa.String(), nullable=True),
    sa.Column('last_name', sa.String(), nullable=True),
    sa.Column('username', sa.String(), nullable=False),
    sa.Column('_password_hash', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_users')),
    sa.UniqueConstraint('username', name=op.f('uq_users_username'))
    )
    op.create_table('bank_accounts',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('balance', sa.Float(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_bank_accounts_user_id_users')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_bank_accounts'))
    )
    op.create_table('bills',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('lender_name', sa.String(), nullable=True),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('pay_date', sa.Date(), nullable=True),
    sa.Column('bill_type', sa.String(), nullable=True),
    sa.Column('balance_init', sa.Float(), nullable=True),
    sa.Column('balance_remain', sa.Float(), nullable=True),
    sa.Column('min_pay_value', sa.Float(), nullable=True),
    sa.Column('apr_rate', sa.Float(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_bills_user_id_users')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_bills'))
    )
    op.create_table('incomes',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('bank_account_id', sa.Integer(), nullable=True),
    sa.Column('pay_value', sa.Float(), nullable=True),
    sa.Column('pay_freq', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['bank_account_id'], ['bank_accounts.id'], name=op.f('fk_incomes_bank_account_id_bank_accounts')),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_incomes_user_id_users')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_incomes'))
    )
    op.create_table('payments',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('bank_account_id', sa.Integer(), nullable=True),
    sa.Column('bill_id', sa.Integer(), nullable=True),
    sa.Column('pay_date', sa.Date(), nullable=True),
    sa.Column('pay_value', sa.Float(), nullable=True),
    sa.ForeignKeyConstraint(['bank_account_id'], ['bank_accounts.id'], name=op.f('fk_payments_bank_account_id_bank_accounts')),
    sa.ForeignKeyConstraint(['bill_id'], ['bills.id'], name=op.f('fk_payments_bill_id_bills')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_payments'))
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('payments')
    op.drop_table('incomes')
    op.drop_table('bills')
    op.drop_table('bank_accounts')
    op.drop_table('users')
    # ### end Alembic commands ###

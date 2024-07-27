"""empty message

Revision ID: b28ac0a2d084
Revises: 20260ee05fa8
Create Date: 2024-07-27 16:28:36.291840

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b28ac0a2d084'
down_revision = '20260ee05fa8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('account_classification',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('account_classification_name', sa.String(length=255), nullable=True),
    sa.Column('active', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('admin_account_classification',
    sa.Column('account_classification_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['account_classification_id'], ['account_classification.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('account_classification_id', 'user_id')
    )
    op.create_table('user_account_classification',
    sa.Column('account_classification_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['account_classification_id'], ['account_classification.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('account_classification_id', 'user_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user_account_classification')
    op.drop_table('admin_account_classification')
    op.drop_table('account_classification')
    # ### end Alembic commands ###
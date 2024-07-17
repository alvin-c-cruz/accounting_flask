"""empty message

Revision ID: 6696f51f8358
Revises: b3403ba393cb
Create Date: 2024-07-14 12:05:50.153639

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6696f51f8358'
down_revision = 'b3403ba393cb'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('wtax',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('wtax_name', sa.String(length=255), nullable=True),
    sa.Column('atc', sa.String(length=255), nullable=True),
    sa.Column('tax_rate', sa.Float(), nullable=True),
    sa.Column('wtax_type_id', sa.Integer(), nullable=False),
    sa.Column('active', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['wtax_type_id'], ['wtax_type.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('admin_wtax',
    sa.Column('wtax_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['wtax_id'], ['wtax.id'], ),
    sa.PrimaryKeyConstraint('wtax_id', 'user_id')
    )
    op.create_table('user_wtax',
    sa.Column('wtax_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['wtax_id'], ['wtax.id'], ),
    sa.PrimaryKeyConstraint('wtax_id', 'user_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user_wtax')
    op.drop_table('admin_wtax')
    op.drop_table('wtax')
    # ### end Alembic commands ###
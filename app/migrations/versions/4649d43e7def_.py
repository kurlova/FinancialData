"""empty message

Revision ID: 4649d43e7def
Revises: 
Create Date: 2018-05-14 10:45:34.466587

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4649d43e7def'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('history',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('date', sa.DateTime(), nullable=True),
    sa.Column('open', sa.Float(precision=2), nullable=True),
    sa.Column('high', sa.Float(precision=2), nullable=True),
    sa.Column('low', sa.Float(precision=2), nullable=True),
    sa.Column('close', sa.Float(precision=2), nullable=True),
    sa.Column('volume', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('history')
    # ### end Alembic commands ###
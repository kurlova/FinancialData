"""split insider and insider trades

Revision ID: 31c40d9957b2
Revises: 5515ef02093e
Create Date: 2018-05-18 12:04:46.956782

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '31c40d9957b2'
down_revision = '5515ef02093e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('insider_trades_ticker_id_fkey', 'insider_trades', type_='foreignkey')
    op.drop_column('insider_trades', 'ticker_id')
    op.add_column('insiders', sa.Column('ticker_id', sa.Integer(), nullable=False))
    op.create_foreign_key(None, 'insiders', 'tickers', ['ticker_id'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'insiders', type_='foreignkey')
    op.drop_column('insiders', 'ticker_id')
    op.add_column('insider_trades', sa.Column('ticker_id', sa.INTEGER(), autoincrement=False, nullable=False))
    op.create_foreign_key('insider_trades_ticker_id_fkey', 'insider_trades', 'tickers', ['ticker_id'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###
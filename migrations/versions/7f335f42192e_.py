"""empty message

Revision ID: 7f335f42192e
Revises: c509c0eca353
Create Date: 2017-06-20 16:43:04.387028

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7f335f42192e'
down_revision = 'c509c0eca353'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('order_pays', sa.Column('pay_price', sa.Numeric(precision=10, scale=2), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('order_pays', 'pay_price')
    # ### end Alembic commands ###
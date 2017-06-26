"""empty message

Revision ID: 684d336f9d79
Revises: 489ec8e075bd
Create Date: 2017-06-21 09:55:32.619503

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '684d336f9d79'
down_revision = '489ec8e075bd'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('driver_posts',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=100), nullable=True),
    sa.Column('start_address', sa.String(length=255), nullable=True),
    sa.Column('end_address', sa.String(length=255), nullable=True),
    sa.Column('note', sa.Text(), nullable=True),
    sa.Column('start_car_time', sa.DateTime(), nullable=True),
    sa.Column('create_time', sa.DateTime(), nullable=True),
    sa.Column('driver_id', sa.Integer(), nullable=True),
    sa.Column('start_price', sa.Numeric(precision=10, scale=2), nullable=True),
    sa.Column('end_price', sa.Numeric(precision=10, scale=2), nullable=True),
    sa.Column('consignor_user_id', sa.Integer(), nullable=True),
    sa.Column('receive_time', sa.DateTime(), nullable=True),
    sa.Column('state', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['consignor_user_id'], ['consignors.id'], ),
    sa.ForeignKeyConstraint(['driver_id'], ['drivers.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column(u'order_pays', sa.Column('driver_post_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'order_pays', 'driver_posts', ['driver_post_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'order_pays', type_='foreignkey')
    op.drop_column(u'order_pays', 'driver_post_id')
    op.drop_table('driver_posts')
    # ### end Alembic commands ###
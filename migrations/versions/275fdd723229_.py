"""empty message

Revision ID: 275fdd723229
Revises: 6a2ec451473d
Create Date: 2017-06-14 11:52:59.386988

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '275fdd723229'
down_revision = '6a2ec451473d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('drivers', sa.Column('user_id', sa.Integer(), nullable=True))
    op.drop_constraint(u'drivers_ibfk_1', 'drivers', type_='foreignkey')
    op.create_foreign_key(None, 'drivers', 'users', ['user_id'], ['id'])
    op.drop_column('drivers', 'master')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('drivers', sa.Column('master', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'drivers', type_='foreignkey')
    op.create_foreign_key(u'drivers_ibfk_1', 'drivers', 'users', ['master'], ['id'])
    op.drop_column('drivers', 'user_id')
    # ### end Alembic commands ###
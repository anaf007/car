"""empty message

Revision ID: 0bd8cee5da01
Revises: d5f6893a8e55
Create Date: 2017-09-25 13:30:56.597407

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '0bd8cee5da01'
down_revision = 'd5f6893a8e55'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('couponsion',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('price', sa.Numeric(precision=10, scale=2), nullable=True),
    sa.Column('maxprice', sa.Integer(), nullable=True),
    sa.Column('state', sa.Integer(), nullable=True),
    sa.Column('create_time', sa.DateTime(), nullable=True),
    sa.Column('expiration_time', sa.DateTime(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('tixianchengqings',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('note', sa.String(length=200), nullable=True),
    sa.Column('price', sa.Numeric(precision=10, scale=2), nullable=True),
    sa.Column('create_time', sa.DateTime(), nullable=True),
    sa.Column('finish_time', sa.DateTime(), nullable=True),
    sa.Column('state', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('consignor_images',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.Column('url', sa.String(length=100), nullable=True),
    sa.Column('consignor_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['consignor_id'], ['consignors.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('driver_self_orders',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('driver_id', sa.Integer(), nullable=True),
    sa.Column('goods_id', sa.Integer(), nullable=True),
    sa.Column('create_time', sa.DateTime(), nullable=True),
    sa.Column('state', sa.Integer(), nullable=True),
    sa.Column('price', sa.Numeric(precision=10, scale=2), nullable=True),
    sa.ForeignKeyConstraint(['driver_id'], ['drivers.id'], ),
    sa.ForeignKeyConstraint(['goods_id'], ['goods.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('Driver_self_orders')
    op.drop_table('category_top')
    op.drop_table('comments')
    op.drop_table('order_tasks')
    op.drop_table('redis_tasks')
    op.drop_table('category_attribute')
    op.drop_table('goods_comments')
    op.drop_table('categorys')
    op.drop_table('articles')
    op.add_column('consignors', sa.Column('fuzheren', sa.String(length=64), nullable=True))
    op.add_column('consignors', sa.Column('shenfenzheng', sa.String(length=64), nullable=True))
    op.add_column('driver_posts', sa.Column('consignor_id', sa.Integer(), nullable=True))
    op.drop_constraint(u'driver_posts_ibfk_3', 'driver_posts', type_='foreignkey')
    op.create_foreign_key(None, 'driver_posts', 'goods', ['consignor_id'], ['id'])
    op.drop_column('driver_posts', 'consignor_user_id')
    op.add_column('goods', sa.Column('online_pirce', sa.Integer(), nullable=True))
    op.add_column('goods', sa.Column('price_is_pay', sa.Integer(), nullable=True))
    op.add_column('goods_self_orders', sa.Column('consignors_id', sa.Integer(), nullable=True))
    op.add_column('goods_self_orders', sa.Column('driver_post_id', sa.Integer(), nullable=True))
    op.drop_constraint(u'goods_self_orders_ibfk_1', 'goods_self_orders', type_='foreignkey')
    op.drop_constraint(u'goods_self_orders_ibfk_2', 'goods_self_orders', type_='foreignkey')
    op.create_foreign_key(None, 'goods_self_orders', 'driver_posts', ['driver_post_id'], ['id'])
    op.create_foreign_key(None, 'goods_self_orders', 'consignors', ['consignors_id'], ['id'])
    op.drop_column('goods_self_orders', 'driver_post')
    op.drop_column('goods_self_orders', 'consignors')
    op.add_column('order_pays', sa.Column('note', sa.String(length=50), nullable=True))
    op.add_column('positions', sa.Column('user_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'positions', 'users', ['user_id'], ['id'])
    op.drop_column('positions', 'users')
    op.add_column('user_infos', sa.Column('cif_time', sa.DateTime(), nullable=True))
    op.add_column('user_infos', sa.Column('confirm_time', sa.DateTime(), nullable=True))
    op.add_column('user_infos', sa.Column('kahao', sa.String(length=64), nullable=True))
    op.add_column('user_infos', sa.Column('kaihuhang', sa.String(length=200), nullable=True))
    op.add_column('user_infos', sa.Column('source', sa.Integer(), nullable=True))
    op.add_column('user_infos', sa.Column('suoshuyinhang', sa.String(length=64), nullable=True))
    op.add_column('user_infos', sa.Column('user_id', sa.Integer(), nullable=True))
    op.drop_constraint(u'user_infos_ibfk_1', 'user_infos', type_='foreignkey')
    op.create_foreign_key(None, 'user_infos', 'users', ['user_id'], ['id'])
    op.drop_column('user_infos', 'users')
    op.add_column('user_msgs', sa.Column('user_id', sa.Integer(), nullable=True))
    op.drop_constraint(u'user_msgs_ibfk_1', 'user_msgs', type_='foreignkey')
    op.create_foreign_key(None, 'user_msgs', 'users', ['user_id'], ['id'])
    op.drop_column('user_msgs', 'users')
    op.add_column('users', sa.Column('lock_price', sa.Numeric(precision=10, scale=2), nullable=True))
    op.add_column('users', sa.Column('pay_pwd_hash', sa.String(length=128), nullable=True))
    op.drop_column('users', 'about_me')
    op.drop_column('users', 'name')
    op.drop_column('users', 'location')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('location', mysql.VARCHAR(length=64), nullable=True))
    op.add_column('users', sa.Column('name', mysql.VARCHAR(length=64), nullable=True))
    op.add_column('users', sa.Column('about_me', mysql.TEXT(), nullable=True))
    op.drop_column('users', 'pay_pwd_hash')
    op.drop_column('users', 'lock_price')
    op.add_column('user_msgs', sa.Column('users', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'user_msgs', type_='foreignkey')
    op.create_foreign_key(u'user_msgs_ibfk_1', 'user_msgs', 'users', ['users'], ['id'])
    op.drop_column('user_msgs', 'user_id')
    op.add_column('user_infos', sa.Column('users', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'user_infos', type_='foreignkey')
    op.create_foreign_key(u'user_infos_ibfk_1', 'user_infos', 'users', ['users'], ['id'])
    op.drop_column('user_infos', 'user_id')
    op.drop_column('user_infos', 'suoshuyinhang')
    op.drop_column('user_infos', 'source')
    op.drop_column('user_infos', 'kaihuhang')
    op.drop_column('user_infos', 'kahao')
    op.drop_column('user_infos', 'confirm_time')
    op.drop_column('user_infos', 'cif_time')
    op.add_column('positions', sa.Column('users', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'positions', type_='foreignkey')
    op.drop_column('positions', 'user_id')
    op.drop_column('order_pays', 'note')
    op.add_column('goods_self_orders', sa.Column('consignors', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True))
    op.add_column('goods_self_orders', sa.Column('driver_post', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'goods_self_orders', type_='foreignkey')
    op.drop_constraint(None, 'goods_self_orders', type_='foreignkey')
    op.create_foreign_key(u'goods_self_orders_ibfk_2', 'goods_self_orders', 'driver_posts', ['driver_post'], ['id'])
    op.create_foreign_key(u'goods_self_orders_ibfk_1', 'goods_self_orders', 'consignors', ['consignors'], ['id'])
    op.drop_column('goods_self_orders', 'driver_post_id')
    op.drop_column('goods_self_orders', 'consignors_id')
    op.drop_column('goods', 'price_is_pay')
    op.drop_column('goods', 'online_pirce')
    op.add_column('driver_posts', sa.Column('consignor_user_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'driver_posts', type_='foreignkey')
    op.create_foreign_key(u'driver_posts_ibfk_3', 'driver_posts', 'goods', ['consignor_user_id'], ['id'])
    op.drop_column('driver_posts', 'consignor_id')
    op.drop_column('consignors', 'shenfenzheng')
    op.drop_column('consignors', 'fuzheren')
    op.create_table('articles',
    sa.Column('id', mysql.INTEGER(display_width=11), nullable=False),
    sa.Column('title', mysql.VARCHAR(length=64), nullable=True),
    sa.Column('show', mysql.TINYINT(display_width=1), autoincrement=False, nullable=True),
    sa.Column('click', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True),
    sa.Column('thumbnail', mysql.TEXT(), nullable=True),
    sa.Column('seokey', mysql.VARCHAR(length=128), nullable=True),
    sa.Column('seoDescription', mysql.VARCHAR(length=200), nullable=True),
    sa.Column('timestamp', mysql.DATETIME(), nullable=True),
    sa.Column('body', mysql.TEXT(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    mysql_default_charset=u'utf8',
    mysql_engine=u'InnoDB'
    )
    op.create_table('categorys',
    sa.Column('id', mysql.INTEGER(display_width=11), nullable=False),
    sa.Column('title', mysql.VARCHAR(length=64), nullable=True),
    sa.Column('show', mysql.TINYINT(display_width=1), autoincrement=False, nullable=True),
    sa.Column('sort', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True),
    sa.Column('pubd', mysql.DATETIME(), nullable=True),
    sa.Column('nlink', mysql.TEXT(), nullable=True),
    sa.Column('template', mysql.VARCHAR(length=64), nullable=True),
    sa.Column('body', mysql.TEXT(), nullable=True),
    sa.Column('seoKey', mysql.VARCHAR(length=200), nullable=True),
    sa.Column('seoDescription', mysql.VARCHAR(length=200), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    mysql_default_charset=u'utf8',
    mysql_engine=u'InnoDB'
    )
    op.create_table('goods_comments',
    sa.Column('id', mysql.INTEGER(display_width=11), nullable=False),
    sa.Column('send_goods_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id'),
    mysql_default_charset=u'utf8',
    mysql_engine=u'InnoDB'
    )
    op.create_table('category_attribute',
    sa.Column('id', mysql.INTEGER(display_width=11), nullable=False),
    sa.Column('name', mysql.VARCHAR(length=64), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    mysql_default_charset=u'utf8',
    mysql_engine=u'InnoDB'
    )
    op.create_table('redis_tasks',
    sa.Column('id', mysql.INTEGER(display_width=11), nullable=False),
    sa.Column('name', mysql.VARCHAR(length=80), nullable=True),
    sa.Column('redis_key', mysql.VARCHAR(length=128), nullable=True),
    sa.Column('start_time', mysql.DATETIME(), nullable=True),
    sa.Column('create_date', mysql.DATETIME(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    mysql_default_charset=u'utf8',
    mysql_engine=u'InnoDB'
    )
    op.create_table('order_tasks',
    sa.Column('id', mysql.INTEGER(display_width=11), nullable=False),
    sa.Column('order_str', mysql.VARCHAR(length=20), nullable=True),
    sa.Column('create_time', mysql.DATETIME(), nullable=True),
    sa.Column('run_time', mysql.DATETIME(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    mysql_default_charset=u'utf8',
    mysql_engine=u'InnoDB'
    )
    op.create_table('comments',
    sa.Column('id', mysql.INTEGER(display_width=11), nullable=False),
    sa.Column('body', mysql.TEXT(), nullable=True),
    sa.Column('body_html', mysql.TEXT(), nullable=True),
    sa.Column('timestamp', mysql.DATETIME(), nullable=True),
    sa.Column('disabled', mysql.TINYINT(display_width=1), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id'),
    mysql_default_charset=u'utf8',
    mysql_engine=u'InnoDB'
    )
    op.create_table('category_top',
    sa.Column('id', mysql.INTEGER(display_width=11), nullable=False),
    sa.Column('title', mysql.VARCHAR(length=255), nullable=True),
    sa.Column('show', mysql.TINYINT(display_width=1), autoincrement=False, nullable=True),
    sa.Column('nlink', mysql.TEXT(), nullable=True),
    sa.Column('sort', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True),
    sa.Column('template', mysql.VARCHAR(length=64), nullable=True),
    sa.Column('seoKey', mysql.VARCHAR(length=200), nullable=True),
    sa.Column('seoDescription', mysql.VARCHAR(length=200), nullable=True),
    sa.Column('body', mysql.TEXT(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    mysql_default_charset=u'utf8',
    mysql_engine=u'InnoDB'
    )
    op.create_table('Driver_self_orders',
    sa.Column('id', mysql.INTEGER(display_width=11), nullable=False),
    sa.Column('goods', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True),
    sa.Column('create_time', mysql.DATETIME(), nullable=True),
    sa.Column('driver', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True),
    sa.Column('state', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True),
    sa.Column('price', mysql.DECIMAL(precision=10, scale=2), nullable=True),
    sa.ForeignKeyConstraint(['driver'], [u'drivers.id'], name=u'driver_self_orders_ibfk_2'),
    sa.ForeignKeyConstraint(['goods'], [u'goods.id'], name=u'driver_self_orders_ibfk_1'),
    sa.PrimaryKeyConstraint('id'),
    mysql_default_charset=u'utf8',
    mysql_engine=u'InnoDB'
    )
    op.drop_table('driver_self_orders')
    op.drop_table('consignor_images')
    op.drop_table('tixianchengqings')
    op.drop_table('couponsion')
    # ### end Alembic commands ###
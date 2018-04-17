#coding=utf-8
"""filename:app/__init__.py
Created 2017-05-29
Author: by anaf
note:初始化函数，坑1
把“app = Flask(__name__)”放到create_app里面 
后面需要到app不知道怎么取
不能from app import app
def create_app(config_name):
"""

from flask import Flask,render_template,session
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from config import config
from flask_login import LoginManager
from flask_admin import Admin
from flask_babelex import Babel
from flask_debugtoolbar import DebugToolbarExtension
from flask_bootstrap import Bootstrap
from rq import Queue
from rq.job import Job
from datetime import timedelta

from flask_apscheduler import APScheduler
from flask_wechatpy import Wechat, wechat_required, oauth

from wechatpy.replies import TextReply
from wechatpy.replies import create_reply


from wechatpy.enterprise import WeChatClient
from flask_admin.contrib.sqla import ModelView

from flask_cache import Cache


scheduler = APScheduler()
flask_wechat = Wechat()
# client = WeChatClient('wxbdd2d9798f27f33a', '7d7b898b7e27957c5d1a11d407be61e0')

DEFAULT_APP_NAME = 'car'

mail = Mail()
moment = Moment()
db = SQLAlchemy()
login_manager = LoginManager()
babel = Babel()
toolbar = DebugToolbarExtension()
bootstrap = Bootstrap()
cache = Cache()


# q = Queue(connection=conn)
# import queue_daemon



#session_protection属性可以设置None，basic，strong提供不同的安全等级防止用户会话遭篡改
login_manager.session_protection ='strong'
#这个login_view  多了一个s，变成了login_views导致错误401  花了好几个钟头查找原因
# login_manager.login_view = 'auth.login'
#自动注册
login_manager.login_view = 'auth.autoregister'
login_manager.login_message = u"请登录后访问该页面."
login_manager.refresh_view = 'auth.login'
app = Flask(__name__)

def create_app(config_name):
	
	
	app.config.from_object(config[config_name])


	# queue_daemon(app)

	#配置文件
	configure_config(app)
	#init初始化
	configure_extensions(app)
	#蓝图
	configure_blueprint(app)
	#创建flask-admin后台
	configure_create_admin(app)

	
	config[config_name].init_app(app)

	#注册自定义过滤器 替换模板手机号码
	app.jinja_env.filters['replace_substring'] = replace_substring




	#wx item
	


	
	

	return app


"""
python manage.py shell 
from app import db 
db.create_all()
xuser_mod = User(username='moderator',password='moderator',role=mod_role)
user_user = User(username='use',password='use',role=user_role)
db.session.add(admin_role)
db.session.add(mod_role)
db.session.add(user_role)
db.session.add_all([user_admin,user_mod,user_user])
db.session.commit()
"""


def configure_extensions(app):
	mail.init_app(app)
	moment.init_app(app)
	db.init_app(app)
	flask_wechat.init_app(app)
	babel.init_app(app)
	# toolbar.init_app(app)
	login_manager.init_app(app)
	bootstrap.init_app(app)

	scheduler.init_app(app)
	#flask定时器
	scheduler.start()

	cache.init_app(app)



def configure_blueprint(app):
	from .main import main as main_blueprint
	app.register_blueprint(main_blueprint)
	from .auth import auth as auth_blueprint
	app.register_blueprint(auth_blueprint,url_prefix='/auth')
	from .driver import driver as driver_blueprint
	app.register_blueprint(driver_blueprint,url_prefix='/driver')
	from .goods import goods as goods_blueprint
	app.register_blueprint(goods_blueprint,url_prefix='/consignor')
	# from .test import codetest as codetest_blueprint
	# app.register_blueprint(codetest_blueprint,url_prefix='/codetest')
	from .usercenter import usercenter as user_blueprint
	app.register_blueprint(user_blueprint,url_prefix='/usercenter')

	from .wechat import wechat as wechat_blueprint
	app.register_blueprint(wechat_blueprint,url_prefix='/wechat')

	from .superadmin import superadmin as superadmin_blueprint
	app.register_blueprint(superadmin_blueprint,url_prefix='/superadmin')


def configure_config(app):
	app.config['BABEL_DEFAULT_LOCALE'] = 'zh_CN'
	app.config['UPLOAD_FOLDER_ADMIN_IMAGES'] ='\\static\\uploads\\admin\\images'
	app.config['UPLOAD_FOLDER_ADMIN'] ='\\static\\uploads\\admin'
	

#flask-admin
def configure_create_admin(app):
	from app.models import User,Driver,Goods,Driver_post,Position,User_msg,Consignor,Order_pay,Driver_self_order
	from app.admin_views import MyAdminIndexView
	admin_app = Admin(name='car', template_mode='bootstrap3')
	# admin_app = Admin(name='car',index_view=MyAdminIndexView())
	admin_app.add_view(ModelView(User, db.session))
	# admin_app.add_view(ModelView(Driver, db.session))
	admin_app.add_view(ModelView(Driver_post, db.session))
	admin_app.add_view(ModelView(Position, db.session))
	admin_app.add_view(ModelView(User_msg, db.session))
	# admin_app.add_view(ModelView(Consignor, db.session))
	# admin_app.add_view(ModelView(Goods, db.session))
	admin_app.add_view(ModelView(Order_pay, db.session))
	admin_app.add_view(ModelView(Driver_self_order, db.session))
	# from admin import *
	# admin_app.add_view(ModelView_User(db.session,name=u'用户管理'))
	# admin_app.add_view(ModelView_Article(db.session,name=u'文章管理'))
	# admin_app.add_view(ModelView_Category(db.session,name=u'栏目管理'))
	# admin_app.add_view(ModelView_CategoryTop(db.session,name=u'顶级栏目'))
	# admin_app.add_view(ModelView(User,db.session,name=u'留言管理'))
	# admin_app.add_view(ModelView(Category_attribute,db.session,name=u'栏目属性表(不要随意更改)'))
	# admin_app.add_view(ModelView(Comment,db.session,name=u'评论管理'))
	# admin_app.add_view(Admin_static_file(path,'/static', name=u'文件管理'))
	# admin_app.add_view(Admin_logout(name=u'退出'))
	admin_app.init_app(app)


#替换手机号码保留后3位数
def replace_substring(phone):
	phone = str(phone)
	return phone.replace(phone[:-4],'***')

#设置会话过期时间。。
@app.before_request
def make_session_permanent():
	session.permanent = True
	#1440一天24*60分钟
	app.permanent_session_lifetime = timedelta(minutes=1440)





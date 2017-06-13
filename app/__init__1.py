#coding=utf-8
"""filename:app/__init__.py
Created 2017-05-29
Author: by anaf
note:初始化函数
"""

from flask import Flask,render_template
from flask.ext.mail import Mail
from flask.ext.moment import Moment
from flask.ext.sqlalchemy import SQLAlchemy
from config import config
from flask.ext.login import LoginManager
from flask.ext.admin import Admin
from flask_babelex import Babel


DEFAULT_APP_NAME = 'car'

mail = Mail()
moment = Moment()
db = SQLAlchemy()
login_manager = LoginManager()
babel = Babel()





# admin2 = Admin(url='/admin99', endpoint='admin2',name='chahua3287')


#session_protection属性可以设置None，basic，strong提供不同的安全等级防止用户会话遭篡改
login_manager.session_protection ='strong'
login_manager.login_views = 'auth.login'
login_manager.login_message = u"请登录后访问该页面."
login_manager.refresh_view = 'auth.login'

def create_app(config_name):
	app = Flask(__name__)
	app.config.from_object(config[config_name])

	#配置文件
	configure_config(app)
	#init初始化
	configure_extensions(app)
	#蓝图
	configure_blueprint(app)
	#创建flask-admin后台
	# configure_create_admin(app)

	


	
	# from .users import users as user_blueprint
	# app.register_blueprint(user_blueprint,url_prefix='/user')

	# from .admins import admin_b as admins_blueprint
	# app.register_blueprint(admins_blueprint)

	
	config[config_name].init_app(app)
	

	return app

"""
python manage.py shell 
from app import db 
db.create_all()
from app.models import Role,User
admin_role = Role(name = 'admin')
mod_role = Role(name = 'Moderator')
user_role = Role(name = 'User')
user_admin = User(username='admins',password='admins',role=admin_role)
user_mod = User(username='moderator',password='moderator',role=mod_role)
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
	
	babel.init_app(app)
	login_manager.init_app(app)


def configure_blueprint(app):
	from .main import main as main_blueprint
	app.register_blueprint(main_blueprint)
	from .auth import auth as auth_blueprint
	app.register_blueprint(auth_blueprint,url_prefix='/auth')
	# from .driver import driver as driver_blueprint
	# app.register_blueprint(driver_blueprint,url_prefix='/driver')
	# from .consignor import consignor as consignor_blueprint
	# app.register_blueprint(consignor_blueprint,url_prefix='/consignor')


def configure_config(app):
	
	app.config['BABEL_DEFAULT_LOCALE'] = 'zh_CN'
	app.config['UPLOAD_FOLDER_ADMIN_IMAGES'] ='\\static\\uploads\\admin\\images'
	app.config['UPLOAD_FOLDER_ADMIN'] ='\\static\\uploads\\admin'
	

def configure_create_admin(app):
	from app.admin_views import MyAdminIndexView
	admin_app = Admin(name='chahua3287',index_view=MyAdminIndexView())
	from admin import *
	admin_app.add_view(ModelView_User(db.session,name=u'用户管理'))
	admin_app.add_view(ModelView_Article(db.session,name=u'文章管理'))
	admin_app.add_view(ModelView_Category(db.session,name=u'栏目管理'))
	admin_app.add_view(ModelView_CategoryTop(db.session,name=u'顶级栏目'))
	# admin_app.add_view(ModelView(User_msg,db.session,name=u'留言管理'))
	# admin_app.add_view(ModelView(Category_attribute,db.session,name=u'栏目属性表(不要随意更改)'))
	# admin_app.add_view(ModelView(Comment,db.session,name=u'评论管理'))
	admin_app.add_view(Admin_static_file(path,'/static', name=u'文件管理'))
	admin_app.add_view(Admin_logout(name=u'退出'))
	admin_app.init_app(app)









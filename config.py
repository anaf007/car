#coding=utf-8
"""filename:config.py
Created 2017-06-12
Author: by anaf
"""
import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
	#保护字段，必须设置  
	SECRET_KEY = os.environ.get('SECRET_KEY') or 'strings'
	#sql自动提交
	SQLALCHEMY_COMMIT_ONTRARDOWN = True
	#####
	SQLALCHEMY_TRACK_MODIFICATIONS  = False
	#redis
	REDIS_URL = "redis://:@localhost:6379/car"
	# REDIS_URL  =  "unix://[:password]@/path/to/socket.sock?db=0"
	#redis缓存
	ONLINE_LAST_MINUTES = 5

	DEBUG = False

	SQLALCHEMY_COMMIT_ON_TEARDOWN = True
	SQLALCHEMY_TRACK_MODIFICATIONS = True

	REDIS_QUEUE_KEY = 'my_queue'

	#微信配置
	CORP_ID = 'wxb6eb5bc8b62ee6d8'
	SECRET = '5bdcb41b6dffd749d50a217c12609c55'

	#qq登录配置
	QQ_APP_ID = os.getenv('QQ_APP_ID', '101187283')
	QQ_APP_KEY = os.getenv('QQ_APP_KEY', '993983549da49e384d03adfead8b2489')


	# PERMANENT_SESSION_LIFETIME = 31

	@staticmethod
	def init_app(app):
		pass

#开发配置
class DevelopmentConfig(Config):
	DEBUG = True
	SUPERADMIN_NAME = os.environ.get('SUPERADMIN_NAME') or 'admin'
	#配置数据库路径从系统变量读取没有就根据字符串中的读取 mysql为例子
	SQLALCHEMY_DATABASE_URI = os.environ.get('dev_database_url') or \
		'mysql://root:@127.0.0.1:3306/car'

#测试配置
class TestingConfig(Config):
	TESTING = True
	SQLALCHEMY_DATABASE_URI = os.environ.get('dev_database_url') or \
		'mysql://root:@127.0.0.1:3306/car'


class ProductionConfig(Config):
	SQLALCHEMY_DATABASE_URI = os.environ.get('dev_database_url') or \
		'mysql://root:@localhost:3306/car'


config = {
	'development' : DevelopmentConfig,
	'testing': TestingConfig,
	'production': ProductionConfig,
	'default': DevelopmentConfig
}


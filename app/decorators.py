#coding=utf-8
"""filename:decorators.py
Created 2017-05-30
Author: by anaf
note: 让视图函数只对具有特定权限的用户开放 自定义装饰器
"""

from functools import wraps
from flask import abort
from flask_login import current_user
from .models import Permission

def permission_required(permission):
	def decorator(f):
		@wraps(f)
		def decorated_function(*args,**kwargs):
			if not current_user.can(permission):
				abort(403)
			return f(*args,**kwargs)
		return decorated_function
	return decorator

def admin_required(f):
	return permission_required(Permission.ADMINISTER)(f)

def driver_required(f):
	return permission_required(Permission.DRIVER)(f)

def goods_required(f):
	return permission_required(Permission.CONSIGNOR)(f)


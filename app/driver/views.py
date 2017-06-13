#coding=utf-8
"""filename:app/main/views.py
Created 2017-06-12
Author: by anaf
"""

# from flask import current_app
from  flask.ext.login import login_required,current_user
from ..decorators import driver_required,permission_required
from . import driver

#需要登陆，且需要管理员权限
@driver.route('/')
@driver.route('/')
@driver.route('/index/')
@login_required
def index():
	return "for driver"
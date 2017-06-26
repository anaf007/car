#coding=utf-8
"""filename:app/driver/__init__.py
Created 2017-06-12
Author: by anaf
note:driver/__init__.py  Blueprint蓝图
""" 

from flask import Blueprint

driver = Blueprint('driver',__name__)

from . import views 
from flask import render_template

# from ..models import Permission

#添加上下文
# @driver.app_context_processor
# def inject_permissions():
# 	return dict(Permission=Permission)

@driver.app_errorhandler(404)
def page_not_found(e):
	return render_template('/driver/404.html'),404

@driver.app_errorhandler(500)
def internal_server_error(e):
	return render_template('/driver/500.html'),500

@driver.app_errorhandler(403)
def page_403(e):
	return render_template('/driver/403.html'),403



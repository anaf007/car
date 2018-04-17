#coding=utf-8
"""filename:app/superadmin/__init__.py
Created 2017-07-24
Author: by anaf
note:superadmin/__init__.py  Blueprint蓝图
""" 

from flask import Blueprint

superadmin = Blueprint('superadmin',__name__)

from . import views 
from flask import render_template

# from ..models import Permission

#添加上下文
# @driver.app_context_processor
# def inject_permissions():
# 	return dict(Permission=Permission)

@superadmin.app_errorhandler(404)
def page_not_found(e):
	return render_template('/superadmin/404.html'),404

@superadmin.app_errorhandler(500)
def internal_server_error(e):
	return render_template('/superadmin/500.html'),500

@superadmin.app_errorhandler(403)
def page_403(e):
	return render_template('/superadmin/403.html'),403



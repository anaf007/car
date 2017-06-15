#coding=utf-8
"""filename:app/driver/__init__.py
Created 2017-06-12
Author: by anaf
note:driver/__init__.py  Blueprint蓝图
""" 

from flask import Blueprint

driver = Blueprint('driver',__name__)

from . import views 

# from ..models import Permission

#添加上下文
# @driver.app_context_processor
# def inject_permissions():
# 	return dict(Permission=Permission)
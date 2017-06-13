#coding=utf-8
"""filename:app/main/__init__.py
Created 2017-05-29
Author: by anaf
note:main/__init__.py  Blueprint蓝图
""" 

from flask import Blueprint

main = Blueprint('main',__name__)

from . import views,errors 

from ..models import Permission

#添加上下文
@main.app_context_processor
def inject_permissions():
	return dict(Permission=Permission)
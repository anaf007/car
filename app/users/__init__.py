#coding=utf-8
"""filename:app/user/__init__.py
Created 2017-05-29
Author: by anaf
note:user/__init__.py  Blueprint蓝图
""" 

from flask import Blueprint

users = Blueprint('user',__name__)

from . import views 


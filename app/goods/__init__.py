#coding=utf-8
"""filename:app/goods/__init__.py
Created 2017-06-15
Author: by anaf
note:goods/__init__.py  Blueprint蓝图
""" 

from flask import Blueprint

goods = Blueprint('goods',__name__)

from . import views
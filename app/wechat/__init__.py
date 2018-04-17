#coding=utf-8
"""filename:app/user/__init__.py
Created 2017-09-28
Author: by anaf
note:weatch/__init__.py  Blueprint蓝图 公众号
""" 

from flask import Blueprint

wechat = Blueprint('wechat',__name__)

from . import wechat_view





#coding=utf-8
"""filename:app/user/__init__.py
Created 2017-05-29
Author: by anaf
note:user/__init__.py  Blueprint蓝图
""" 

from flask import Blueprint

usercenter = Blueprint('usercenter',__name__)

from . import views 


#获取下单次数
@usercenter.context_processor
def getSend_Driver_post_Count():
    def get(items = []):
    	itemscount = 0
    	for i in  items:
    		itemscount +=i.post.count()
    	return itemscount
    return dict(getSend_Driver_post_Count=get)

@usercenter.context_processor
def getSendItemsCount():
    def get(items = []):
    	itemscount = 0
    	for i in  items:
    		itemscount +=i.goods_id.count()
    	return itemscount
    return dict(getSend_Goods_Count=get)



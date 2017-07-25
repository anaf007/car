#coding=utf-8

from . import superadmin
from flask import render_template,flash,redirect,url_for,request,abort
from  flask.ext.login import login_required,current_user
from app.models import Goods,Driver,Driver_self_order
from datetime import datetime
from ..decorators import *
from app import db

@superadmin.route('/')
@superadmin.route('/index')
@login_required
def index():
	return render_template('superadmin/index.html')


#货物预约列表
@superadmin.route('/make_goods')
@login_required
def make_goods():
	goods = Goods.query.filter(Goods.state==0).filter(Goods.start_car_time>datetime.utcnow()).order_by('create_time').all()
	return render_template('superadmin/make_goods.html',goods=goods)


#货物详细预约信息
@superadmin.route('/make_goods_show')
@superadmin.route('/make_goods_show/<int:id>')
@login_required
def make_goods_show(id=0):
	goods = Goods.query.get_or_404(id)
	return render_template('superadmin/make_goods_show.html',goods=goods)


#确认用户
@superadmin.route('/make_goods_comfirm')
@superadmin.route('/make_goods_comfirm/<int:goodsid>/<int:driverid>/<int:confirmid>')
@login_required
def make_goods_comfirm(goodsid=0,driverid=0,confirmid=0):
	print goodsid
	print driverid
	print confirmid

	goods = Goods.query.get_or_404(goodsid)
	print goods 
	driver = Driver.query.get_or_404(driverid)
	print driver
	confirm = Driver_self_order.query.get_or_404(confirmid)
	
	
	print confirm
	confirm.state = 1
	goods.state = 1
	db.session.add(confirm)
	db.session.add(goods)
	db.session.commit()
	return 'ok'





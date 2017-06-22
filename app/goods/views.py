#coding=utf-8
"""filename:app/goods/views.py
Created 2017-06-15
Author: by anaf
note:货源信息栏目，首页货物显示及某些司机看的页面，只能司机访问，所以是 @permission_required(Permission.DRIVER)

"""

from . import goods
from flask import render_template,flash,redirect,url_for,request,abort
from  flask.ext.login import login_required,current_user
from ..decorators import permission_required
from app.models import Permission,Goods,Order_pay,Driver
from .forms import GoodsForm
from app import db
import random,time
from datetime import datetime
from decimal import Decimal

@goods.route('/')
@goods.route('/index')
@goods.route('/index/')
@login_required
@permission_required(Permission.DRIVER)
#只能司机查看首页的货物信息
def index():
	return render_template('goods/index.html',goods = Goods.query.filter_by(state=0).order_by('create_time').all())


@goods.route('/send_goods')
@login_required
@permission_required(Permission.CONSIGNOR)
#发布货源信息  只能货主访问
def send_goods():
	return render_template('goods/send_goods.html',form = GoodsForm())

@goods.route('/send_goods',methods=['POST'])
@login_required
@permission_required(Permission.CONSIGNOR)
def send_goods_post():
	form = GoodsForm()
	if form.validate_on_submit():
		good = Goods()
		good.name = form.name.data
		good.unit = form.unit.data
		good.count = form.count.data
		good.start_address = form.start_address.data
		good.end_address = form.end_address.data
		good.start_car_time = form.start_car_time.data
		good.note = form.note.data
		good.start_price = form.start_price.data
		good.state = 0
		good.user_goods = current_user
		try:
			db.session.add(good)
			db.session.commit()
			flash(u'发布成功')
		except Exception, e:
			db.session.rollback()
			flash(u'发布失败')
	else:
		flash(u'校验数据错误')
	return redirect(url_for('.send_goods'))



#显示货物信息，司机访问
@goods.route('/show_goods')
@goods.route('/show_goods/<int:id>')
@login_required
@permission_required(Permission.DRIVER)
def show_goods(id=0):
	gd = Goods.query.get_or_404(id)
	return render_template('goods/show_goods.html',gd = gd)



#接货下单  司机访问
@goods.route('/send_order',methods=['POST'])
@login_required
@permission_required(Permission.DRIVER)
def send_order():
	id = request.form.get('id')
	try:
		gd = Goods.query.get_or_404(int(id))
	except Exception, e:
		abort(403)
	
	return render_template('goods/send_order.html',gd=gd)

#确认接货下单  司机访问
#这里是司机下单过程  需要限时支付，需要到缓存机制
#目前没有使用限时支付
@goods.route('/confirm_order',methods=['POST'])
@login_required
@permission_required(Permission.DRIVER)
def confirm_order():
	id = request.form.get('id')
	car_id = request.form.get('car')
	choice_str = 'ABCDEFGHJKLNMPQRSTUVWSXYZ'
	order_str = ''
	str_time =  time.time()
	order_str = str(int(int(str_time)*1.347))+order_str
	for i in range(10):
		order_str += random.choice(choice_str)
	try:
		gd = Goods.query.get_or_404(int(id))
		car = Driver.query.get_or_404(int(car_id))
	except Exception, e:
		abort(403)
	op = Order_pay()
	op.order = order_str
	op.order_pay = gd
	op.order_pays = car
	op.order_pay_user = current_user
	gd.car_goods = current_user
	gd.receive_time = datetime.utcnow()
	gd.state = 2
	op.pay_price = Decimal(float(gd.start_price) * 0.3)
	
	
	try:
		db.session.add(op)
		db.session.add(gd)
		db.session.commit()
	except Exception, e:
		return 'error%s'%str(e)

	return redirect(url_for('goods.index'))







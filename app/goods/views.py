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
from app.models import Permission,Goods,Order_pay,Driver,Order_Task
from .forms import GoodsForm
from app import db,scheduler,app
import random,time
from datetime import datetime
from decimal import Decimal
from app import redis_store
import logging
import datetime as datime


@goods.route('/')
@goods.route('/index')
@goods.route('/index/')
@login_required
@permission_required(Permission.DRIVER)
#只能司机查看首页的货物信息
def index():
	#查询发车时间大于当前时间
	goods = Goods.query.filter(Goods.state==0).filter(Goods.start_car_time>datetime.utcnow()).order_by('create_time').all()
	return render_template('goods/index.html',goods = goods)


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
	good = Goods()
	start_sheng = request.form.get('start_sheng')
	start_shi = request.form.get('start_shi')
	start_qu = request.form.get('start_qu')

	end_sheng = request.form.get('end_sheng')
	end_shi = request.form.get('end_shi')
	end_qu = request.form.get('end_qu')

	if not start_sheng:
		flash(u'请选择发货地点')
		return redirect(url_for('.send_goods'))
	if not end_sheng:
		flash(u'请选择到货地点')
		return redirect(url_for('.send_goods'))



	if start_shi:
		form.start_address.data = start_sheng+"-"+start_shi
	if start_qu:
		form.start_address.data = start_sheng+"-"+start_shi+"-"+start_qu

	if end_shi:
		form.end_address.data = end_sheng+"-"+end_shi
	if end_qu:
		form.end_address.data = end_sheng+"-"+end_shi+"-"+end_qu

	if form.validate_on_submit():
		
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
	if gd.start_car_time<datetime.utcnow():
		return u'发车时间不能小于当前时间，该信息已过期！<a href="/">返回主页</a>'
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
@goods.route('/confirm_order',methods=['POST'])
@login_required
@permission_required(Permission.DRIVER)
def confirm_order():
	req_id = request.form.get('id')
	car_id = request.form.get('car')
	choice_str = 'ABCDEFGHJKLNMPQRSTUVWSXYZ'
	order_str = ''
	str_time =  time.time()
	order_str = str(int(int(str_time)*1.347))+order_str
	for i in range(9):
		order_str += random.choice(choice_str)
	try:
		gd = Goods.query.get_or_404(int(req_id))
		car = Driver.query.get_or_404(int(car_id))
	except Exception, e:
		abort(403)
	order_str = 'H'+order_str

	op = Order_pay()
	op.order = order_str
	op.order_pay = gd
	op.order_pays = car
	op.order_pay_user = current_user
	gd.car_goods = current_user
	gd.receive_time = datetime.utcnow()
	gd.state = 1  #1司机已下单
	op.pay_price = Decimal(float(gd.start_price) * 0.3)

	
	try:
		db.session.add(op)
		db.session.add(gd)
		db.session.commit()

		#限时支付
		from apscheduler.triggers.interval import IntervalTrigger
		now = datetime.now()
		#年year月mom日day 时hour分min秒seconds
		delta = datime.timedelta(seconds=600)
		n_days = now + delta
		runtime = n_days.strftime('%Y-%m-%d %H:%M:%S')
		db.session.add(Order_Task(order_str=order_str,create_time=datetime.utcnow(),run_time=runtime))
		db.session.commit()
		#添加定时任务
		scheduler.add_job(func=limit_confirm_pay,id=order_str,args=[order_str,],trigger=IntervalTrigger(seconds=600),replace_existing=True)
		# print datetime.utcnow()
		#此处应该是跳转到支付页面url_for
	except Exception, e:
		return 'error:%s'%str(e)
		
	return redirect(url_for('goods.index'))

#司机接单限时支付
def limit_confirm_pay(order_str):
	#不添加日志会提示错误
	logging.basicConfig()
	#数据库操作
	with app.app_context():
		#获取任务信息
		ot = Order_Task.query.filter_by(order_str=order_str).first()
		op = Order_pay.query.filter_by(order=ot.order_str).first()
		if op.state==0:
			op.state = -1
			#货物信息
			op.order_pay.state = 0
			db.session.add(op)
		db.session.delete(ot)
		db.session.commit()
	#删除队列任务
	scheduler.delete_job(id=order_str)















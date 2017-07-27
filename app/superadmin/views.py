#coding=utf-8

from . import superadmin
from flask import render_template,flash,redirect,url_for,request,abort
from  flask.ext.login import login_required,current_user
from app.models import Goods,Driver,Driver_self_order,User_msg,Order_pay
from datetime import datetime
from ..decorators import *
from app import db
import time,random
from decimal import Decimal

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


#确认用户  确认用户后将添加支付信息 ，消息通知信息
@superadmin.route('/make_goods_comfirm')
@superadmin.route('/make_goods_comfirm/<int:goodsid>/<int:driverid>/<int:confirmid>/<price>')
@login_required
def make_goods_comfirm(goodsid=0,driverid=0,confirmid=0,price='0.00'):
	
	#货物
	goods = Goods.query.get_or_404(goodsid);
	#车辆
	driver = Driver.query.get_or_404(driverid);
	#司机自助下单信息
	dso = Driver_self_order.query.get_or_404(confirmid)	
	if dso.state ==1:
		flash(u'该信息已经确认了承运司机，请不要重复确认。','error')
		return redirect(url_for('main.index'))

	#此处应该做判断是否非法访问
	dso.state = 1
	goods.state = 1
	goods.end_price = price
	db.session.add(dso)
	# db.session.commit()
	
	db.session.add(goods)
	
	

	#以上修改货物状态，以下添加支付订单信息 用户消息通知信息

	choice_str = 'ABCDEFGHJKLNMPQRSTUVWSXYZ'
	order_str = ''
	str_time =  time.time()
	order_str = str(int(int(str_time)*1.347))+order_str
	for i in range(9):
		order_str += random.choice(choice_str)
	
	order_str = 'H'+order_str

	op = Order_pay()
	op.order = order_str
	#货物信息表
	op.goods_order_pay = goods
	#车辆表
	op.order_pays = driver
	#支付用户 用于判断是否司机或者货主的支付
	# op.order_pay_user = current_user
	#因为一辆车有多个用户使用，所以多增加的这个字段用于是当前哪一个用户登录并下单的
	#
	#车辆用户  #如果一辆车有多个用户呢？ 或者车队 将报错？
	op.order_pay_user = driver.driver_user
	#接单实际
	goods.receive_time = datetime.utcnow()
	goods.state = 1  #1司机已下单
	#dp  Driver_post
	# dp.state = 4  #具体字段意思是看models模型设计   4为司机自己寻找货源
	#支付金额
	
	price = "%.2f" % (float(price) * 0.3-float(current_user.price))
	# print Decimal(float(price) * 0.3-float(current_user.price)).prec(2)
	
	op.pay_price = Decimal(price)

	um = User_msg()
	um.title = u'您有一条货物定金支付信息'
	um.body = u'您已经确认了承载【%s】的货物，<a href="/zhifudingjin">点击支付货物的定金</a>。暂定内容。'%(goods.start_shi+'-'+goods.end_shi)
	um.state = 0
	um.user_msg = driver.driver_user

	
	try:
		db.session.add(op)

		db.session.add(um)
		db.session.commit()

		#限时支付
		# from apscheduler.triggers.interval import IntervalTrigger
		# now = datetime.now()
		# #年year月mom日day 时hour分min秒seconds
		# delta = datime.timedelta(seconds=30)
		# n_days = now + delta
		# runtime = n_days.strftime('%Y-%m-%d %H:%M:%S')
		# db.session.add(Order_Task(order_str=order_str,create_time=datetime.utcnow(),run_time=runtime))
		# db.session.commit()
		#添加定时任务
		# scheduler.add_job(func=limit_confirm_pay,id=order_str,args=[order_str,],trigger=IntervalTrigger(seconds=30),replace_existing=True)
		# print datetime.utcnow()
		#此处应该是跳转到支付页面url_for
	except Exception, e:
		print str(e)
		return 'error:%s'%str(e)
		
	return redirect(url_for('goods.index'))


	# return 'ok'





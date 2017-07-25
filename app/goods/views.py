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
from app.models import Permission,Goods,Order_pay,Driver,\
Order_Task,Driver_post,Consignor,User,Role,Car_Info,Car_Type,Driver_self_order
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
# @permission_required(Permission.DRIVER)
#只能司机查看首页的货物信息
def index():
	#查询发车时间大于当前时间
	goods = Goods.query.filter(Goods.state==0).filter(Goods.start_car_time>datetime.utcnow()).order_by('create_time').all()
	return render_template('goods/index.html',goods = goods)


@goods.route('/send_goods')
@login_required
#发布货源信息  只能货主访问
def send_goods():
	carinfo = Car_Info.query.order_by(Car_Info.sort).all()
	cartype = Car_Type.query.all()
	return render_template('goods/send_goods.html',form = GoodsForm(),carinfo = carinfo,cartype=cartype)


@goods.route('/send_goods',methods=['POST'])
@login_required
def send_goods_post():
	# form = GoodsForm()
	good = Goods()
	start_sheng = request.form.get('start_sheng')
	start_shi = request.form.get('start_shi')
	start_qu = request.form.get('start_qu')
	start_xiangxi_address = request.form.get('start_xiangxi_address')

	end_sheng = request.form.get('end_sheng')
	end_shi = request.form.get('end_shi')
	end_qu = request.form.get('end_qu')
	end_xiangxi_address = request.form.get('end_xiangxi_address')

	mon = request.form.get('mon')
	day = request.form.get('day')
	zone = request.form.get('zone')

	if not start_sheng:
		flash(u'请选择发货地点','error')
		return redirect(url_for('.send_goods'))
	if not end_sheng:
		flash(u'请选择到货地点','error')
		return redirect(url_for('.send_goods'))

	if not start_shi:
		flash(u'请选择出发城市','error')
		return redirect(url_for('.send_goods'))

	if not end_shi:
		flash(u'请选择目的城市','error')
		return redirect(url_for('.send_goods'))


	# if start_shi:
	# 	start_address = start_sheng+"-"+start_shi
	# if start_qu:
	# 	start_address = start_sheng+"-"+start_shi+"-"+start_qu

	# if end_shi:
	# 	end_address = end_sheng+"-"+end_shi
	# if end_qu:
	# 	end_address = end_sheng+"-"+end_shi+"-"+end_qu

	if current_user.phone=='' or not current_user.phone:
		if request.form.get('phone') =='' or request.form.get('phone') == None:
			flash(u'数据校验失败,请输入手机号码','error')
			return redirect(url_for('.send_goods'))

	yesr = time.strftime('%Y',time.localtime(time.time()))
	timestr = yesr+'/'+mon+'/'+day
	consignor = Consignor()

	#货物名称
	
	#单位
	# good.unit = form.unit.data
	#数量
	good.count = 1
	#开始地址
	good.start_address = start_xiangxi_address
	good.start_sheng = start_sheng
	good.start_shi = start_shi
	good.start_qu = start_qu
	good.start_xiangxi_address = start_sheng+start_shi+start_qu+start_xiangxi_address
	#达到地址
	good.end_address = end_xiangxi_address
	good.end_sheng = end_sheng
	good.end_shi = end_shi
	good.end_qu = end_qu
	good.end_xiangxi_address = end_sheng+end_shi+end_qu+end_xiangxi_address
	
	#装车时间
	good.start_car_time = timestr
	#装车时段
	good.start_zone = request.form.get('zone')
	#备注
	good.note = request.form.get('note')
	#报价运费
	good.start_price = request.form.get('price')
	#状态0刚发布信息
	good.state = 0

	zhengche = request.form.get('zhengche')
	pingche = request.form.get('pingche')

	if zhengche:
		good.name = request.form.get('zhengche')
		good.select_car_type = u'整车'
		good.car_type = request.form.get('chexing')
		chechang = request.form.get('chechang').split(',')
		good.car_length = chechang[0]
		good.tiji = chechang[1]
		good.zhongliang = chechang[2]
	if pingche:
		good.name = request.form.get('pingche')
		good.select_car_type = u'拼车'
		good.car_length = u'拼车'
		good.car_type = u'拼车'
		good.tiji = request.form.get('tiji')
		good.zhongliang = request.form.get('zhongliang')

	#没有货主的公司先系统默认注册一个公司

	if not current_user.consignors:
		phone = request.form.get('phone')
		if User.query.filter_by(phone=phone).first():
			flash(u'该手机号码已经被注册，请登录后再发布。','login')
			return redirect(url_for('auth.login'))

		consignor.consignor_user = current_user
		consignor.name = u'系统默认的公司名称'
		consignor.note = u'联系电话：'+phone
		consignor.state = 0 #未开通 未认证信息
		try:
			r = Role.query.filter_by(name=u'货主').first()
			current_user.role =  r
			current_user.phone =  phone
			db.session.add(current_user)
			db.session.add(consignor)
			db.session.commit()
		except Exception, e:
			flash(u'数据错误，添加失败：%s'%str(e),'error')
			db.session.rollback()
			return redirect(url_for('.send_goods'))



	#外键货主表货主表
	good.consignorsGoods = current_user.consignors
	try:
		db.session.add(good)
		db.session.commit()
		flash(u'预约返程车信息发布成功','success')
	except Exception, e:
		db.session.rollback()
		flash(u'预约返程车信息发布失败：%s'%str(e),'error')
	
		
	return redirect(url_for('.send_goods'))



#显示货物信息，司机访问
@goods.route('/show_goods')
@goods.route('/show_goods/<int:id>')
@login_required
def show_goods(id=0):
	if current_user.role.name==u'货主':
		flash(u'您是货主不能查看货物详情。','error')
		return redirect(url_for('main.index'))
	gd = Goods.query.get_or_404(id)
	if gd.start_car_time<datetime.utcnow():
		return u'发车时间不能小于当前时间，该信息已过期！<a href="/">返回主页</a>'
	return render_template('goods/show_goods.html',gd = gd)



#自行接货下单，预约确认
@goods.route('/send_order',methods=['POST'])
@login_required
# @permission_required(Permission.DRIVER)
def send_order():

	goodsid = request.form.get('goodsid')
	try:
		gd = Goods.query.get_or_404(int(goodsid))
	except Exception, e:
		abort(403)

	#如果没有手机号，获取手机号码  更改用户角色 为司机
	d = Driver()
	if current_user.phone=='' or current_user.phone ==None:
		phone = request.form.get('phone')
		if not phone:
			flash(u'请输入手机号码。','error')
			return redirect(url_for('main.index'))
		if User.query.filter_by(phone=phone).first():
			flash(u'该手机号码已经被注册，请登录后再发布。','login')
			return redirect(url_for('auth.login'))
		d.users = current_user
		d.phone = phone
		d.number = u'联系电话'+phone
		
		d.note = u'默认车辆信息，联系电话'+phone
		d.driver_user = current_user
		d.use.append(current_user)
		r = Role.query.filter_by(name=u'司机').first()
		try:
			db.session.add(d)
			# gd.make_count  = gd.make_count+1
			current_user.role =  r
			current_user.phone =  phone
			db.session.add(current_user)
			# db.session.add(gd)
			db.session.commit()
		except Exception, e:
			flash(u'数据错误，添加失败：%s'%str(e),'error')
			db.session.rollback()
			return redirect(url_for('.show_goods'))
	else:
		d = Driver.query.get_or_404(int(request.form.get('car')))

	selfdriverpost = Driver_self_order.query.filter_by(goods=gd.id,driver=d.id).first()
	
	if selfdriverpost:
		flash(u'您已经预约过了，请不要重复预约','error')
		return redirect(url_for('main.index'))
	else:
		flash(u'预约成功，系统审核通过将电话通知您。','success')
		db.session.add(Driver_self_order(driver_self_orders=gd,driver_self_order_driver=d))


	#预约人数+1
	gd.make_count  = gd.make_count+1
	db.session.add(gd)
	db.session.commit()


	start_price = float(gd.start_price)*0.3
	if current_user.price < start_price:
		show_price = start_price
	else:
		show_price = 0
	return render_template('goods/send_order.html',gd=gd,show_price=show_price)


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
		#获取车源信息表 不是之前的获取车辆表了
		dp = Driver_post.query.get_or_404(int(car_id))
		
	except Exception, e:
		abort(403)
	order_str = 'H'+order_str

	op = Order_pay()
	op.order = order_str
	#货物信息表
	op.goods_order_pay = gd
	#车辆信息表
	op.driver_posts_order_pays = dp
	#支付用户 用于判断是否司机或者货主的支付
	op.order_pay_user = current_user
	#因为一辆车有多个用户使用，所以多增加的这个字段用于是当前哪一个用户登录并下单的
	gd.car_goods_user = current_user
	#接单实际
	gd.receive_time = datetime.utcnow()
	gd.state = 1  #1司机已下单
	#dp  Driver_post
	dp.state = 4  #具体字段意思是看models模型设计   4为司机自己寻找货源
	#支付金额
	op.pay_price = Decimal(float(gd.start_price) * 0.3-float(current_user.price))

	
	try:
		db.session.add(op)
		db.session.add(gd)
		db.session.commit()

		#限时支付
		from apscheduler.triggers.interval import IntervalTrigger
		now = datetime.now()
		#年year月mom日day 时hour分min秒seconds
		delta = datime.timedelta(seconds=30)
		n_days = now + delta
		runtime = n_days.strftime('%Y-%m-%d %H:%M:%S')
		db.session.add(Order_Task(order_str=order_str,create_time=datetime.utcnow(),run_time=runtime))
		db.session.commit()
		#添加定时任务
		scheduler.add_job(func=limit_confirm_pay,id=order_str,args=[order_str,],trigger=IntervalTrigger(seconds=30),replace_existing=True)
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
		#获取任务信息,根据单号查询
		ot = Order_Task.query.filter_by(order_str=order_str).first()
		op = Order_pay.query.filter_by(order=ot.order_str).first()
		#如果单号为0未支付，改为-1失效订单  并且更改货源 车源信息的状态
		if op.state==0:
			op.state = -1
			#车源信息状态更改
			op.driver_posts_order_pays.state = 0
			#货物信息
			op.goods_order_pay.state = 0
			db.session.add(op)
		db.session.delete(ot)
		db.session.commit()
	#删除队列任务
	scheduler.delete_job(id=order_str)















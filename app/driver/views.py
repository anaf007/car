#coding=utf-8
"""filename:app/driver/views.py
Created 2017-06-12
Author: by anaf
"""

# from flask import current_app
from  flask.ext.login import login_required,current_user
from ..decorators import goods_required,permission_required,driver_required
from . import driver
from ..models import Permission,Driver,User,Driver_post,Role,Goods,Order_pay,Order_Task
from flask import render_template,request,redirect,url_for,flash,abort
from app import db,scheduler
from datetime import datetime
from forms import Register_driver
from app import redis_store,app
import logging,time,random
from decimal import Decimal
import datetime as datime


#需要登陆，且需要货主权限
@driver.route('/')
@driver.route('/index/')
@login_required
@goods_required
def index():
	#查询时间大于今天，并且状态=0，  这个 filter时间查询花了1个多小时
	dp = Driver_post.query.filter(Driver_post.state==0).filter(Driver_post.start_car_time>datetime.utcnow()).order_by('create_time').all()
	return render_template('driver/index.html',dp=dp)


#注册车辆信息？
@driver.route('/reg_dirver_add',methods=['POST'])
@login_required
@goods_required
def reg_driver_add():
	r_d = request.form.get('driver')
	r_u = request.form.get('user')
	d = Driver.query.get_or_404(int(r_d))
	u = User.query.filter_by(username=r_u).first()
	if d.user.id != current_user.id:
		return u"请勿非法访问"
	if not u:
		return u"没有这个用户。"
	d.use.append(u)
	db.session.add(d)
	db.session.commit()

	return "ok"


#添加源信息
@driver.route('/add_post')
@login_required
def add_post():
	return render_template('driver/add_post.html')


#添加车源信息，此处应该进行系统匹配并发送邮件消息 短信等各种操作
@driver.route('/add_post',methods=['POST'])
@login_required
def add_posts():
	start_sheng = request.form.get('start_sheng')
	start_shi = request.form.get('start_shi')
	start_qu = request.form.get('start_qu')

	end_sheng = request.form.get('end_sheng')
	end_shi = request.form.get('end_shi')
	end_qu = request.form.get('end_qu')

	mon = request.form.get('mon')
	day = request.form.get('day')
	zone = request.form.get('zone')

	yesr = time.strftime('%Y',time.localtime(time.time()))
	timestr = yesr+'/'+mon+'/'+day


	if not start_sheng:
		flash(u'数据校验失败,请选择发车地点','error')
		return redirect(url_for('.add_post'))
	if not end_sheng:
		flash(u'数据校验失败,请选择到达地点','error')
		return redirect(url_for('.add_post'))

	if not start_shi:
		flash(u'数据校验失败,请选择出发城市','error')
		return redirect(url_for('.add_post'))

	if not end_shi:
		flash(u'数据校验失败,请选择目的城市','error')
		return redirect(url_for('.add_post'))

	if current_user.phone=='' or not current_user.phone:
		if request.form.get('phone') =='' or request.form.get('phone') == None:
			flash(u'数据校验失败,请输入手机号码','error')
			return redirect(url_for('.add_post'))




	if start_shi:
		start_address = start_sheng+"-"+start_shi
	if start_qu:
		start_address = start_sheng+"-"+start_shi+"-"+start_qu

	if end_shi:
		end_address = end_sheng+"-"+end_shi
	if end_qu:
		end_address = end_sheng+"-"+end_shi+"-"+end_qu

	carid = request.form.get('car')
	#如果没有验证角色，获取手机号码  更改用户角色
	d = Driver()
	if not carid:
		phone = request.form.get('phone')
		if User.query.filter_by(phone=phone).first():
			flash(u'该手机号码已经被注册，请登录后再发布。','login')
			return redirect(url_for('auth.login'))
		d.users = current_user
		d.phone = phone
		d.number = u'默认车辆'
		d.car_length = u'未知'
		
		d.note = u'默认车辆信息，联系电话'+phone
		d.driver_user = current_user
		d.use.append(current_user)
		r = Role.query.filter_by(name=u'司机').first()
		try:
			db.session.add(d)
			current_user.role =  r
			current_user.phone =  phone
			db.session.add(current_user)
			db.session.commit()
		except Exception, e:
			flash(u'数据错误，添加失败：%s'%str(e),'error')
			db.session.rollback()
			return redirect(url_for('.add_post'))
	else:
		d = Driver.query.get_or_404(int(request.form.get('car')))

	car = d
	starttime = timestr
	price = request.form.get('price')
	note = request.form.get('note')

	gp = Driver_post()
	#标题
	gp.title = '['+start_shi+'-'+end_shi+']'+u'发车时间:'+yesr+'/'+mon+'/'+day+zone
	#发车地址
	gp.start_address = start_address
	gp.start_sheng = start_sheng
	gp.start_shi = start_shi
	gp.start_qu = start_qu
	#目的地址
	gp.end_sheng = end_sheng
	gp.end_shi = end_shi
	gp.end_qu = end_qu
	gp.end_address = end_address
	#备注
	gp.note = note
	#发车时间
	gp.start_car_time = starttime
	#车辆信息
	gp.driverPosts = car
	#报价价格
	gp.start_price = price
	#装车时段
	gp.zone = request.form.get('zone')
	try:
		db.session.add(gp)
		db.session.commit()
		
		flash(u'您的车辆信息发布成功，系统自动进行信息匹配，匹配成功后会短信通知您，请稍后。','success')
		#添加定时操作
		return redirect(url_for('.add_post'))

	except Exception, e:
		db.session.rollback()
		
		flash(u'添加失败%s'%str(e),'error')

	
	return redirect(url_for('.add_post'))



@driver.route('/show_post/<int:id>')
@goods_required
def show_post(id=0):
	dp = Driver_post.query.get_or_404(id)
	return render_template('driver/show_post.html',dp = dp)


#注册司机
@driver.route('/register_driver',methods=['GET'])
def register_driver():
	form = Register_driver()
	return render_template('driver/register_driver.html',form=form)

#注册司机
@driver.route('/register_driver',methods=['POST'])
def register_driver_post():
	form = Register_driver()
	if form.validate_on_submit():
		d = Driver()
		d.users = current_user
		d.phone = form.phone.data
		d.length = form.length.data
		d.number = form.number.data
		d.travel = form.travel.data
		d.driver = form.driver.data
		d.note = form.note.data
		d.driver_user = current_user
		d.use.append(current_user)
		r = Role.query.filter_by(name=u'司机').first()
		try:
			db.session.add(d)
			current_user.role =  r
			db.session.add(current_user)
			db.session.commit()
			flash(u'车主添加完毕')
		except Exception, e:
			flash(u'数据错误，添加失败：%s'%str(e))
			db.session.rollback()
		

		flash(u'申请司机完成。')
		return redirect(url_for('usercenter.index'))
	else:
		flash(u'校验数据错误')
	return redirect(url_for('.register_driver'))

#接车下单货主访问
@driver.route('/send_order',methods=['POST'])
@login_required
@goods_required
def send_order():
	id = request.form.get('id')
	try:
		dp = Driver_post.query.get_or_404(int(id))
	except Exception, e:
		abort(403)
	return render_template('driver/send_order.html',dp=dp)


#确认接车下单货主访问
#这里是货主下单过程  需要限时支付，需要到缓存机制
@driver.route('/confirm_order',methods=['POST'])
@login_required
@goods_required
def confirm_order():

	#车源id
	req_id = request.form.get('id')
	goods_id = request.form.get('goods')
	choice_str = 'ABCDEFGHJKLNMPQRSTUVWSXYZ'
	order_str = ''
	str_time =  time.time()
	order_str = str(int(int(str_time)*1.347))+order_str
	
	for i in range(9):
		order_str += random.choice(choice_str)
	try:
		dp = Driver_post.query.get_or_404(int(req_id))
		goodsid = Goods.query.get_or_404(int(goods_id))
	except Exception, e:
		abort(403)
	order_str = 'C'+order_str

	op = Order_pay()
	op.order = order_str
	#货物信息
	op.goods_order_pay = goodsid 
	#车源信息
	op.driver_posts_order_pays = dp 
	#付款者
	op.order_pay_user = current_user 
	# dp.car_goods = current_user
	#创建时间
	dp.receive_time = datetime.utcnow()
	#1货主已下单
	dp.state = 1  
	#具体字段意思是看models模型设计   4为货主自己寻找货源
	goodsid.state = 4

	#支付金额
	op.pay_price = Decimal(float(dp.start_price) * 1-float(current_user.price))
	
	
	try:
		db.session.add(op)
		db.session.add(dp)
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
		
		#此处应该是跳转到支付页面url_for
	except Exception, e:
		return 'error:%s'%str(e)
	return redirect(url_for('driver.index'))



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
			#订单
			op.state = -1
			#车源信息 状态更改
			op.driver_posts_order_pays.state = 0
			#货源信息 状态更改
			op.goods_order_pay.state = 0
			
			db.session.add(op)
		db.session.delete(ot)
		db.session.commit()
	#删除队列任务
	scheduler.delete_job(id=order_str)



#coding=utf-8

from . import superadmin
from flask import render_template,flash,redirect,url_for,request,abort,Response
from flask_login import current_user
from app.models import *
from datetime import datetime
from ..decorators import *
from ..fck import authSendGoods
from ..errorSendMail import send_email
from app import db,flask_wechat,scheduler
import time,random,xlwt,StringIO,psutil
from decimal import Decimal
from sqlalchemy import text, create_engine, MetaData, Table, Column, String, Integer
from sqlalchemy.orm import sessionmaker
import datetime as datetimes
from apscheduler.triggers.interval import IntervalTrigger

import sys
reload(sys)
sys.setdefaultencoding('utf8')

@superadmin.route('/')
@superadmin.route('/index')
@admin_required
def index():
        print request.url
	
	cpu = psutil.cpu_times()
	mem = psutil.virtual_memory()
	disk = psutil.disk_usage('/')
	return render_template('superadmin/index.html',cpu=cpu,mem=mem,disk=disk,psutil=psutil)

#用户消息
@superadmin.route('/all_user_message')
@admin_required
def all_user_message():
	return render_template('superadmin/all_user_message.html')

#货物预约列表
@superadmin.route('/make_goods')
@admin_required
def make_goods():
	#获取货物信息 发车时间大于当前时间并按照装货时间顺时排序
	goods = Goods.query.filter((Goods.state==1)|(Goods.state==0)).filter(Goods.start_car_time>datetime.now()).order_by('state,start_car_time').all()
	return render_template('superadmin/make_goods.html',goods=goods)

#更改状态 是否在线支付
@superadmin.route('/change_online_pirce/<int:goodsid>')
@admin_required
def change_online_pirce(goodsid=0):
	gd = Goods.query.get_or_404(goodsid)
	if gd.state ==0 :
		if gd.online_pirce == 0:
			gd.online_pirce = 1
		else:
			gd.online_pirce = 0
		db.session.add(gd)
		db.session.commit()
	return redirect(url_for('superadmin.make_goods_show',id=goodsid))


#货物详细预约信息
@superadmin.route('/make_goods_show')
@superadmin.route('/make_goods_show/<int:id>')
@admin_required
def make_goods_show(id=0):
	goods = Goods.query.get_or_404(id)
	return render_template('superadmin/make_goods_show.html',goods=goods)


#司机不同意接单。
@superadmin.route('/make_goods_no')
@superadmin.route('/make_goods_no/<int:goodsid>/<int:driverid>/<int:confirmid>')
@admin_required
def make_goods_no(goodsid=0,driverid=0,confirmid=0):
	#货物
	goods = Goods.query.get_or_404(goodsid);
	#车辆
	driver = Driver.query.get_or_404(driverid);
	#司机自助下单信息
	dso = Driver_self_order.query.get_or_404(confirmid)	
	#自主预约 状态为2 放弃接单
	dso.state =2
	try:
		db.session.add(dso)
		db.session.commit()
	except Exception, e:
		db.session.rollback()
	return redirect(url_for('superadmin.make_goods_show',id=goods.id))

#撤回司机接单申请
@superadmin.route('/make_goods_repeal')
@superadmin.route('/make_goods_repeal/<int:goodsid>/<int:confirmid>')
@admin_required
def make_goods_repeal(goodsid=0,confirmid=1):
	gsq = Goods.query.get_or_404(goodsid)
	dso = Driver_self_order.query.get_or_404(confirmid)
	gsq.state = 0 
	gsq.end_price = ''
	dso.state = 0 
	db.session.add(gsq)
	db.session.add(dso)
	op = Order_pay.query.filter_by(goodsed=gsq).all()
	for i in op:
		db.session.delete(i)
	db.session.commit()
	return redirect(url_for('superadmin.make_goods_show',id=goodsid))





#确认用户  确认用户后将添加支付信息 ，消息通知信息
#此处应该做账户登记验证
@superadmin.route('/make_goods_comfirm')
@superadmin.route('/make_goods_comfirm/<int:goodsid>/<int:driverid>/<int:confirmid>/<price>')
@admin_required
def make_goods_comfirm(goodsid=0,driverid=0,confirmid=0,price='0.00'):

	#货物
	gd = Goods.query.get_or_404(goodsid);
	#车辆
	driver = Driver.query.get_or_404(driverid);
	#司机自助下单信息
	dso = Driver_self_order.query.get_or_404(confirmid)	
	if dso.state ==1:
		flash(u'该信息已经确认了承运司机，请不要重复确认。','error')
		return redirect(url_for('superadmin.index'))

	#不允许有未支付的订单
	if Order_pay.query.filter(Order_pay.state==0).filter(Order_pay.user==dso.driver.user).first():
		flash(u'该司机目前还有承运信息未支付，需要支付或取消后才能重新接单。','error')
		return redirect(url_for('superadmin.make_goods_show',id=gd.id))
	if Order_pay.query.filter(Order_pay.state==0).filter(Order_pay.user==dso.goodsed.consignor.user).first():
		flash(u'该货主目前还有货运信息未支付，需要支付或取消后才能继续操作。','error')
		return redirect(url_for('superadmin.make_goods_show',id=gd.id))
	#此处应该做判断是否非法访问

	dso.state = 1
	gd.state = 1
	#司机确认的运费,货主同意
	gd.end_price = dso.price
	db.session.add(dso)
	db.session.add(gd)
	
	
	#以上修改货物状态，以下添加支付订单信息

	choice_str = '23456789ABCDEFGHJKLNMPQRSTUVWSXYZ'
	order_str = ''
	str_time =  time.time()
	order_str = str(int(int(str_time)*1.347))+order_str
	for i in range(9):
		order_str += random.choice(choice_str)
	
	siji_order_str = 'C'+order_str

	#司机订单
	opdriver = Order_pay()
	opdriver.order = siji_order_str
	#货物信息表
	opdriver.goodsed = gd
	#车辆表
	opdriver.driver = driver
	#支付用户 用于判断是否司机或者货主的支付
	# opdriver.order_pay_user = current_user
	#因为一辆车有多个用户使用，所以多增加的这个字段用于是当前哪一个用户登录并下单的
	#
	#车辆用户  #如果一辆车有多个用户呢？ 或者车队 将报错？
	opdriver.user = driver.user
	#接单时间
	gd.receive_time = datetime.utcnow()
	gd.state = 1  #1司机已接单
	driverprice = "%.2f" % (float(price) * 1)
	# print Decimal(float(price) * 0.3-float(current_user.price)).prec(2)
	#订单支付金额
	opdriver.pay_price = Decimal(driverprice)

	# um = User_msg()
	# um.title = u'您有一条货物定金支付信息'
	# um.body = u'您已经确认了承载【%s】的货物，<a href="/sijizhifu/">点击查看详情</a>。'%(gd.start_shi+'-'+gd.end_shi)
	# um.state = 0
	# um.user = driver.user

	
	opgoodsed = Order_pay()
	opgoodsed.order = 'H'+order_str
	opgoodsed.goodsed = gd
	opgoodsed.driver = driver
	opgoodsed.user = gd.consignor.user
		#货主在线支付
	if gd.online_pirce ==1:

		opgoodsed.pay_price = Decimal("%.2f" % (float(dso.price) * 1))

		# umgd = User_msg()
		# umgd.title = u'您有货物已确认承运。'
		# umgd.body = u'您已经确认了车辆承载您的货物，<a href="/huozhuzhifu/">点击在线支付运费</a>。线上支付更安全，并可查看车辆位置信息。'
		# umgd.state = 0
		# umgd.user = gd.consignor.user
		
		
		try:
			flask_wechat.message.send_text(gd.consignor.user.wx_open_id,u'您已经确认了车辆承载您的货物，<a href="http://car.anaf.cn/huozhuzhifu/">点击在线支付运费</a>。线上支付更安全，并可查看车辆位置信息。')
		except Exception, e:
			send_email(u'用户：%s 。预约货物微信通知用户错误：%s'%(gd.consignor.user.phone,str(e)))
		
		
	else:
		try:
			opgoodsed.pay_price = Decimal("%.2f" % (float(0.00) * 1))
			opgoodsed.state = 2
			opgoodsed.goodsed.state = 2
			opgoodsed.goodsed.price_is_pay = 1
			db.session.add(opgoodsed)
			flask_wechat.message.send_text(gd.consignor.user.wx_open_id,u'系统已经验证确认了司机身份信息，请等待司机确认订单信息。')
		except Exception, e:
			send_email(u'用户：%s 。预约货物微信通知用户错误：%s'%(gd.consignor.user.phone,str(e)))
	
	try:
		flask_wechat.message.send_text(driver.user.wx_open_id,u'您已经确认了承载【%s】的货物，<a href="http://car.anaf.cn/sijizhifu/">点击查看详情</a>。'%(gd.start_shi+'-'+gd.end_shi))
	except Exception, e:
		send_email(u'用户：%s 。预约货物微信通知用户错误：%s'%(driver.user.phone,str(e)))
	
	try:

		db.session.add(opdriver)
		
		db.session.commit()
	except Exception, e:
		return 'error:%s'%str(e)
		
	return redirect(url_for('superadmin.make_goods'))




#所有货物信息
@superadmin.route('/all_goods',methods=['GET'])
@admin_required
def all_goods():
	page = Goods.query.order_by(Goods.id.desc()).paginate(1,20,False)
	return render_template('superadmin/all_goods.html',page=page,gd=page.items)

@superadmin.route('/all_goods',methods=['POST'])
@admin_required
def all_goods_post():
	goodsid = request.form.get('goodsid')
	start_address= request.form.get('start_address')
	end_address = request.form.get('end_address')
	low_price = request.form.get('low_price')
	height_price = request.form.get('height_price')
	start_car_time = request.form.get('start_car_time')
	pay_type = request.form.get('pay_type')

	if not start_address:
		start_address = ''
	if not end_address:
		end_address = ''
	
	
	if goodsid:
		gd = Goods.query.filter_by(id=goodsid).all()
		page= []

		return render_template('superadmin/all_goods.html',page=page,gd=gd)
	if not goodsid and not start_address and not end_address and not low_price and not height_price and not pay_type and not start_car_time:
		return redirect(url_for('superadmin.all_goods'))

	if not start_car_time:
		start_car_time = '2016-10-01'
	if not low_price:
		low_price = 0
	if not height_price:
		height_price = 1000000
	if not pay_type:
		pay_type = '0,1'
	
	
	selectsql = """select * from goods where start_xiangxi_address like "%{}%" and end_xiangxi_address like "%{}%" and start_price > {} and start_price < {} and start_car_time > "{}" and online_pirce in ({}) order by id desc""".format(start_address,end_address,low_price,\
		height_price,start_car_time,pay_type)
	gdall = db.engine.execute(text(selectsql))
	

	page = []
	gd = []
	for i in gdall.fetchall():
		gd.append(i)

	return render_template('superadmin/all_goods.html',page=page,gd=gd)


#手动添加  自动更新货物信息任务  用于关闭服务器再次开启的时候
#一般情况都是 发车时间大于当前时间
#因为一到发车时间只要装车了 定时任务都会被删除
@superadmin.route('/start_scheduler_task')
@admin_required
def start_scheduler_task():
	st = Scheduler_task.query.all()
	sice = 1
	for i in st:
		scheduler.add_job(func=authSendGoods,id=i.func_id,args=[i.args,],trigger=IntervalTrigger(seconds=sice),replace_existing=True)
		sice  +=  10
		# if i.create_time <= datetime.now():
		# 	scheduler.add_job(func=authSendGoods,id=i.func_id,args=[i.args,],trigger=IntervalTrigger(seconds=10),replace_existing=True)
		# else:
		# 	seconds =  (datetime.strptime(str(i.create_time),"%Y-%m-%d %H:%M:%S")-datetimes.datetime.now()).seconds 
		# 	scheduler.add_job(func=authSendGoods,id=i.func_id,args=[i.args,],trigger=IntervalTrigger(seconds=seconds),replace_existing=True)
	return redirect(url_for('superadmin.all_scheduler'))

#所有用户位置
@superadmin.route('/all_user_position',methods=['GET'])
@admin_required
def all_user_position():
	page = Position.query.order_by(Position.id.desc()).paginate(1,100,False)
	return render_template('superadmin/all_user_position.html',pos=page.items,page=page)

#所有用户信息
@superadmin.route('/all_user_info',methods=['GET'])
@admin_required
def all_user_info():
	page = User.query.order_by(User.id.desc()).paginate(1,100,False)
	return render_template('superadmin/all_user_info.html',info=page.items,page=page)

#删除用户
@superadmin.route('/del_user/<int:id>',methods=['GET'])
@admin_required
def del_user(id=0):
	u = User.query.get_or_404(id)
	if not u.username == current_app.config['SUPERADMIN_NAME']:
		db.session.delete(u)
		db.session.commit()
	return redirect(url_for('.all_user_info'))





#所有公司信息
@superadmin.route('/all_company',methods=['GET'])
@admin_required
def all_company():
	page = Consignor.query.order_by(Consignor.id.desc()).paginate(1,100,False)
	return render_template('superadmin/all_company.html',info=page.items,page=page)


@superadmin.route('/del_company/<int:id>',methods=['GET'])
@admin_required
def del_company(id=0):
	try:
		cs = Consignor.query.get(id)
		db.session.delete(cs)
		if cs.user:
			db.session.delete(cs.user)
		db.session.commit()
	except Exception, e:
		pass
	
	return redirect(url_for('.all_company'))

@superadmin.route('/del_goods/<int:id>',methods=['GET'])
@admin_required
def del_goods(id=0):
	try:
		db.session.delete(Goods.query.get(id))
		db.session.commit()
	except Exception, e:
		pass
	
	return redirect(url_for('.all_goods'))


@superadmin.route('/show_company/<int:id>',methods=['GET'])
@admin_required
def show_company(id=0):
	try:
		return render_template('superadmin/show_company.html',company=Consignor.query.get(id))
	except Exception, e:
		return redirect(url_for('.all_company'))

#不通过
@superadmin.route('/forbid_company/<int:id>',methods=['GET'])
@admin_required
def forbid_company(id=0):
	try:
		cs = Consignor.query.get(id)
		cs.state = 0
		db.session.add(cs)
		
		csimg =Consignor_images.query.filter_by(consignor=current_user.consignors).all()
		for i in csimg:
			db.session.delete(i)
		db.session.commit()
		try:
			flask_wechat.message.send_text(gd.consignor.user.wx_open_id,u'您申请的资料不通过审核，请重新申请。')
		except Exception, e:
			pass
		return redirect(url_for('.all_company'))
	except Exception, e:
		return redirect(url_for('.all_company'))

#撤销
@superadmin.route('/repeal_company/<int:id>',methods=['GET'])
@admin_required
def repeal_company(id=0):
	try:
		cs = Consignor.query.get(id)
		cs.state = 0 
		db.session.add(cs)
		csimg =Consignor_images.query.filter_by(consignor=current_user.consignors).all()
		for i in csimg:
			db.session.delete(i)
		db.session.commit()
		try:
			flask_wechat.message.send_text(gd.consignor.user.wx_open_id,u'您申请的资料不通过审核，请重新申请。')
		except Exception, e:
			pass
		return redirect(url_for('.all_company'))
	except Exception, e:
		return redirect(url_for('.all_company'))

#通过审核
@superadmin.route('/finish_company/<int:id>',methods=['GET'])
@admin_required
def finish_company(id=0):
	try:
		cs = Consignor.query.get(id)
		cs.state = 2
		cs.user.user_infos.info_level = 2
		db.session.add(cs)
		db.session.commit()
		try:
			flask_wechat.message.send_text(gd.consignor.user.wx_open_id,u'您申请的资料已通过审核。')
		except Exception, e:
			pass
		return redirect(url_for('.all_company'))
	except Exception, e:
		return redirect(url_for('.all_company'))	
	

#所有定时任务
@superadmin.route('/all_scheduler',methods=['GET'])
@admin_required
def all_scheduler():
	return render_template('superadmin/all_scheduler.html',\
		sqlsch=Scheduler_task.query.all(),job=scheduler.get_jobs())


@superadmin.route('/del_postion/<int:id>',methods=['GET'])
@admin_required
def del_postion(id=0):
	try:
		pos = Position.query.get(id)
		db.session.delete(pos)
		db.session.commit()
	except Exception, e:
		pass
	
	return redirect(url_for('.all_user_position'))



#所有车辆信息
@superadmin.route('/all_driver',methods=['GET'])
@admin_required
def all_driver():
	page = Driver.query.order_by(Driver.id.desc()).paginate(1,100,False)
	return render_template('superadmin/all_driver.html',info=page.items,page=page)


#所有车运信息
@superadmin.route('/all_driver_post',methods=['GET'])
@admin_required
def all_driver_post():
	page = Driver_post.query.order_by(Driver_post.id.desc()).paginate(1,100,False)
	return render_template('superadmin/all_driver_post.html',info=page.items,page=page)


#车运预约信息
@superadmin.route('/mark_driver_post',methods=['GET'])
@admin_required
def mark_driver_post():
	page = Driver_post.query.order_by(Driver_post.id.desc()).paginate(1,100,False)
	return render_template('superadmin/mark_driver_post.html',info=page.items,page=page)


#显示车辆信息
@superadmin.route('/show_driver/<int:id>',methods=['GET'])
@admin_required
def show_driver(id=0):
	try:
		return render_template('superadmin/show_driver.html',d=Driver.query.get(id))
	except Exception, e:
				return redirect(url_for('.all_driver'))


#验证通过  车辆信息
@superadmin.route('/finish_driver/<int:id>',methods=['GET'])
@admin_required
def finish_driver(id=0):
	try:
		cs = Driver.query.get(id)
		cs.state = 2
		cs.user.user_infos.info_level = 2
		db.session.add(cs)
		db.session.commit()
		try:
			flask_wechat.message.send_text(gd.consignor.user.wx_open_id,u'您申请的资料已通过审核。')
		except Exception, e:
			pass
		return redirect(url_for('.all_driver'))
	except Exception, e:
		return redirect(url_for('.all_driver'))




#验证不通过 车辆信息
@superadmin.route('/forbid_driver/<int:id>',methods=['GET'])
@admin_required
def forbid_driver(id=0):
	try:
		cs = Driver.query.get(id)
		cs.state = 0
		db.session.add(cs)
		
		csimg =Driver_images.query.filter_by(driver=current_user.drivers).all()
		for i in csimg:
			db.session.delete(i)
		db.session.commit()
		try:
			flask_wechat.message.send_text(gd.consignor.user.wx_open_id,u'您申请的资料不通过审核，请重新申请。')
		except Exception, e:
			pass
		return redirect(url_for('.all_driver'))
	except Exception, e:
		return redirect(url_for('.all_driver'))






#删除车辆信息
@superadmin.route('/del_driver/<int:id>',methods=['GET'])
@admin_required
def del_driver(id=0):
	try:
		dr = Driver.query.get(id)
		db.session.delete(dr)
		number = dr.number
		db.session.commit()
		flash(u'删除车辆信息（%s）成功，'%number,'success')
	except Exception, e:
		flash(u'删除车辆信息失败:%s'%str(e),'error')
	
	return redirect(url_for('.all_driver'))


#删除车辆信息
@superadmin.route('/del_driver_post/<int:id>',methods=['GET'])
@admin_required
def del_driver_post(id=0):
	try:
		dr = Driver_post.query.get(id)
		db.session.delete(dr)
		db.session.commit()
		flash(u'删除车运信息成功，','success')
	except Exception, e:
		flash(u'删除车运信息失败:%s'%str(e),'error')
	
	return redirect(url_for('.all_driver_post'))

@superadmin.route('/all_driver_post',methods=['POST'])
def all_driver_post_p():
	dp = Driver_post.query

	start_address= request.form.get('start_address')
	end_address = request.form.get('end_address')
	low_price = request.form.get('low_price')
	height_price = request.form.get('height_price')
	
	
	if  not start_address and not end_address and not low_price and not height_price :
		return redirect(url_for('superadmin.all_driver_post'))

	start_address = "%"+start_address+"%"
	end_address = "%"+end_address+"%"

	if start_address:
		dp = dp.filter(Driver_post.start_address.like(start_address))
	if end_address:
		dp = dp.filter(Driver_post.end_address.like(end_address))
	if low_price:
		dp = dp.filter_by(start_price>=low_price)
	if height_price:
		dp = dp.filter_by(start_price<=low_price)
	

	dp = dp.all()
	
	# selectsql = """select * from driver_posts where start_address like "%{}%" and end_address like "%{}%" and start_price > {} and start_price < {} order by id desc""".format(start_address,end_address,low_price,height_price)
	# gdall = db.engine.execute(text(selectsql))
	

	page = []

	return render_template('superadmin/all_driver_post.html',page=page,info=dp)



@superadmin.route('/make_driver_post_show/<int:id>',methods=['GET'])
@admin_required
def make_driver_post_show(id=0):
	dp = Driver_post.query.get_or_404(id)
	return render_template('superadmin/make_driver_post_show.html',dp=dp)


@superadmin.route('/all_order_pay')
@admin_required
def all_order_pay():
	page = Order_pay.query.order_by(Order_pay.id.desc()).paginate(1,20,False)
	return render_template('superadmin/all_order_pay.html',page=page,info=page.items)


@superadmin.route('/all_tixian')
@admin_required
def all_tixian():
	page = Tixianchengqing.query.order_by(Tixianchengqing.id.desc()).paginate(1,20,False)
	return render_template('superadmin/all_tixian.html',page=page,info=page.items)


@superadmin.route('/send_apay/<int:id>')
@admin_required
def send_apay(id=0):
	try:
		tixian = Tixianchengqing.query.get_or_404(id)
		tixian.state = 1
		db.session.add(tixian)
		db.session.commit()
	except Exception, e:
		pass

	return redirect(url_for('.all_tixian'))
		



@superadmin.route('/finsh_apay/<int:id>')
@admin_required
def finsh_apay(id=0):
	try:
		tixian = Tixianchengqing.query.get_or_404(id)
		tixian.state = 2
		tixian.caozuoyuan_id = current_user.phone
		tixian.finish_time = datetimes.datetime.now()
		db.session.add(tixian)
		db.session.commit()
	except Exception, e:
		pass

	return redirect(url_for('.all_tixian'))



@superadmin.route('/toexcel_apay')
@admin_required
def toexcel_apay(id=0):
	tx = Tixianchengqing.query.filter_by(state=1).all()
	wb = xlwt.Workbook(encoding='utf8')
	shijian = datetimes.datetime.now()
	ws = wb.add_sheet(u'出库表数据')
	title_shipment = [u'编号',u'联系号码',u'打款金额',u'申请时间',u'开户银行',u'开户地',u'卡号',u'备注']
	for i,x in enumerate(title_shipment):
		ws.write(0,i,x)
	for i,x in enumerate(tx):
		ws.write(i+1,0,x.id)
		ws.write(i+1,1,x.user.phone)
		ws.write(i+1,2,x.price)
		ws.write(i+1,3,x.create_time)
		ws.write(i+1,4,x.user.user_infos.suoshuyinhang)
		ws.write(i+1,5,x.user.user_infos.kaihuhang)
		ws.write(i+1,6,x.user.user_infos.kahao)

	filename = str(shijian)+'.xls'
	output = StringIO.StringIO()
	wb.save(output)
	response = Response()
	response.data = output.getvalue()
	# response = make_response(wb.save())
	response.headers['Charset'] = 'UTF-8;'
	response.headers["Content-Disposition"] = "attachment; filename=%s;"%filename
	return response


@superadmin.route('/del_scheduler/<int:id>')
@admin_required
def del_scheduler(id=0):
	st = Scheduler_task.query.get_or_404(id)
	db.session.delete(st)
	db.session.commit()
	return redirect(url_for('.all_scheduler'))

#微信素材
@superadmin.route('/wx_materia',methods=['GET'])
@admin_required
def wx_materia():
	try:
		sucaifile = flask_wechat.material.batchget('image')

	except Exception, e:
		print str(3)
		sucaifile = []
	return render_template('superadmin/wx_materia.html',sucaifile=sucaifile)

@superadmin.route('/wx_materia',methods=['POST'])
@admin_required
def wx_materia_post():
	try:
		sucaifile = request.files['sucaifile']
		if sucaifile:
			try:
				flask_wechat.material.add(media_type='image', media_file=(sucaifile.filename, sucaifile, 'image/jpeg'))			
			except Exception, e:
				send_email(u'微信接口素材图片上传错误：%s'%str(e))

	except Exception, e:
		print str(e)
	
	return redirect(url_for('.wx_materia'))








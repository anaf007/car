#coding=utf-8
"""filename:app/goods/views.py
Created 2017-06-15
Author: by anaf
note:货源信息栏目，首页货物显示及某些司机看的页面，只能司机访问，所以是 @permission_required(Permission.DRIVER)

"""

from . import goods
from flask import render_template,flash,redirect,url_for,request,abort,current_app
from  flask_login import login_required,current_user
from ..errorSendMail import send_email
from ..fck import authSendGoods
from ..decorators import goods_required,driver_required
from app.models import *
from .forms import GoodsForm
from app import db,scheduler,app,flask_wechat
import random,time
from datetime import datetime
from decimal import Decimal
# from app import redis_store
import logging,os,urllib2
import datetime as datime
from apscheduler.triggers.interval import IntervalTrigger

import sys
reload(sys)
sys.setdefaultencoding('utf8')

@goods.route('/')
@goods.route('/index')
@goods.route('/index/')
@login_required
#只能司机查看首页的货物信息
def index():
	#查询发车时间大于当前时间
	# for i in Goods.query.all():
	# 	db.session.delete(i)
	# db.session.commit()
	# for i in Position.query.all():
	# 	db.session.delete(i)
	# db.session.commit()
	# send_email(u'ceshi')

	#这里应该获取司机最新定位
	try:
		pos = Position.query.filter_by(user=current_user).order_by(Position.id.desc()).first()
		url = "http://restapi.amap.com/v3/geocode/regeo?key=5e1b3e64caf0d25eb6bca46848269bf9&location=%s,%s&radius=1000&extensions=all&batch=false&roadlevel=0"%(pos.longitude,pos.latitude)
		response = urllib2.Request(url = url)
		addr = urllib2.urlopen(response).read()
		addr = eval(addr)
		sheng = addr['regeocode']['addressComponent']['province'].encoding('utf-8')
		shi = addr['regeocode']['addressComponent']['city'].encoding('utf-8')
		dangqian = Goods.query.filter(Goods.state==0).filter(Goods.start_shi.like(shi)).filter(Goods.start_car_time>=datetime.utcnow()).order_by(Goods.create_time.desc()).paginate(1,50,False)
		fujin = Goods.query.filter(Goods.state==0).filter(Goods.start_sheng.like(sheng)).filter(Goods.start_car_time>=datetime.utcnow()).order_by(Goods.create_time.desc()).paginate(1,30,False)
		return render_template('goods/index.html',dangqian=dangqian,fujin=fujin)
	except Exception, e:
		dangqian = Goods.query.filter(Goods.state==0).filter(Goods.start_car_time>=datetime.utcnow()).order_by('create_time desc').paginate(1,50,False)
		
		return render_template('goods/index.html',dangqian=dangqian,fujin=[])
	


	


@goods.route('/deleteAuthSendGoods')
@goods_required
def deleteAuthSendGoods():
	return ''


@goods.route('/send_goods')
@login_required
#发布货源信息
def send_goods():

	carinfo = Car_Info.query.order_by(Car_Info.sort).all()
	cartype = Car_Type.query.all()
	try:
		pos = Position.query.filter_by(user=current_user).order_by(Position.id.desc()).first()
		url = "http://restapi.amap.com/v3/geocode/regeo?key=5e1b3e64caf0d25eb6bca46848269bf9&location=%s,%s&radius=1000&extensions=all&batch=false&roadlevel=0"%(pos.longitude,pos.latitude)
		response = urllib2.Request(url = url)
		addr = urllib2.urlopen(response).read()
		addr = eval(addr)
			
		try:
			sheng = addr['regeocode']['addressComponent']['province']
			shi = addr['regeocode']['addressComponent']['city']
			qu = addr['regeocode']['addressComponent']['district']	
			jie = addr['regeocode']['addressComponent']['township']
			jie = jie + addr['regeocode']['addressComponent']['streetNumber']['street']
			jie = jie + addr['regeocode']['addressComponent']['streetNumber']['number']
		except Exception, e:
			pass	
			# send_email(u'用户：%s 。发送货物信息地址定位错误：%s'%(current_user.phone,str(e)))
		
		
		return render_template('goods/send_goods.html',carinfo = carinfo,\
			cartype=cartype,addr=addr,sheng=sheng,shi=shi,qu=qu,jie=jie)
	except Exception, e:
		# send_email(u'用户：%s 。发送货物信息错误：%s'%(current_user.phone,str(e)))
		return render_template('goods/send_goods.html',carinfo=carinfo,cartype=cartype)
	


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



	if current_user.phone=='' or not current_user.phone:
		if request.form.get('phone') =='' or request.form.get('phone') == None:
			flash(u'请输入您的手机号码.','error')
			return redirect(url_for('.send_goods'))

	yesr = time.strftime('%Y',time.localtime(time.time()))
	timestr = yesr+'-'+mon+'-'+day
	consignor = Consignor()

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
	hms = ''
	if zone==u'全天':
		good.start_car_time = timestr+' 22:29:59 '
	if zone==u'上午':
		good.start_car_time = timestr+' 07:59:59 '
	if zone==u'下午':
		good.start_car_time = timestr+' 13:59:59 '
	if zone==u'晚上':
		good.start_car_time = timestr+' 19:59:59 '
	
	#装车时段
	good.start_zone = zone
	#备注
	good.note = request.form.get('note')
	#报价运费
	price = request.form.get('price')
	if not price:
		flash(u'请输入预约价格.','error')
		return redirect(url_for('.send_goods'))
	good.start_price = price
	#状态0刚发布信息
	good.state = 0

	zhengche = request.form.get('zhengche')
	pingche = request.form.get('pingche')

	good.name = u'普货'
	good.select_car_type = '整车'
	good.car_type = '无要求'
	good.car_length = ''
	good.tiji = ''
	good.zhongliang = ''

	if zhengche:
		good.name = request.form.get('zhengche')
		good.select_car_type = u'整车'
		good.car_type = request.form.get('chexing',u'未知')
		chechang = request.form.get('chechang',u'未知,未知,未知')
		chechang = chechang.split(',')
		good.car_length = chechang[0]
		good.tiji = chechang[1]
		good.zhongliang = chechang[2]
	if pingche:
		good.name = request.form.get('pingche')
		good.select_car_type = u'拼车'
		good.car_length = u'拼车'
		good.car_type = u'拼车'
		good.tiji = request.form.get('tiji','')
		good.zhongliang = request.form.get('zhongliang','')

	#没有货主的公司先系统默认注册一个公司
	if not current_user.consignors:
		phone = request.form.get('phone')
		if User.query.filter_by(phone=phone).first():
			flash(u'该手机号码已经被注册，请用微信关联手机号后再发布。','login')
			return redirect(url_for('auth.login'))

		consignor.user = current_user
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
			send_email(u'用户：%s 。货主确认发货添加公司信息错误：%s'%(current_user.phone,str(e)))
			return redirect(url_for('.send_goods'))

	#更新下单次数
	current_user.user_infos.order_times = current_user.user_infos.order_times+1

	#外键货主表货主表
	good.consignor = current_user.consignors
	try:
		db.session.add(good)
		db.session.add(current_user)
		db.session.commit()
		flash(u'货物信息发布成功，系统自动进行信息匹配，匹配成功后将会通知您，请稍后。','success')
		#信息：出发省市 抵达省市 start_sheng start_shi end_sheng end_shi
		#获取发运表  获取 预约表得到 司机常跑 路线  推送微信消息
		adr = "["+start_sheng+"-"+end_sheng+"]"
		try:
			#发送过车运信息的
			# senddp = Driver_post.query.filter(Driver_post.start_sheng.like(start_sheng))\
			# 	.filter(Driver_post.end_sheng.like(end_sheng)).group_by('driver_id').all()
			
			# for i in senddp:
			# 	flask_wechat.message.send_text(i.driver.user.wx_open_id,\
			# 		u'%s有了新的货物信息，<a href="http://car.anaf.cn/consignor/show_goods/%s">点击查看货物信息。</a>'%(adr,good.id))
			#预约过货物信息的车辆
			dso = Driver_self_order.query.join(Goods).filter(Goods.start_sheng.like(start_sheng))\
				.filter(Goods.end_sheng.like(end_sheng)).group_by('driver_id').all()
			for i in dso:
				try:
					flask_wechat.message.send_text(i.driver.user.wx_open_id,\
						u'%s有了新的货物信息，回复“hw%s”查看货物信息链接。'%(adr,good.id))
				except Exception, e:
					send_email(u'用户：%s 。发送货物微信通知用户错误：%s'%(current_user.phone,str(e)))
		
					
			#定时任务,获取发车时间和当前发布时间差 秒数  添加定时任务
			# a = datime.datetime.now()
			# seconds =  (datetime.strptime(str(good.start_car_time),"%Y-%m-%d %H:%M:%S")-a).seconds 
			# if zone ==u'全天':
				# seconds = seconds-43200  #中午12点
			jobid = str(good.consignor.id) +':::'+str(good.id)
			scheduler.add_job(func=authSendGoods,id=jobid,args=[good.id,],trigger=IntervalTrigger(seconds=30),replace_existing=True)
			
			st = Scheduler_task()
			st.func_id = jobid
			st.func = authSendGoods
			st.args = good.id
			st.create_time = good.start_car_time 
			db.session.add(st)
			db.session.commit()


			# scheduler.add_job(func=authSendGoods,id=jobid,args=[good,],trigger=IntervalTrigger(seconds=seconds),replace_existing=True)
		except Exception, e:
			send_email(u'用户：%s 。发送货物提交信息错误：%s'%(current_user.phone,str(e)))
		

	except Exception, e:
		db.session.rollback()
		flash(u'发布失败，数据校验失败。','error')
		send_email(u'用户：%s 。发送货物提交信息错误，最外层：%s'%(current_user.phone,str(e)))
	
		
	return redirect(url_for('main.index'))




#显示货物信息，司机访问
@goods.route('/show_goods')
@goods.route('/show_goods/<int:id>')
@login_required
def show_goods(id=0):
	if current_user.role.name==u'货主':
		flash(u'您是货主不能查看货物详情。','error')
		return redirect(url_for('main.index'))
	gd = Goods.query.get(id)
	if not gd:
		flash(u'该货物信息已被删除或不存在。','error')
		return redirect(url_for('main.index'))

	if gd.start_car_time<datetime.utcnow():
		flash(u'发车时间不能小于当前时间，该信息已过期！','error')
		return redirect(url_for('main.index'))
	print gd

	return render_template('goods/show_goods.html',gd = gd)


#修改货物信息
@goods.route('/edit_goods',methods=['GET'])
@goods.route('/edit_goods/<int:id>',methods=['GET'])
@goods_required
def edit_goods(id=0):
	gd = Goods.query.get_or_404(id)
	carinfo = Car_Info.query.order_by(Car_Info.sort).all()
	cartype = Car_Type.query.all()
	return render_template('goods/edit_goods.html',gd = gd,carinfo = carinfo,cartype=cartype)

@goods.route('/edit_goods',methods=['POST'])
@goods_required
def edit_goods_post():
	# form = GoodsForm()
	goodsid = request.form.get('id')
	good = Goods.query.get(int(goodsid))
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

	if start_sheng:
		good.start_sheng = start_sheng
	if end_sheng:
		good.end_sheng = end_sheng

	if start_shi:
		good.start_shi = start_shi
	if end_shi:
		good.end_shi = end_shi


	
	yesr = time.strftime('%Y',time.localtime(time.time()))
	timestr = yesr+'-'+mon+'-'+day

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
	hms = ''
	if zone==u'全天':
		good.start_car_time = timestr+' 22:29:59 '
	if zone==u'上午':
		good.start_car_time = timestr+' 07:59:59 '
	if zone==u'下午':
		good.start_car_time = timestr+' 13:59:59 '
	if zone==u'晚上':
		good.start_car_time = timestr+' 19:59:59 '
	
	#装车时段
	good.start_zone = zone
	#备注
	good.note = request.form.get('note')
	#报价运费
	price = request.form.get('price')
	if price:
		good.start_price = price
	
	zhengche = request.form.get('zhengche')
	pingche = request.form.get('pingche')

	good.name = u'普货'
	good.select_car_type = '整车'
	good.car_type = '无要求'
	good.car_length = ''
	good.tiji = ''
	good.zhongliang = ''

	if zhengche:
		good.name = request.form.get('zhengche')
		good.select_car_type = u'整车'
		good.car_type = request.form.get('chexing',u'未知')
		chechang = request.form.get('chechang',u'未知,未知,未知')
		chechang = chechang.split(',')
		good.car_length = chechang[0]
		good.tiji = chechang[1]
		good.zhongliang = chechang[2]
	if pingche:
		good.name = request.form.get('pingche')
		good.select_car_type = u'拼车'
		good.car_length = u'拼车'
		good.car_type = u'拼车'
		good.tiji = request.form.get('tiji','')
		good.zhongliang = request.form.get('zhongliang','')

	
	
	
	try:
		db.session.add(good)
		db.session.commit()
		flash(u'货物信息更新成功。','success')
	except Exception, e:
		db.session.rollback()
		flash(u'发布失败，数据校验失败。','error')
		send_email(u'用户：%s 。更新货物提交信息错误：%s'%(current_user.phone,str(e)))
	
		
	return redirect(url_for('main.index'))









#用户、司机自行接货下单，预约确认  普通用户预约自行转换成司机角色
@goods.route('/send_order',methods=['POST'])
@login_required
def send_order():

	goodsid = request.form.get('goodsid')
	try:
		gd = Goods.query.get_or_404(int(goodsid))
	except Exception, e:
		send_email(u'用户：%s 。司机预约确认获取货物信息错误%s'%(current_user.phone,str(e)))
		abort(403)

	#如果没有手机号，获取手机号码  更改用户角色 为司机
	d = Driver()
	if current_user.phone=='' or current_user.phone == None:
		phone = request.form.get('phone')
		if not phone:
			flash(u'请输入手机号码。','error')
			return redirect(url_for('main.index'))
		if User.query.filter_by(phone=phone).first():
			flash(u'该手机号码已经被注册，请登录后再预约。','login')
			return redirect(url_for('auth.login'))
		d.user = current_user
		d.phone = phone
		d.number = u'未知车牌、'
		d.length = u'未知车长'
		
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
			return redirect(url_for('.show_goods'))
	else:
		d = Driver.query.get_or_404(int(request.form.get('car')))

	selfdriverpost = Driver_self_order.query.filter_by(goodsed=gd,driver=d).first()
	
	if selfdriverpost:
		flash(u'您已经预约过了，请不要重复预约','error')
		return redirect(url_for('main.index'))
	else:
		flash(u'预约成功，系统审核通过将电话通知您。','success')
		savedso = Driver_self_order(goodsed=gd,driver=d,price=request.form.get('price'))
		db.session.add(savedso)

		

		

	#预约人数+1
	gd.make_count  = gd.make_count+1
	db.session.add(gd)
	db.session.commit()

	
	gdxiangxi = gd.start_shi+u"——"+gd.end_shi+u','+gd.name+u',报价运费'+str(gd.start_price)
	try:
		flask_wechat.message.send_text(gd.consignor.user.wx_open_id,\
			u'您发布的货物信息：[%s]，已有司机进行预约，预约价格为：%s元,如您同意该预约价格，请回复：cy%s。'%(gdxiangxi,request.form.get('price'),savedso.id))
	
	except Exception, e:
		send_email(u'用户：%s 。预约货物微信通知用户错误：%s'%(current_user.phone,str(e)))
		
		


	return render_template('goods/send_order.html',gd=gd)

@goods.route('/tongyiyuyue/<int:yuyueid>',methods=['GET'])
@goods_required
def tongyiyuyue(yuyueid=0):
	dso = Driver_self_order.query.get_or_404(yuyueid)
	if dso.goodsed.consignor != current_user.consignors:
		return redirect(url_for('main.index'))
	if dso.state != 0:
		return redirect(url_for('main.index'))
	dso.state = 3
	db.session.add(dso) 
	db.session.commit()
	#推送消息给管理员或指定客服。
	try:
		flask_wechat.message.send_text('otCWCxPJxCSn6xuEE9UHzO544SvA',u'货物编号:%s 的货主同意了司机的预约请求，请进入后台查看双方身份信息认证。'%(dso.goodsed.id))
	except Exception, e:
		send_email(u'用户：%s 货主同意司机的接单申请微信通知错误。%s'%(current_user.phone,str(e)))
	
	return render_template('goods/tongyiyuyue.html')


#企业信息显示
@goods.route('/show_consignor',methods=['GET'])
@goods_required
def show_consignor():
	return render_template('goods/show_consignor.html')

def gen_rnd_filename():
    filename_prefix = datime.datetime.now().strftime('%Y%m%d%H%M%S')
    return '%s%s' % (filename_prefix, str(random.randrange(1000, 10000)))

#企业信息更改
@goods.route('/show_consignor',methods=['POST'])
@goods_required
def show_consignor_p():
	#公司名称
	name = request.form.get('name')
	#负责人
	fuzheren = request.form.get('fuzheren')
	#身份证号
	shenfenzheng = request.form.get('number')
	address = request.form.get('address')


	#营业执照
	yingyezhizhao = request.files['yingyezhizhao']
	fname, fext = os.path.splitext(yingyezhizhao.filename)
	rnd_name = '%s%s' % (gen_rnd_filename(), fext)

	filepath = os.path.join(current_app.static_folder, 'uploads/goods', rnd_name)
	dirname = os.path.dirname(filepath)
	if not os.path.exists(dirname):
		os.makedirs(dirname)
	yingyezhizhao.save(filepath)	
	saveurl = '/static/uploads/goods/'+rnd_name			
	db.session.add(Consignor_images(name=u'营业执照',url=saveurl,consignor=current_user.consignors))

	#身份证
	shenfenzhong = request.files['shenfenzhong']
	fname, fext = os.path.splitext(shenfenzhong.filename)
	rnd_name = '%s%s' % (gen_rnd_filename(), fext)
	filepath = os.path.join(current_app.static_folder, 'uploads/goods', rnd_name)
	dirname = os.path.dirname(filepath)
	if not os.path.exists(dirname):
		os.makedirs(dirname)
	shenfenzhong.save(filepath)	
	saveurl = '/static/uploads/goods/'+rnd_name		
	db.session.add(Consignor_images(name=u'身份证',url=saveurl,consignor=current_user.consignors))

	current_user.consignors.state = 1
	current_user.consignors.name = name
	current_user.consignors.fuzheren = fuzheren
	current_user.consignors.shenfenzheng = shenfenzheng
	current_user.consignors.address = address
	try:
		db.session.add(current_user)
		flash(u'已修改企业信息,请等待客服的审核。','success')
		try:
			flask_wechat.message.send_text(current_user.wx_open_id,\
				u'您已经提交了企业信息修改的申请，请等待客服的审核。')
		except Exception, e:
			send_email(u'用户：%s 。提交修改企业信息微信通知错误：%s'%(current_user.phone,str(e)))
		
		
		db.session.commit()
	except Exception, e:
		db.session.rollback()
	return redirect(url_for('.show_consignor'))

#确认接货下单  司机访问
#这里是司机下单过程  需要限时支付，需要到缓存机制
@goods.route('/confirm_order',methods=['POST'])
@login_required
@driver_required
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
		# from apscheduler.triggers.interval import IntervalTrigger
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
		send_email(u'用户：%s 确认接货下单错误。%s'%(current_user.phone,str(e)))
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















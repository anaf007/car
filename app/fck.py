#coding=utf-8

from app.models import *
from datetime import datetime
from app import db,scheduler,app,flask_wechat
import logging
import datetime as datime
from .errorSendMail import send_email
from apscheduler.triggers.interval import IntervalTrigger

#过时自动发送货物信息
def authSendGoods(goodsid):
	#不添加日志会提示错误
	logging.basicConfig()
	#数据库操作
	with app.app_context():
		try:
			#货物信息
			authgood = Goods.query.get(goodsid)
			st = Scheduler_task.query.filter_by(args=goodsid).first()
			#获取出发省 目的省
			adr = "["+authgood.start_sheng+"-"+authgood.end_sheng+"]"
			func_id = str(authgood.consignor.id)+":::"+str(authgood.id)
			#已发布未有任何操作
			if authgood.state == 0:
				now = datime.datetime.now()
				
				if authgood.start_car_time < now:
					day = datime.datetime.now() + datime.timedelta(days=1)
					if authgood.start_zone == u'全天':
						authgood.start_car_time = datime.datetime(day.year, day.month, day.day, 21, 59, 59)
					if authgood.start_zone == u'上午':
						authgood.start_car_time = datime.datetime(day.year, day.month, day.day, 07, 59, 59)
					if authgood.start_zone == u'下午':
						authgood.start_car_time = datime.datetime(day.year, day.month, day.day, 13, 59, 59)
					if authgood.start_zone == u'晚上':
						authgood.start_car_time = datime.datetime(day.year, day.month, day.day, 19, 59, 59)
					st.create_time = authgood.start_car_time
					db.session.add(authgood)
					db.session.add(st)
					try:
						flask_wechat.message.send_text(authgood.consignor.user.wx_open_id,\
							u'抱歉!您发送的%s，运费为：%s的货物已过期，系统已自动为您更新货物信息。%s'%(adr,authgood.start_price,authgood.id))
					except Exception, e:
						pass

				#更新定时器的执行时间 authgood.start_car_time已经等于当前一天后+10分钟
				seconds =  (datetime.strptime(str(authgood.start_car_time),"%Y-%m-%d %H:%M:%S")-now).seconds + 600								
				scheduler.delete_job(id=func_id)					
				scheduler.add_job(func=authSendGoods,id=func_id,args=[st.args,],trigger=IntervalTrigger(seconds=seconds),replace_existing=True)
			
				
				# dso = Driver_self_order.query.join(Goods).filter(Goods.start_sheng.like(authgood.start_sheng))\
				# 		.filter(Goods.end_sheng.like(authgood.end_sheng)).group_by('driver_id').all()
				# for i in dso:
				# 	try:
				# 		flask_wechat.message.send_text(i.driver.user.wx_open_id,\
				# 		u'%s有了新的货物信息，<a href="http://car.anaf.cn/consignor/show_goods/%s">点击查看货物信息。</a>'%(adr,authgood.id))
				# 	except Exception, e:
				# 		print str(e)

				#删除任务重新添加
				try:
										
					db.session.commit()
			
				except Exception, e:
					send_email(u'过时自动发送货物信息功能错误添加数据库错误：%s'%str(e))
			else:
				try:
					db.session.delete(st)
					db.session.commit()
					scheduler.delete_job(id=func_id)
				except Exception, e:
					send_email(u'job自动发送货物信息功能删除错误：%s'%str(e))
				


		except Exception, e:
			send_email(u'过时自动发送货物信息功能错误：%s,GoodsID:%s'%(str(e),goodsid))


#手动发送添加job货物信息
def Start_SendGoods(goodsid):
	logging.basicConfig()
	with app.app_context():
		try:
			authgood = Goods.query.get(goodsid)
			if authgood.state != 0:
				return
			a = datime.datetime.now()
			if authgood.start_car_time >= a:
				
				seconds =  (datetime.strptime(str(authgood.start_car_time),"%Y-%m-%d %H:%M:%S")-a).seconds 
				if authgood.start_zone ==u'全天':
					seconds = seconds-43200  #中午12点
				jobid = str(good.consignor.id) +':::'+str(good.id)
				scheduler.add_job(func=authSendGoods,id=jobid,args=[good.id,],trigger=IntervalTrigger(seconds=seconds),replace_existing=True)
		except Exception, e:
			send_email(u'手动发送货物信息功能错误：%s'%str(e))




			
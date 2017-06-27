#coding=utf-8
"""filename:app/driver/views.py
Created 2017-06-12
Author: by anaf
"""

# from flask import current_app
from  flask.ext.login import login_required,current_user
from ..decorators import goods_required,permission_required,driver_required
from . import driver
from ..models import Permission,Driver,User,Driver_post,Role
from flask import render_template,request,redirect,url_for,flash
from app import db
from datetime import datetime
from forms import Register_driver


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
@driver_required
def add_post():
	return render_template('driver/add_post.html')


#添加车源信息，此处应该进行系统匹配并发送邮件消息 短信等各种操作
@driver.route('/add_post',methods=['POST'])
@login_required
@driver_required
def add_posts():
	start_sheng = request.form.get('start_sheng')
	start_shi = request.form.get('start_shi')
	start_qu = request.form.get('start_qu')

	end_sheng = request.form.get('end_sheng')
	end_shi = request.form.get('end_shi')
	end_qu = request.form.get('end_qu')

	car = Driver.query.get_or_404(int(request.form.get('car')))
	time = request.form.get('time')
	price = request.form.get('price')
	note = request.form.get('note')

	gp = Driver_post()
	gp.title = '['+start_shi+'-'+end_shi+']'+u'发车时间:'+time
	gp.start_address = start_sheng+'-'+start_shi+'-'+start_qu
	gp.end_address = end_sheng+'-'+end_shi+'-'+end_qu
	gp.note = note
	gp.start_car_time = time
	gp.posts = car
	gp.start_price = price
	try:
		db.session.add(gp)
		db.session.commit()
		flash(u'添加成功')

	except Exception, e:
		db.session.rollback()
		flash(u'添加失败%s'%str(e))

	
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





#coding=utf-8
"""filename:app/auth/views.py
Created 2017-05-30
Author: by anaf
note:auth视图函数
"""
from flask import render_template,redirect,request,url_for,flash,make_response,current_app,session
from . import auth
from flask_login import login_user,login_required,logout_user,current_user
from ..models import User,Driver,Permission,Role,Consignor
from .forms import LoginForm,Register_goods
from app import db
import random,time

from flask_wechatpy import Wechat, wechat_required,oauth

# @auth.route('/verify')
# def verify():
# 	response = make_response.generate_verification_code()
# 	response.headers['Content-Type'] = 'image/jpeg'
# 	return response






@auth.route('/login',methods=['GET'])
def login():
	return render_template('auth/login.html',form=LoginForm())

@auth.route('/login',methods=['POST'])
def login_post():
	form = LoginForm()
	if form.validate_on_submit():
		try:
			if form.verification_code.data.upper() != session['verify']:
				flash(u'验证码错误1','error')
				return redirect(url_for('.login'))
		except Exception, e:
			flash(u'校验错误2','error')
			return redirect(url_for('.login'))

		user = User.query.filter_by(username=form.username.data).first()
		if not user:
			user = User.query.filter_by(phone=form.username.data).first()

		if user is not None and user.verify_password(form.password.data):
			login_user(user,True)
			
			if user.role is None or user.role.name==u'普通用户':
				return redirect(request.args.get('next') or url_for('main.main_login'))
				# return redirect(url_for('.register_goods'))
			else:
				return redirect(request.args.get('next') or url_for('main.main_login'))
		flash(u'校验数据错误3','error')
	else:
		flash(u'校验数据错误4','error')

	return redirect(url_for('.login'))

@auth.route('/logout')
@login_required
def logout():
	logout_user()
	flash(u'您已成功退出')
	return redirect(url_for('main.index_main'))


@auth.route('/register')
def register():
	return render_template('auth/register.html')

@auth.route('/register',methods=['POST'])
def register_post():
	username = request.form.get('username')
	password = request.form.get('password')
	repassword = request.form.get('repassword')
	if password !=repassword: 
		flash(u'两次密码不一样')
		return redirect(url_for('.register'))
	if username!='' :
		user = User.query.filter_by(username=username).first()
	else:
		user = ''
	if user is None:
		user = User(username=username,password=password)
		db.session.add(user)
		db.session.commit()
		flash(u'注册成功')
		return redirect(url_for('.login'))
	return render_template('auth/register.html')


@auth.before_app_request
def before_request():
	if current_user.is_authenticated:
		current_user.ping()
		#书本中还代码的  不知道方法有什么用  所以省去也没见有什么变化



#注册货主
@auth.route('/register_goods',methods=['GET'])
def register_goods():
	form = Register_goods()
	return render_template('auth/register_goods.html',form=form)


@auth.route('/register_goods',methods=['POST'])
def register_goods_post():
	form = Register_goods()
	if form.validate_on_submit():
		c = Consignor()
		c.user = current_user
		c.name = form.name.data
		c.company_size = form.company_size.data
		c.company_industry = form.company_industry.data
		c.address = form.address.data
		c.note = form.note.data
		c.static = 1
		r = Role.query.filter_by(name=u'货主').first()
		try:
			db.session.add(c)
			current_user.role =  r
			db.session.add(current_user)
			db.session.commit()
			flash(u'货主添加完毕')
			return redirect(url_for('usercenter.index'))
		except Exception, e:
			flash(u'数据错误，添加失败：%s'%str(e))
			db.session.rollback()
	else:
		flash(u'校验数据错误')
	return redirect(url_for('.register_goods'))

#自动注册 微信登录
@auth.route('/autoregister')
@oauth(scope='snsapi_userinfo')
def autoregister():
	try:
		wechat_id = session.get('wechat_user_id','')
	except Exception, e:
		wechat_id = ''
	if wechat_id:
		user = User.query.filter_by(wx_open_id=session.get('wechat_user_id')).first()
	else:
		user = []
	if user:
		login_user(user,True)
		return redirect(url_for('main.index'))


	choice_str = 'ABCDEFGHJKLNMPQRSTUVWSXYZ'
	username_str = ''
	password_str = ''
	str_time =  time.time()
	username_str = 'AU'
	username_str += str(int(int(str_time)*1.301))
	for i in range(2):
		username_str += random.choice(choice_str)

	for i in range(6):
		password_str += random.choice(choice_str)

	username = username_str
	password = password_str

	user = User.query.filter_by(username=username).first()
	if user is None:
		user = User(username=username,password=password,wx_open_id=wechat_id)
		db.session.add(user)
		db.session.commit()
		login_user(user,True)
		return redirect(url_for('main.index'))
	else:
		return redirect(url_for('.autoregister'))

@auth.route('/autologin/<int:id>')
def autologin(id):
	login_user(User.query.get_or_404(id))
	return redirect(url_for('main.index'))









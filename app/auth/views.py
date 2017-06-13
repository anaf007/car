#coding=utf-8
"""filename:app/auth/views.py
Created 2017-05-30
Author: by anaf
note:auth视图函数
"""
from flask import render_template,redirect,request,url_for,flash,make_response,current_app,session
from . import auth
from flask.ext.login import login_user,login_required,logout_user,current_user
from ..models import User
from .forms import LoginForm
from app import db
import random


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
				flash(u'验证码错误')
				return redirect(url_for('.login'))
		except Exception, e:
			flask(u'校验错误')
			return redirect(url_for('.login'))

		user = User.query.filter_by(username=form.username.data).first()
		if user is not None and user.verify_password(form.password.data):
			login_user(user,form.remember_me.data)
			return redirect(request.args.get('next') or url_for('main.main_login'))
		flash(u'校验数据错误')
	else:
		flash(u'校验数据错误')

	return redirect(url_for('.login'))

@auth.route('/logout')
@login_required
def logout():
	logout_user()
	flash(u'您已成功退出')
	return redirect(url_for('main.index'))


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








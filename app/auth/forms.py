#coding=utf-8
"""filename:app/auth/forms.py
Created 2017-05-30
Author: by anaf
"""
from flask.ext.wtf import Form
from wtforms import StringField,PasswordField,BooleanField,SubmitField
from wtforms.validators import Required,Length,Email

class LoginForm(Form):
	# email = StringField('Email',validators=[Required(),Length(1,64),Email()])
	username = StringField('Username',validators=[Required(),Length(1,64)])
	password = PasswordField('Password',validators=[Required(),Length(3, 12, message=u'密码长度在3到12为')])
	verification_code = StringField(u'验证码', validators=[Required(), Length(4, 4, message=u'填写4位验证码')])
	remember_me = BooleanField('Keep me logged in ')
	submit = SubmitField('Log In')


class Register_driver(Form):
	phone = StringField(u'车辆联系电话',validators=[Required(),Length(11)])
	length = StringField(u'车身长度',validators=[Required(),Length(1,10)])
	number = StringField(u'车牌号',validators=[Required(),Length(1,10)])
	travel = StringField(u'行驶证号',validators=[Required(),Length(1,10)])
	driver = StringField(u'驾驶证号',validators=[Required(),Length(1,10)])
	note = StringField(u'车辆描述')
	submit = SubmitField(u'注册')


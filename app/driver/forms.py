#coding=utf-8
from flask.ext.wtf import Form
from wtforms import StringField,PasswordField,BooleanField,SubmitField
from wtforms.validators import Required,Length

class Register_driver(Form):
	phone = StringField(u'车辆联系电话',validators=[Required(),Length(11)])
	length = StringField(u'车身长度',validators=[Required(),Length(1,10)])
	number = StringField(u'车牌号',validators=[Required(),Length(1,10)])
	travel = StringField(u'行驶证号',validators=[Required(),Length(1,10)])
	driver = StringField(u'驾驶证号',validators=[Required(),Length(1,10)])
	note = StringField(u'车辆描述')
	submit = SubmitField(u'注册')
#coding=utf-8
"""filename:app/consignor/forms.py
Created 2017-06-15
Author: by anaf
"""
from flask_wtf import Form
from wtforms import StringField,PasswordField,BooleanField,SubmitField,TextAreaField
from wtforms.validators import Required,Length,Email

class GoodsForm(Form):
	# name = StringField(u'货物标题',validators=[Required(),Length(1,64)])
	# unit = StringField(u'单位',validators=[Required(),Length(1,64)])
	# count = StringField(u'数量',validators=[Required(),Length(1,64)])
	# start_address = StringField(u'发货地',validators=[Required(),Length(1,64)])
	# end_address = StringField(u'运达地',validators=[Required(),Length(1,64)])
	# note = StringField(u'描述',validators=[Required(),Length(1,64)])
	# start_car_time = StringField(u'发车时间',validators=[Required(),Length(1,64)])
	start_price = StringField(u'报价运费',validators=[Required(),Length(1,64)])
	submit = SubmitField(u'发布')






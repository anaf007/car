#coding=utf-8
"""filename:app/goods/views.py
Created 2017-06-15
Author: by anaf
note:货源信息栏目，首页货物显示及某些司机看的页面，只能司机访问，所以是 @permission_required(Permission.DRIVER)

"""

from . import goods
from flask import render_template,flash,redirect,url_for
from  flask.ext.login import login_required,current_user
from ..decorators import permission_required
from app.models import Permission,Goods
from .forms import GoodsForm
from app import db

@goods.route('/')
@goods.route('/index')
@goods.route('/index/')
@login_required
@permission_required(Permission.DRIVER)
#只能司机查看首页的货物信息
def index():
	return render_template('goods/index.html')


@goods.route('/send_goods')
@login_required
@permission_required(Permission.CONSIGNOR)
#发布货源信息  只能货主访问
def send_goods():
	return render_template('goods/send_goods.html',form = GoodsForm())

@goods.route('/send_goods',methods=['POST'])
@login_required
@permission_required(Permission.CONSIGNOR)
def send_goods_post():
	form = GoodsForm()
	if form.validate_on_submit():
		good = Goods()
		good.name = form.name.data
		good.unit = form.unit.data
		good.count = form.count.data
		good.start_address = form.start_address.data
		good.end_address = form.end_address.data
		good.start_car_time = form.start_car_time.data
		good.note = form.note.data
		good.start_price = form.start_price.data
		good.state = 1
		good.user_goods = current_user
		try:
			db.session.add(good)
			db.session.commit()
			flash(u'发布成功')
		except Exception, e:
			db.session.rollback()
			flash(u'发布失败')
	else:
		flash(u'校验数据错误')
	return redirect(url_for('.send_goods'))




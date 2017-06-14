#coding=utf-8
"""filename:app/main/views.py
Created 2017-06-12
Author: by anaf
"""

# from flask import current_app
from  flask.ext.login import login_required,current_user
from ..decorators import driver_required,permission_required
from . import driver
from ..models import Permission,Driver,User
from ..decorators import driver_required,permission_required
from flask import render_template,request
from app import db

#需要登陆，且需要司机员权限
@driver.route('/')
@driver.route('/index/')
@login_required
@driver_required
def index():
	d = Driver.query.filter_by(user_id=current_user.id)
	car = current_user.drivers.all()
	return render_template('driver/index.html',car = car)


@driver.route('/reg_dirver_add',methods=['POST'])
@login_required
@driver_required
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
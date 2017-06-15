#coding=utf-8
"""filename:app/goods/views.py
Created 2017-06-15
Author: by anaf
note:货源信息栏目，只能司机访问，所以是 @permission_required(Permission.DRIVER)
"""

from . import goods
from flask import render_template
from  flask.ext.login import login_required
from ..decorators import permission_required
from app.models import Permission

@goods.route('/')
@goods.route('/index')
@goods.route('/index/')
@login_required
@permission_required(Permission.DRIVER)
def index():
	
	return render_template('goods/index.html')

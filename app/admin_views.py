#coding=utf-8
from flask.ext import admin,login
from flask_admin import helpers, expose
from flask import redirect,url_for,request
from wtforms import form, fields, validators
from .decorators import admin_required

#主页视图
class MyAdminIndexView(admin.AdminIndexView):
	#增加这个必须要登录后才能访问，不然显示403错误
	#但是还是不许再每一个函数前加上这么判定的  ，不然还是可以直接通过地址访问
	#加入了角色管理只能是超级管理员才能登录后台，注意导入初始化的顺序，不然报错
	@admin_required
	def is_accessible(self):
		return login.current_user.is_authenticated

	#跳转
	def inaccessible_callback(self, name, **kwargs):
		return redirect(url_for('auth.login', next=request.url))

	#后台首页   
	@admin.expose('/')
	def index(self):
		return self.render('admin/index.html')

	@admin.expose('/superadmin')
	def superadmin(self):
		return self.render('admin/index.html')

	
"""
	@expose('/')
	def index(self):
		if not login.current_user.is_authenticated:
			return redirect(url_for('.login_view'))
		return super(MyAdminIndexView, self).index()

	@expose('/login/', methods=('GET', 'POST'))
	def login_view(self):
		form = LoginForm(request.form)
		if helpers.validate_form_on_submit(form):
			user = form.get_user()
			login.form.get_user()
			login.login_user(user)

		if login.current_user.is_authenticated:
			return redirect(url_for('.index'))
		link = '<p>Don\'t have an account? <a href="' + url_for('.login_view') + '">Click here to register.</a></p>'
		self._template_args['form'] = form
		self._template_args['link'] = link
		return super(MyAdminIndexView, self).index()

	@expose('/logout/')
	def logout_view(self):
		login.logout_user()
		return redirect(url_for('.index'))

class LoginForm(form.Form):
    login = fields.TextField(validators=[validators.required()])
    password = fields.PasswordField(validators=[validators.required()])

    def validate_login(self, field):
        user = self.get_user()

        if user is None:
            raise validators.ValidationError('Invalid user')

        # we're comparing the plaintext pw with the the hash from the db
        if not check_password_hash(user.password, self.password.data):
        # to compare plain text passwords use
        # if user.password != self.password.data:
            raise validators.ValidationError('Invalid password')



"""


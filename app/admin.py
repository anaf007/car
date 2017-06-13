#coding=utf-8
"""filename:app/admin/views.py
Created 2017-06-01
Author: by anaf
note:admin视图函数
"""


from flask import Flask,request,redirect,url_for
from flask.ext.admin import Admin, BaseView, expose
from app import db
from app.models import Article,Category,User,User_msg,Category_attribute,Comment,Role,CategoryTop
from flask.ext.admin.contrib.sqla import ModelView
from flask.ext.login import current_user,login_required
from wtforms.validators import Required
from wtforms import TextAreaField
from wtforms.widgets import TextArea
from jinja2 import Markup
from flask_admin.form import rules
from flask.ext.admin.contrib.fileadmin import FileAdmin
import hashlib
from .decorators import admin_required
import os.path as op
path = op.join(op.dirname(__file__), 'static/uploads')
from flask_admin import form
import random
from werkzeug import secure_filename

# class admin_index_view(BaseView):
# 	@expose('/')
# 	@login_required
# 	def index(self):
# 		return '<a href="/admin">Click me to get to Admin!</a>'


#增加一个导航
# admin_app.add_view(admin_index_view(name=u'主页'))

# admin_app.add_view(ModelView(User,db.session,name=u'用户管理'))

class CKTextAreaWidget(TextArea):
	def __call__(self, field, **kwargs):
		if kwargs.get('class'):
			kwargs['class'] += ' ckeditor'
		else:
			kwargs.setdefault('class', 'ckeditor')
		return super(CKTextAreaWidget, self).__call__(field, **kwargs)


class CKTextAreaField(TextAreaField):
	widget = CKTextAreaWidget()


#User模型视图
class ModelView_User(ModelView):
	#认证
	# @admin_required	
	def is_accessible(self):
		return current_user.is_authenticated

	#跳转
	def inaccessible_callback(self, name, **kwargs):
		return redirect(url_for('auth.login', next=request.url))

	#解决密码无法盐加密问题
	def on_model_change(self, form, User, is_created):
		User.password = form.password_hash.data
		User.avatar_hash = hashlib.md5(User.username.encode('utf-8')).hexdigest()


	#是否允许创建、删除、编辑、只读
	can_create = True
	# can_delete = False
	# can_edit = False
	# can_view_details = True
	#每页记录显示行数
	page_size = 50

	column_display_pk = True
	column_display_all_relations = True

	#删除行
	column_exclude_list = ['comments', 'article_id','followed','followers',
							'password_hash','about_me','member_since','location']

	#搜索列表
	column_searchable_list = ['username', 'name']
	#筛选列表
	# column_filters = ['location']
	#直接在视图中启用内联编辑，快速编辑行
	column_editable_list = ['name']
	#直接在当前页弹框 进行 编辑或者添加，  不是很大用
	# create_modal = True
	# edit_modal = True
	#移除创建和编辑列表的字段
	form_excluded_columns = ['comments','last_seen', 'avatar_hash','article_id','followed','followers','member_since','location']
	#form  WTForms 表单验证，详细验证规则 看WTForms 
	# form_args={'name':{'label':u'名字','validators':[Required()]}}
	#制定form渲染参数
	form_widget_args = {
					'about_me': {
					'rows': 10,
					'style': 'color: black'
						}
					}
	#当表单包含外键时，使用Ajax加载那些相关的模型（没会用）
	# form_ajax_refs = {
	# 	'role_id': {
	# 		'fields': ['first_name', 'last_name', 'email'],
	# 		'page_size': 10
	# 		}
	# 	}
	#过滤ajax加载的结果 没会用
	# form_ajax_refs = {'active_user': QueryAjaxModelLoader('user', db.session, User,filters=["is_active=True", "id>1000"])}


	# select choices   没有select选择器  不知道效果
	# form_choices = {
	# 	'title': [
 #    		('MR', 'Mr'),
 #        	('MRS', 'Mrs'),
 #        	('MS', 'Ms'),
 #        	('DR', 'Dr'),
 #        	('PROF', 'Prof.')
 #        	]
 #        }
 	
    
	#列表行重写
	column_labels = {
		'id':u'序号',
		'username' : u'用户账号',
		'password_hash':u'密码',
		'name':u'真实姓名',
		'location':u'地址',
		'role_id':u'角色',
		'avatar_hash':u'头像',
		'last_seen':u'最后访问时间',
		'about_me':u'自我介绍',
		'role':u'角色',
    }
	# column_list = ('id', 'username','name',
	# 			'location','role_id','avatar_hash')
	#JS文件
	# extra_js = [url_for('static',filename='ckeditor/ckeditor.js')]
	extra_js = ['/static/ckeditor/ckeditor.js']
	form_overrides ={'about_me':CKTextAreaField}

	#头像
	def _list_thumbnail(view, context, model, name):
		if model.avatar_hash:
			return Markup('<img src="http://www.gravatar.com/avatar/%s?d=identicon&s=32"' % model.avatar_hash)
		else:
			return Markup('<img src="http://www.gravatar.com/avatar/%s?d=identicon&s=32"' % hashlib.md5(model.username.encode('utf-8')).hexdigest())


	def _list_about_me_sub(view, context, model, name):
		if model.about_me:
			return model.about_me[0:50]
		return model.about_me
	def _list_role_id_show(view,context,model,name):
		if model.role_id:
			return model.role_id
	#格式化列
	column_formatters = {'avatar_hash': _list_thumbnail,'about_me':_list_about_me_sub}

	# form_create_rules = ('location', rules.HTML('<input type="text" />'), 'username', 'about_me')


	def __init__(self, session, **kwargs):
		super(ModelView_User, self).__init__(User, session, **kwargs)


#文件管理
class Admin_static_file(FileAdmin):
	#认证
	def is_accessible(self):
		return current_user.is_authenticated

	#跳转
	def inaccessible_callback(self, name, **kwargs):
		return redirect(url_for('auth.login', next=request.url))



#用户退出
class Admin_logout(BaseView):
	@expose('/')
	def index(self):
		return redirect(url_for('auth.logout'))



#文章模型视图
class ModelView_Article(ModelView):
	file_str = ''
	for i in range(5):
		file_str += chr(random.randint(65, 90))
	#认证
	# @admin_required	
	def is_accessible(self):
		return current_user.is_authenticated

	#跳转
	def inaccessible_callback(self, name, **kwargs):
		return redirect(url_for('auth.login', next=request.url))

	def _list_thumbnail(view, context, model, name):
		#如果没有图片显示缩略图
		if not model.thumbnail:
			return Markup('<img src="%s">' % url_for('static',filename="uploads/admin/thumbnail/"+form.thumbgen_filename('111')))
		return Markup('<img src="%s">' % url_for('static',filename="uploads/admin/thumbnail/"+form.thumbgen_filename(model.thumbnail)))

	#格式化列显示
	column_formatters = {'thumbnail':_list_thumbnail}
	#格式化创建表格为文件上传
	def prefix_name(obj, file_data):
		parts = op.splitext(file_data.filename)
		return ModelView_Article.file_str+'_'+secure_filename('%s%s' % parts)
	
	form_overrides = {
		'thumbnail': form.ImageUploadField
	}
	
	# form_args = {
	# 	'thumbnail': {
	# 		'label': u'缩略图',
	# 	}
	# }
	
	form_extra_fields = {
		'thumbnail': form.ImageUploadField(u'缩略图',
			base_path=path+'/admin/thumbnail/',
			thumbnail_size=(50, 50, True),
			namegen=prefix_name  #本地保存文件名称
		)
	}

	#列表行重写
	column_labels = {
		'id':u'序号',
		'title' : u'文章标题',
		'show':u'是否显示',
		'click':u'查看次数',
		'timestamp':u'发布时间',
		'author_id':u'作者',
		'seokey':u'SEO优化词',
		'seoDescription':u'SEO优化',
		'body':u'内容',
		'author':u'作者',
		'thumbnail':u'缩略图',
		'category':u'所属栏目',
	}

	#显示列表行删除
	column_exclude_list = ['comments','seokey','seoDescription','body','Author']
	
	#分页
	page_size = 20
	#富文本编辑器
	form_widget_args = {
		'body': {
		'rows': 5,
		'style': 'color: black'
		}
	}
	extra_js = ['/static/ckeditor/ckeditor.js']
	form_overrides ={'body':CKTextAreaField}

	#搜索列表
	column_searchable_list = ['title', 'body']

	#移除创建和编辑列表的字段
	form_excluded_columns = ['click','author', 'comments']
	#更改模型，页面取消添加的作者在后端添加防止更改
	def on_model_change(self, form, Article, is_created):
		Article.author = current_user
	

	def __init__(self, session, **kwargs):
		super(ModelView_Article, self).__init__(Article, session, **kwargs)


#顶级栏目模型视图
class ModelView_CategoryTop(ModelView):
	#认证
	@admin_required	
	def is_accessible(self):
		return current_user.is_authenticated

	#跳转
	def inaccessible_callback(self, name, **kwargs):
		return redirect(url_for('auth.login', next=request.url))

	#列表行重写
	column_labels = {
		'id':u'序号',
		'title' : u'栏目名称',
		'show':u'是否显示',
		'sort':u'栏目排序',
		'nlink':u'外部链接',
		'template':u'栏目模板',
		'body':u'栏目内容',
		'seoDescription':u'SEO优化',
		'seoKey':u'SEO关键词',
		'category_top_attribute':u'栏目属性',
	}

	#创建和编辑列表删除列
	form_excluded_columns = ['category']
	#显示列表删除行
	column_exclude_list = ['body']
	#富文本编辑器
	extra_js = ['/static/ckeditor/ckeditor.js']
	form_overrides ={'body':CKTextAreaField}


	def __init__(self, session, **kwargs):
		super(ModelView_CategoryTop, self).__init__(CategoryTop, session, **kwargs)
	


#栏目分类模型视图
class ModelView_Category(ModelView):
	#认证
	@admin_required	
	def is_accessible(self):
		return current_user.is_authenticated

	#跳转
	def inaccessible_callback(self, name, **kwargs):
		return redirect(url_for('auth.login', next=request.url))

	#列表行重写
	column_labels = {
		'id':u'序号',
		'title' : u'栏目名称',
		'show':u'是否显示',
		'sort':u'栏目排序',
		'nlink':u'外部链接',
		'template':u'栏目模板',
		'body':u'栏目内容',
		'seoDescription':u'SEO优化',
		'seoKey':u'SEO关键词',
		'category_pid':u'上级栏目',
		'category_attribute':u'栏目属性',
	}
	#列表删除行
	column_exclude_list = ['pubd','seoKey','seoDescription','body']
	#移除创建和编辑列表的字段
	form_excluded_columns = ['pubd','article_id']

	extra_js = ['/static/ckeditor/ckeditor.js']
	form_overrides ={'body':CKTextAreaField}

	def on_model_change(self, form, Category, is_created):
		# print Category
		pass


	def __init__(self, session, **kwargs):
		super(ModelView_Category, self).__init__(Category, session, **kwargs)



#coding=utf-8
"""filename:app/models.py
Created 2017-05-30
Author: by anaf
note:数据库模型函数
"""

from werkzeug.security import generate_password_hash,check_password_hash
from app import db
from flask.ext.login import UserMixin,AnonymousUserMixin
from .import login_manager
from datetime import datetime
import hashlib,random
from flask import request,current_app
import datetime as datetime2



#权限,必须进二阶乘 *2  0x10,0x20,0x40,0x80
class Permission:
	FOLLOW = 0x01   #关注
	COMMIT = 0x02	#在他人的文章中发表评论
	WRITE_ARTICLES = 0x03	#写文章
	MODERATE_COMMENTS = 0x04 #管理他人发表的评论
	DRIVER = 0x08  #司机栏目
	CONSIGNOR =0x10 #货主栏目
	ADMINISTER = 0x80	#管理员


"""角色表 一对多，一个角色对应多个用户
db.relationship('User',backref='role')
因为User 还没有定义 所以使用字符串形式指定
"""
class Role(db.Model):
	__tablename__ = 'roles'
	id = db.Column(db.Integer,primary_key=True)
	name = db.Column(db.String(64),unique=True)
	default = db.Column(db.Boolean,default=False,index=True)
	permissions = db.Column(db.Integer)
	users = db.relationship('User',backref='role',lazy='dynamic')

	def __repr__(self):
		return self.name

	@staticmethod
	def insert_roles():
		#二进制处理的所以在数据库中显示的7、255、3
		roles = {
			u'普通用户':(Permission.FOLLOW|
					Permission.COMMIT|
					Permission.WRITE_ARTICLES,True),

			u'管理员':(Permission.FOLLOW|
					Permission.COMMIT|
					Permission.WRITE_ARTICLES|
					Permission.MODERATE_COMMENTS,False),

			u'司机':(Permission.FOLLOW|
					Permission.COMMIT|
					Permission.WRITE_ARTICLES|
					Permission.DRIVER,False),

			u'货主':(Permission.FOLLOW|
					Permission.COMMIT|
					Permission.WRITE_ARTICLES|
					Permission.CONSIGNOR,False),

			u'超级管理员':(0xff,False)
		}
		for r in roles:
			role = Role.query.filter_by(name=r).first()
			if role is None:
				role = Role(name=r)
			role.permissions = roles[r][0]
			role.default = roles[r][1]
			db.session.add(role)
		db.session.commit()


#多对多关系
#自引用关系
class Follow(db.Model):
	__tablename__ = 'follows'
	follower_id = db.Column(db.Integer, db.ForeignKey('users.id'),primary_key=True)
	followed_id = db.Column(db.Integer, db.ForeignKey('users.id'),primary_key=True)
	timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class User(UserMixin,db.Model):
	__tablename__ = 'users'
	id = db.Column(db.Integer,primary_key = True)
	#账户名称
	username = db.Column(db.String(64),unique=True,index=True)
	#密码
	password_hash = db.Column(db.String(128))
	#角色，多对一
	role_id = db.Column(db.Integer,db.ForeignKey('roles.id'))
	#名字
	name = db.Column(db.String(64))
	#地址
	location = db.Column(db.String(64))
	#自我简介
	about_me = db.Column(db.Text())
	#创建时间
	member_since = db.Column(db.DateTime(),default=datetime.utcnow)
	#最后访问时间
	last_seen = db.Column(db.DateTime(),default=datetime.utcnow)
	#头像哈希
	avatar_hash = db.Column(db.String(32))
	#电子邮箱，找回密码
	mail = db.Column(db.String(100),unique=True) 
	#手机号，也可以用于登陆
	phone  = db.Column(db.String(100),index=True,unique=True)
	#货主表 一对一   
	consignors  = db.relationship('Consignor', backref='consignor_user',uselist=False)
	#创建者负责人  多对一  relationship  不会在表中显示行
	drivers  = db.relationship('Driver', backref='driver_user',primaryjoin='Driver.user_id == User.id',lazy='dynamic')
	#车队
	fleet_id  = db.Column(db.Integer())
	#账户保障金
	price = db.Column(db.Numeric(precision=10,scale=2,\
		asdecimal=True, decimal_return_scale=None),default=0)
	#状态  默认1
	status = db.Column(db.Integer(),default=1)
	#外键文章
	article_id = db.relationship('Article',backref='author',lazy='dynamic')
	#多对多关系
	followed = db.relationship('Follow',
								foreign_keys=[Follow.follower_id],
								backref=db.backref('follower', lazy='joined'),
								lazy='dynamic',
								cascade='all, delete-orphan')
	followers = db.relationship('Follow',
								foreign_keys=[Follow.followed_id],
								backref=db.backref('followed', lazy='joined'),
								lazy='dynamic',
								cascade='all, delete-orphan')
	#评论
	comments = db.relationship('Comment', backref='author', lazy='dynamic')
	#货物发布者 这里不做货物发布了   货物发布应当链接到货主表
	# goods_id = db.relationship('Goods',backref='user_goods',primaryjoin='Goods.user_id == User.id')
	#货物司机接单者
	car_goods_id = db.relationship('Goods',backref='car_goods_user',primaryjoin='Goods.car_user_id == User.id')
	#付款者
	order_pay = db.relationship('Order_pay', backref='order_pay_user',lazy='dynamic',primaryjoin='Order_pay.pay_user_id == User.id')
	#用户邮件
	user_msgs = db.relationship('User_msg', backref='user_msg',primaryjoin='User_msg.users == User.id')
	

	def __init__(self,**kwargs):
		super(User,self).__init__(**kwargs)
		#初始化时候添加自己为关注者
		#self.follow(self)
		#赋予角色信息
		if self.role is None:
			if self.username ==current_app.config['SUPERADMIN_NAME']:
				self.role = Role.query.filter_by(permissions=0xff).first()
			if self.role is None:
				self.role = Role.query.filter_by(default=True).first()

		#头像
		if self.avatar_hash is None:
			#使用flask-admin这里得到的self为空
			if self.username:
				self.avatar_hash = hashlib.md5(self.username.encode('utf-8')).hexdigest()
			# db.session.add(self)
			# db.session.commit()

	# def __repr__(self):
	# 	return self.username

	@property
	def password(self):
		raise AttributeError('password is not a readable attribute')

	@password.setter
	def password(self,password):
		self.password_hash = generate_password_hash(password)

	def verify_password(self,password):
		return check_password_hash(self.password_hash,password)

	#验证角色
	def can(self,permissions):
		return self.role is not None and \
			(self.role.permissions & permissions) == permissions

	#验证角色
	def is_administrator(self):
		return self.can(Permission.ADMINISTER)

	#刷新用户最后访问时间
	def ping(self):
		self.last_seen = datetime.utcnow()
		db.session.add(self)

	#头像
	def gravatar(self,size=100,default='identicon',rating='g'):
		if request.is_secure:
			url = 'https://secure.gravatar.com/avatar'
		else:
			url = 'http://www.gravatar.com/avatar'
		hash = self.avatar_hash or hashlib.md5(self.username.encode('utf-8')).hexdigest()
		return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
				url=url,hash=hash,size=size,default=default,rating=rating)

	#生成虚拟数据
	@staticmethod
	def generate_fake(count=100):
		from sqlalchemy.exc import IntegrityError
		from random import seed
		import forgery_py
		seed()
		for i in range(count):
			 u = User(username=forgery_py.internet.user_name(True),
			 		password = forgery_py.lorem_ipsum.word(),
			 		# confirmed=True,
			 		name = forgery_py.name.full_name(),
			 		location = forgery_py.address.city(),
			 		about_me = forgery_py.lorem_ipsum.sentence(),
			 		member_since = forgery_py.date.date(True)
			 		)
			 db.session.add(u)
			 try:
			 	db.session.commit()
			 except Exception, e:
			 	db.session.rollback()

	#多对多关注关系辅助方法
	# def follow(self, user):
	# 	if not self.is_following(user):
	# 		f = Follow(follower=self,followed=user)
	# 		db.session.add(f)
	# 		db.session.commit()

	# def unfollow(self, user):
	# 	f = self.followed.filter_by(followed_id=user.id).first()
	# 	if f:
	# 		db.session.delete(f)
			# db.session.commit()

	# def is_following(self, user):
	# 	return self.followed.filter_by(followed_id=user.id).first() is not None
	# 	return fo is not None

	# def is_followed_by(self, user):
	# 	return self.followers.filter_by(follower_id=user.id).first() is not None


#验证角色
class AnonymousUser(AnonymousUserMixin):
	def can(self,permissions):
		return False

	def is_administrator(self):
		return False
#验证角色
login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))


#文章
class Article(db.Model):
	__tablename__ = 'articles'
	id = db.Column(db.Integer,primary_key=True)
	#标题
	title = db.Column(db.String(64))
	#是否显示
	show = db.Column(db.Boolean,default=True)
	#点击次数
	click = db.Column(db.Integer,default=random.randint(100,200)) 
	#缩略图
	thumbnail = db.Column(db.Text)
	#关键字
	seokey = db.Column(db.String(128))
	#描述
	seoDescription = db.Column(db.String(200))
	#创建时间
	timestamp = db.Column(db.DateTime,index=True,default=datetime.utcnow)
	#用户角色 多对一   此表为多
	author_id = db.Column(db.Integer,db.ForeignKey('users.id'))
	#评论 一对多 对应多条评论
	comments = db.relationship('Comment', backref='articles', lazy='dynamic')
	#栏目内容
	body = db.Column(db.Text)
	#所属栏目
	category_id = db.Column(db.Integer,db.ForeignKey('categorys.id'))
	# category_id = db.relationship('Category', backref=db.backref('category', lazy='dynamic'))

	def __repr__(self):
		return u"<文章:{}>".format(self.title)

	#生成虚拟数据
	@staticmethod
	def generate_fake(count=100):
		from random import seed,randint
		import forgery_py
		seed()
		user_count = User.query.count()
		for i in range(count):
			u = User.query.offset(randint(0,user_count-1)).first()
			p = Article(title=forgery_py.name.full_name(),
					body = forgery_py.lorem_ipsum.sentences(randint(1,3)),
					timestamp=forgery_py.date.date(True),
					author = u
					)
			db.session.add(p)
			db.session.commit()

	"""平板上花了挺长的时间  很多错误，
	都是打错或者没导入，都解决了
	python manage.py shell
	from app.models import User,Post
	User.generate_fake(100)
	Post.generate_fake(100)
	"""


#评论
class Comment(db.Model):
	__tablename__ = 'comments'
	id = db.Column(db.Integer,primary_key=True)
	body = db.Column(db.Text)
	body_html = db.Column(db.Text)
	timestamp = db.Column(db.DateTime,index=True,default=datetime.utcnow)
	disabled = db.Column(db.Boolean)
	author_id =db.Column(db.Integer,db.ForeignKey('users.id'))
	article_id = db.Column(db.Integer,db.ForeignKey('articles.id'))

	@staticmethod
	def on_changed_body(target,value,oldvalue,initiator):
		allowed_tags = ['a','abbr','acronym','b','code','em','i','strong']
		target.body_html 



category_attribute_reg = db.Table('category_attribute_register',
							db.Column('category_id',db.Integer,db.ForeignKey('categorys.id')),
							db.Column('category_attribute_id',db.Integer,db.ForeignKey('category_attribute.id'))
							)


#顶级栏目
class CategoryTop(db.Model):
	__tablename__ = 'category_top'
	id = db.Column(db.Integer,primary_key=True)
	title = db.Column(db.String(255))
	show = db.Column(db.Boolean,default=True)
	nlink = db.Column(db.Text)
	sort = db.Column(db.Integer,default=10)
	template  = db.Column(db.String(64))
	seoKey = db.Column(db.String(200))
	seoDescription = db.Column(db.String(200))
	body = db.Column(db.Text)
	category = db.relationship('Category',backref='category_pid',lazy='dynamic')
	category_attribute_id = db.Column(db.Integer,db.ForeignKey('category_attribute.id'))
	
	

	def __repr__(self):
		return self.title
	

#本来是想用多对多自引用关系 但是出现的错误太多，解决起来花很多时间，
#干脆用一对多关系解决父级栏目关系
#栏目导航分类
class Category(db.Model):
	__tablename__ = 'categorys'
	id = db.Column(db.Integer,primary_key=True)
	title = db.Column(db.String(64))
	show = db.Column(db.Boolean,default=True)
	sort = db.Column(db.Integer,default=100)
	pubd =  db.Column(db.DateTime(),default = datetime.utcnow)
	nlink = db.Column(db.Text)
	template  = db.Column(db.String(64))
	body = db.Column(db.Text)
	#外键属性表
	category_attribute_id = db.Column(db.Integer,db.ForeignKey('category_attribute.id'))
	#父级栏目

	category_top_id = db.Column(db.Integer,db.ForeignKey('category_top.id'))
	#一对多文章
	article_id = db.relationship('Article',backref='category',lazy='dynamic')
	# article_id = db.Column(db.Integer,db.ForeignKey('Article.id'))
	seoKey = db.Column(db.String(200))
	seoDescription = db.Column(db.String(200))
	

	def __repr__(self):
		return self.title


class Category_attribute(db.Model):
	__tablename__ = 'category_attribute'
	id = db.Column(db.Integer,primary_key=True)
	name = db.Column(db.String(64))
	category_id = db.relationship('Category',backref='category_attribute',lazy='dynamic')
	category_top_id = db.relationship('CategoryTop',backref='category_top_attribute',lazy='dynamic')
	def __repr__(self):
		return self.name


#用户消息表
class User_msg(db.Model):
	__tablename__ = 'user_msgs'
	id = db.Column(db.Integer,primary_key=True)
	title = db.Column(db.String(64))
	body = db.Column(db.Text)
	timestamp = db.Column(db.DateTime(),default=datetime.utcnow)
	#是否显示？
	show = db.Column(db.Integer,default=0)
	#状态0已发送未读 1已读 -1删除 2已确认,已确认跟已读区别就是已确认就是支付内容一定的删除了
	state = db.Column(db.Integer())
	users = db.Column(db.Integer, db.ForeignKey('users.id'))


"""
使用者    负责人    车辆
A		A			A
B		A			A
C		A			A	
A		B			B
B		A			C

1.一辆车只有一个负责人
2.一辆车可以有多个使用者
3.一个负责人可以有多台车

"""

driver_user_reg = db.Table('driver_user_reg',
						db.Column('user_id',db.Integer,db.ForeignKey('users.id')),
						db.Column('use_driver_id',db.Integer,db.ForeignKey('drivers.id'))
					)


#车辆表
class Driver(db.Model):
	__tablename__ = 'drivers'
	id = db.Column(db.Integer(),primary_key=True)
	# 创建者主人# 多对一    会在表中创建user_id
	user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
	
	#创建者  多，     一辆车 多个人用
	use = db.relationship('User',
								secondary=driver_user_reg,
								backref=db.backref('use_drivers', lazy='dynamic'),
								lazy='dynamic')
	
	# users_id = db.Column(db.Integer, db.ForeignKey('users.id'))
	#车长
	length = db.Column(db.String(255))
	#车型
	car_type = db.Column(db.String(255))
	#体积
	tiji = db.Column(db.String(255))
	#重量
	zhongliang = db.Column(db.String(255))
	#品牌
	# brand =  db.Column(db.String(255))
	#车牌号
	number = db.Column(db.String(255))
	#车架号码
	frame_number  = db.Column(db.String(255))
	#发动机号码
	engine_number  = db.Column(db.String(255))
	#行驶证
	driver   = db.Column(db.String(255))
	#驾驶证
	travel   = db.Column(db.String(255))
	#违约次数
	break_number = db.Column(db.Integer(),default=0) 
	#申请时间
	create_time = db.Column(db.DateTime,default=datetime.utcnow) 
	#开通时间
	start_time = db.Column(db.DateTime,default=datetime.utcnow) 
	#状态
	state = db.Column(db.Integer(),default=0)
	#车辆描述
	note = db.Column(db.Text)
	#车辆证件照片   一
	driver_images = db.relationship('Driver_images', backref='driverImages',lazy='dynamic')
	#直接关联车辆信息表driver_posts ,2017-07-21-司机自助下单  直接关联这个表不用发布信息所以不用关联下面这个了
	order_pay = db.relationship('Order_pay', backref='order_pays',lazy='dynamic',primaryjoin='Order_pay.drivers_id == Driver.id')
	post = db.relationship('Driver_post', backref='driverPosts',lazy='dynamic',primaryjoin='Driver_post.driver_id == Driver.id')
	#司机自助下单货物用户
	driver_self_post_id = db.relationship('Driver_self_order', backref='driver_self_order_driver',lazy='dynamic',primaryjoin='Driver_self_order.driver == Driver.id')



	# def __repr__(self):
	# 	return self.number


#车辆照片
class Driver_images(db.Model):
	__tablename__ = 'driver_images'
	id = db.Column(db.Integer(),primary_key=True)
	name = db.Column(db.String(64)) #
	url = db.Column(db.String(100))
	#多
	driver_id = db.Column(db.Integer, db.ForeignKey('drivers.id'))


#货主表发货人。不是goods货源表
class Consignor(db.Model):
	__tablename__ = 'consignors'
	id = db.Column(db.Integer(),primary_key=True)
	# 创建者主人# 多对一    会在表中创建user_id
	user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
	#公司名称
	name = db.Column(db.String(64))
	#公司大小规模 人数  20人  50人100人200人 500人1000人 2000人10000人
	company_size = db.Column(db.String(50)) 
	#公司行业，水产，销售 木材。。等等
	company_industry = db.Column(db.String(50)) 
	#证件表  ，公司营业执照等证件。
	# company_cer = db.Column(db.Integer()) 
	#公司地址
	address  = db.Column(db.String(255)) 
	#违约次数
	break_number = db.Column(db.Integer(),default=0) 
	#申请时间
	create_time = db.Column(db.DateTime,default=datetime.utcnow) 
	#开通时间
	start_time = db.Column(db.DateTime,default=datetime.utcnow) 
	#状态 0未开通 1正常
	state = db.Column(db.Integer(),default=0)
	#公司简介
	note = db.Column(db.Text)
	#接单车辆？ 接的是  车辆信息表
	# driver_post = db.relationship('Driver_post', backref='driver_posts',lazy='dynamic',primaryjoin='Driver_post.consignor_user_id == Consignor.id')
	#货物表
	goods_id = db.relationship('Goods', backref='consignorsGoods',lazy='dynamic',primaryjoin='Goods.consignors_id == Consignor.id')
	#货主自助下单   一对一uselist='False'？
	goods_self_order = db.relationship('Goods_self_order', backref='consignors_selft_order',lazy='dynamic')



#货主发布的货物信息表
class Goods(db.Model):
	__tablename__ = 'goods'
	id = db.Column(db.Integer(),primary_key=True)
	#名称
	name = db.Column(db.String(255)) 
	#体积 方
	tiji = db.Column(db.String(16)) 
	#重量
	zhongliang = db.Column(db.String(16)) 
	#车型
	car_type = db.Column(db.String(16)) 
	#车长
	car_length = db.Column(db.String(16)) 
	#单位  （吨，千克，次[趟]）
	unit = db.Column(db.String(16)) 
	#数量
	count = db.Column(db.Integer(),default=1)
	#发货地
	start_address = db.Column(db.String(255)) 
	start_sheng = db.Column(db.String(255)) 
	start_shi = db.Column(db.String(255)) 
	start_qu = db.Column(db.String(255)) 
	start_xiangxi_address = db.Column(db.String(255)) 
	#运送地
	end_address = db.Column(db.String(255)) 
	end_sheng = db.Column(db.String(255)) 
	end_shi = db.Column(db.String(255)) 
	end_qu = db.Column(db.String(255)) 
	end_xiangxi_address = db.Column(db.String(255)) 
	#描述
	note = db.Column(db.Text) 
	#car_type 整车拼车零担
	select_car_type = db.Column(db.String(255)) 
	#发车时间
	start_car_time =  db.Column(db.DateTime) 
	start_zone = db.Column(db.String(10))
	#发布时间
	create_time = db.Column(db.DateTime,default=datetime.utcnow) 
	#发布者 不是user表 应该是货主公司表 
	consignors_id = db.Column(db.Integer, db.ForeignKey('consignors.id'))
	# user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
	#开始报价运费
	start_price = db.Column(db.Numeric(precision=10,scale=2,\
		asdecimal=True, decimal_return_scale=None))
	#实际运费   接单结算运费 定金抽取比例在订单列表  系统调节
	end_price =  db.Column(db.Numeric(precision=10,scale=2,\
		asdecimal=True, decimal_return_scale=None))
	#接单者
	car_user_id =  db.Column(db.Integer, db.ForeignKey('users.id'))
	#对应车辆信息表
	driver_post_id = db.relationship('Driver_post', backref='goods_driver_posts',lazy='dynamic',primaryjoin='Driver_post.consignor_user_id == Goods.id')
	# derver_posts_id =  db.Column(db.Integer, db.ForeignKey('driver_post.id'))
	#接单时间
	receive_time = db.Column(db.DateTime) 
	#状态 -2失效订单超时未支付  -1管理员关闭 0发布 1司机已经接单未付款 ，2司机已付款到系统  3司机已经运送抵达ok  4系统确认已经抵达ok 完成   其他状态等待 ?4初期未付款状态?
	state = db.Column(db.Integer(),default=0)
	order_pay = db.relationship('Order_pay', backref='goods_order_pay',lazy='dynamic',primaryjoin='Order_pay.goods_id == Goods.id')
	#预约数量
	make_count = db.Column(db.Integer,default=0)
	#紧急状态 置顶1
	show_statie = db.Column(db.Integer,default=0)
	#自助下单
	driver_self_post_id = db.relationship('Driver_self_order', backref='driver_self_orders',lazy='dynamic',primaryjoin='Driver_self_order.goods == Goods.id')


#货源留言表,目前还没有关系
class Goods_comment(db.Model):
	__tablename__ = 'goods_comments'
	id = db.Column(db.Integer(),primary_key=True)
	send_goods_id  = db.Column(db.Integer())


#支付订单,预约表
class Order_pay(db.Model):
	__tablename__ = 'order_pays'
	id = db.Column(db.Integer,primary_key=True)
	#订单
	order  = db.Column(db.String(20),unique=True)
	#货物
	goods_id =  db.Column(db.Integer, db.ForeignKey('goods.id'))
	#车辆
	drivers_id =  db.Column(db.Integer, db.ForeignKey('drivers.id'))
	#车辆信息
	driver_post_id =  db.Column(db.Integer, db.ForeignKey('driver_posts.id'))
	#创建时间
	create_time = db.Column(db.DateTime,default=datetime.utcnow)
	#支付时间
	pay_time = db.Column(db.DateTime)
	#-1失效 0创建 1审核通过未支付 2已支付 
	state = db.Column(db.Integer,default=0)
	#支付者，不能直接关联货主或者车辆信息表  因为一个车可能是多个用户使用
	pay_user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
	#支付金额
	pay_price = db.Column(db.Numeric(precision=10,scale=2,\
		asdecimal=True, decimal_return_scale=None))


#车源信息
class Driver_post(db.Model):
	__tablename__ = 'driver_posts'
	id = db.Column(db.Integer,primary_key=True)
	#名称
	title = db.Column(db.String(100))
	#发车地点
	#出发省
	start_sheng = db.Column(db.String(100))
	#出发市
	start_shi = db.Column(db.String(100))
	#出发区
	start_qu = db.Column(db.String(100))

	#目的省
	end_sheng = db.Column(db.String(100))
	#目的省
	end_shi = db.Column(db.String(100))
	#目的省
	end_qu = db.Column(db.String(100))

	#描述
	note = db.Column(db.Text) 
	#发车时间
	start_car_time =  db.Column(db.DateTime) 
	#发车时段  全天 上午下午晚上
	zone = db.Column(db.String(100))

	start_address = db.Column(db.String(100))
	#目的省
	end_address = db.Column(db.String(100))

	#发布时间
	create_time = db.Column(db.DateTime,default=datetime.utcnow) 
	#发布者
	driver_id = db.Column(db.Integer, db.ForeignKey('drivers.id'))
	#开始报价运费
	start_price = db.Column(db.Numeric(precision=10,scale=2,\
		asdecimal=True, decimal_return_scale=None))
	#实际运费   接单结算运费 系统抽取比例  系统调节
	end_price =  db.Column(db.Numeric(precision=10,scale=2,\
		asdecimal=True, decimal_return_scale=None))
	#接单者，关联到货物信息表
	consignor_user_id =  db.Column(db.Integer, db.ForeignKey('goods.id'))
	#接单时间
	receive_time = db.Column(db.DateTime) 
	#状态 -2失效订单被抢付  -1管理员关闭 0发布 1司机已经接单未付款 ，2司机已付款到系统  3已经运送抵达ok  4司机自身去接单，所以该条信息自动冲掉 ！5！其他状态等待
	state = db.Column(db.Integer(),default=0)
	#外键
	order_pay = db.relationship('Order_pay', backref='driver_posts_order_pays',uselist='False')

	goods_self_order = db.relationship('Goods_self_order', backref='driver_post_self_order',uselist='False')
	#预约次数
	make_count = db.Column(db.Integer,default=0)



class Order_Task(db.Model):
	__tablename__ = 'order_tasks'
	id = db.Column(db.Integer,primary_key=True)
	#订单号
	order_str = db.Column(db.String(20))
	#创建时间
	create_time = db.Column(db.DateTime,default=datetime.utcnow)
	#运行时间
	run_time = db.Column(db.DateTime,default=datetime.utcnow)


class Redis_Task(db.Model):
	__tablename__ = 'redis_tasks'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(80))
	redis_key = db.Column(db.String(128), unique=True)
	start_time = db.Column(db.DateTime)
	create_date = db.Column(db.DateTime, default=datetime.utcnow)

	def __init__(self, name, redis_key, start_time):
		self.name = name
		self.redis_key = redis_key
		start_time = ':'.join(start_time.split(':')[:2])
		self.start_time = datetime2.datetime.strptime(start_time, "%Y-%m-%d %H:%M")
		# self.seconds as key expire seconds
		self.seconds = int((self.start_time - datetime.utcnow()).total_seconds())

	def __repr__(self):
		return '<Task name:%r, key:%r>' % (self.name, self.redis_key)


#车辆信息  车长  体积 方   重量 吨  不做外键。
class Car_Info(db.Model):
	__tablename__ = 'car_infos'
	id = db.Column(db.Integer,primary_key=True)
	length = db.Column(db.String(80))
	tiji = db.Column(db.String(80))
	zhongliang = db.Column(db.String(80))
	sort = db.Column(db.Integer,default=10)

#车型  低栏 平板 高栏 冷藏车 等   不做外键
class Car_Type(db.Model):
	__tablename__ = 'car_types'
	id = db.Column(db.Integer,primary_key=True)
	name = db.Column(db.String(80))

#司机自助下单 货物预约表
class Driver_self_order(db.Model):
	__tablename__ = 'Driver_self_orders'
	id = db.Column(db.Integer,primary_key=True)
	driver = db.Column(db.Integer, db.ForeignKey('drivers.id'))
	goods = db.Column(db.Integer, db.ForeignKey('goods.id'))
	create_time = db.Column(db.DateTime,default=datetime.utcnow)
	#状态默认0 1审核通过  一般一条货物信息只有一个是审核通过的
	state = db.Column(db.Integer(),default=0)
	#预约价格
	price =  db.Column(db.Numeric(precision=10,scale=2,\
		asdecimal=True, decimal_return_scale=None))

#货主自助下单 车辆预约表
class Goods_self_order(db.Model):
	__tablename__ = 'goods_self_orders'
	id = db.Column(db.Integer,primary_key=True)
	driver_post = db.Column(db.Integer, db.ForeignKey('driver_posts.id'))
	consignors = db.Column(db.Integer, db.ForeignKey('consignors.id'))
	create_time = db.Column(db.DateTime,default=datetime.utcnow)
	#状态默认0 1审核通过  一般一条货物信息只有一个是审核通过的
	state = db.Column(db.Integer(),default=0)
	#预约价格
	price =  db.Column(db.Numeric(precision=10,scale=2,\
		asdecimal=True, decimal_return_scale=None))




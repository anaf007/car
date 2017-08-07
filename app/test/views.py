#coding=utf-8

from . import codetest
from flask import current_app
from app import redis_store
from app import scheduler
import random,time
from forms import AddTaskForm
from app.models import Redis_Task,Order_Task,Order_pay
from flask import request,render_template,redirect,abort,session,jsonify,url_for
from app import db
from rq import Worker, Queue, Connection
from rq.job import Job
from app.redis_worker import conn
import uuid
from redis import Redis
import logging
redis = Redis()
from app import app
# app = app._get_current_object()

from wechatpy import WeChatClient
# from flask_oauthlib.client import OAuth
# client = WeChatClient('app_id', 'secret')
# user = client.user.get('user id')
# menu = client.menu.get()
# client.message.send_text('user id', 'content')




@codetest.route('/')
def index():
	tasks = Redis_Task.query.order_by(Redis_Task.start_time.desc())
	task_lists = []
	for obj in tasks:
		dic = {}
		dic['id'] = obj.id
		dic['name'] = obj.name
		dic['redis_key'] = obj.redis_key
		dic['start_time'] = obj.start_time
		dic['expired'] = 0 if redis_store.exists(obj.redis_key) else 1
		dic['create_date'] = obj.create_date
		task_lists.append(dic)
		# todo: task执行结果回调
	return render_template('codetest/index.html', tasks=task_lists)

@codetest.route('/ramdom')
def ramdom():
	choice_str = 'ABCDEFGHJKLNMPQRSTUVWSXYZ'
	return_str = ''
	str_time =  time.time()
	return_str = str(int(int(str_time)*1.347))+return_str
	for i in range(10):
		return_str += random.choice(choice_str)
	
	return return_str


@codetest.route('/add_task', methods=['GET', 'POST'])
def add_task():
    task_id = request.args.get('tid')
    ori_task = Redis_Task.query.filter(Redis_Task.id == task_id).first()
    form = AddTaskForm()
    print ori_task
    if ori_task:
        form = AddTaskForm(name=ori_task.name, key=ori_task.redis_key, ctime=ori_task.start_time)

    if request.method == 'POST' and form.validate():
        tid = request.values.get('tid')
        str_key = form.key.data
        task = Redis_Task(form.name.data, str_key, form.ctime.data)
        if tid:
            # update
            tsObj = Redis_Task.query.filter(Redis_Task.id == tid).first()
            ori_str_key = tsObj.redis_key
            redis_store.delete(ori_str_key)
            tsObj.redis_key = str_key
            tsObj.name = form.name.data
            tsObj.start_time = form.ctime.data
            db.session.commit()
        else:
            db.session.add(task)
        print 'seconds'
        print task.seconds

        redis_store.setex(str_key,task.seconds,add(1,2))
        return redirect('/')
    return render_template('codetest/add.html', form=form)



def count_and_save_words(url):
	# errors = []
	# try:
	# 	r = requests.get(url)
	# except:
	# 	errors.append("Unable to get URL. Please make sure it's valid and try again.")
	# 	return {"error": errors}
	# # text processing
	# raw = BeautifulSoup(r.text).get_text()
	# nltk.data.path.append('./nltk_data/')  # set the path
	# tokens = nltk.word_tokenize(raw)
	# text = nltk.Text(tokens)

	# # remove punctuation, count raw words
	# nonPunct = re.compile('.*[A-Za-z].*')
	# raw_words = [w for w in text if nonPunct.match(w)]
	# raw_word_count = Counter(raw_words)

	# # stop words
	# no_stop_words = [w for w in raw_words if w.lower() not in stops]
	# no_stop_words_count = Counter(no_stop_words)

	# save the results
	from app.models import Redis_Task
	rt = Redis_Task(name='name',redis_key='7',start_time='2017-07-12 1:12')
	db.session.add(rt)
	db.session.commit()
	try:
		print 'ok'
	
	# 	result = Result(
	# 		url=url,
	# 		result_all=raw_word_count,
	# 		result_no_stop_words=no_stop_words_count
	# 	)
	# 	db.session.add(result)
	# 	db.session.commit()
	# 	return result.id
	except:
		errors.append("Unable to add item to database.")
		# return {"error": errors}
	return 'ok'


@codetest.route('/codetestindex', methods=['GET', 'POST'])
def codetestindex():
	results = {}
	# from app.redis_worker import conn
	q = Queue(connection=conn)
	
		# get url that the person has entered
	# url = request.form['url']
	url = 'url.com'
	if 'http://' not in url[:7]:
		url = 'http://' + url
	#这里好像是指 运行的函数执行多少秒  而不是多少秒后执行  不是要的结果
	job = q.enqueue_call(
		func=count_and_save_words(url), args=(url,), result_ttl=10
	)
	print(job.get_id())
	return render_template('codetest/index.html', results=results)

@codetest.route("/results/<job_key>", methods=['GET'])
def get_results(job_key):
	job = Job.fetch(job_key, connection=conn)
	if job.is_finished:
		return str(job.result), 200
	else:
		return "Nay!", 202


from pickle import loads, dumps




"""
>>> a = [1, 2, 3]  
>>> b = a  
>>> a  
[1, 2, 3]  
>>> b  
[1, 2, 3]  
>>> a.append(4)  
>>> a  
[1, 2, 3, 4]  
>>> b  
[1, 2, 3, 4]  
>>> c = pickle.dumps((a, b))  
>>> d, e = pickle.loads(c)  
>>> d  
[1, 2, 3, 4]  
>>> e  
[1, 2, 3, 4]  
>>> d.append(5)  
>>> d  
[1, 2, 3, 4, 5]  
>>> e  
[1, 2, 3, 4, 5] 
http://www.cnblogs.com/cobbliu/archive/2012/09/04/2670178.html
仔细认真阅读例子代码这个例子花了差不多一天理解
"""
@codetest.route('/add/<int:a>/<int:b>',methods=['GET'])
def add_numbers(a=0,b=0):
	if a is None or b is None:
		abort(400)
	rv = add.delay(a, b)
	session['add_result_key'] = rv.key
	return 'Waiting for result...%s'%rv.key

@codetest.route('/add-result')
def add_numbers_result():
	key = session.get('add_result_key')
	if key is None:
		return jsonify(ready=False)
	rv = DelayedResult(key)
	if rv.return_value is None:
		return jsonify(ready=False)
	redis.delete(key)
	del session['add_result_key']
	# return '1'
	return jsonify(ready=True, result=rv.return_value)


class DelayedResult(object):
	def __init__(self, key):
		self.key = key
		self._rv =  None

	@property
	def return_value(self):
		if self._rv is None:
			rv = redis.hget(current_app.config['REDIS_QUEUE_KEY'],self.key)
			if rv is not None:
				a,b,[c,e],d = loads(rv)
				self._rv = a(c,e)
		return self._rv


def queuefunc(f):
	def delay(*args, **kwargs):
		qkey = current_app.config['REDIS_QUEUE_KEY']
		key = '%s:result:%s' % (qkey, str(uuid.uuid4()))
		s = dumps((f, key, args, kwargs))
		#添加到redis  字典添加 不能使用get获取
		redis.hset(current_app.config['REDIS_QUEUE_KEY'],key,s)
		return DelayedResult(key)
	f.delay = delay
	return f

@queuefunc
def add(a=0, b=0):
	print a+b
	return a+b

"""
end
http://flask.pocoo.org/snippets/73/, 2011年的例子。
例子始终跑步起来 没办法get，只好使用hget。
发现setex定时功能在shell下定时function，
redis_store.setex(str_key,add(), task.seconds)
例子中都是以字符串数字作为传参对象。实际开发多以function作为传参
"""

from app.models import User
def job1(a):
	#不添加日志会提示错误
	logging.basicConfig()
	#数据库操作
	with app.app_context():
		u = User.query.get(1)
		# u.phone = '99999999999'
		# db.session.add(u)
		# db.session.commit()
	print a
	#删除队列任务
	scheduler.delete_job(id='job1')



def jobfromparm(**jobargs):
	id = jobargs['id']
	func = jobargs['func']
	# args = eval_r(jobargs['args'])
	trigger = jobargs['trigger']
	seconds = jobargs['seconds']
	from apscheduler.triggers.interval import IntervalTrigger
	job = scheduler.add_job(func=job1,id='job1',args=[7,],trigger=IntervalTrigger(seconds=5),replace_existing=True)
	return 'sucess'
@codetest.route('/pause')
def pausejob():
	scheduler.pause_job('job1')
	return "Success!"

@codetest.route('/remove')
def removejob():
	scheduler.delete_job(id='job1')
	return "Success!"

	
@codetest.route('/resume')
def resumejob():
	scheduler.resume_job('job1')
	return "Success!"
@codetest.route('/addjob', methods=['GET', 'POST'])
def addjob():
	# data = request.get_json(force=True)
	data = {"id":"job1","func": "job1","args":"(1, 8)","trigger":"interval","seconds":10}
	job = jobfromparm(**data)
	return '12'

import functools
from wechatpy.enterprise import WeChatClient
client = WeChatClient(app.config.get('CORP_ID'),app.config.get('SECRET'))
def oauth(method):
	@functools.wraps(method)
	def warpper(*args, **kwargs):

		code = request.args.get('code', None)
		url = client.oauth.authorize_url(request.url)
		print url
		# qr = client.oauth.qrconnect_url(url)

		if code:
			try:
				user_info = client.oauth.get_user_info(code)
			except Exception as e:
				print e.errmsg, e.errcode
				# 这里需要处理请求里包含的 code 无效的情况
				abort(403)
			else:
				session['user_info'] = user_info
		else:
			return redirect(url)

		return method(*args, **kwargs)
	return warpper


@codetest.route('/weixinlogin')
@oauth
def weixinlogin():
	user_info = session.get('user_info')
	return jsonify(data=user_info)
	
#正确的地址
"""
https://open.weixin.qq.com/connect/oauth2/authorize?appid=wxb6eb5bc8b62ee6d8&redirect_uri=http://zhongyou.tx520.cn&response_type=code&scope=snsapi_base
"""



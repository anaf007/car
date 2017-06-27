#coding=utf-8

from . import codetest
from app import redis_store
import random,time
from forms import AddTaskForm
from app.models import Redis_Task
from flask import request,render_template,redirect,abort,session,jsonify
from app import db
from rq import Worker, Queue, Connection
from rq.job import Job
from app.redis_worker import conn
import uuid

from redis import Redis
redis = Redis()

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

        redis_store.setex(str_key, 1, task.seconds)
        return redirect('/')
    return render_template('codetest/add.html', form=form)



def count_and_save_words(url):
	errors = []
	try:
		r = requests.get(url)
	except:
		errors.append("Unable to get URL. Please make sure it's valid and try again.")
		return {"error": errors}
	# text processing
	raw = BeautifulSoup(r.text).get_text()
	nltk.data.path.append('./nltk_data/')  # set the path
	tokens = nltk.word_tokenize(raw)
	text = nltk.Text(tokens)

	# remove punctuation, count raw words
	nonPunct = re.compile('.*[A-Za-z].*')
	raw_words = [w for w in text if nonPunct.match(w)]
	raw_word_count = Counter(raw_words)

	# stop words
	no_stop_words = [w for w in raw_words if w.lower() not in stops]
	no_stop_words_count = Counter(no_stop_words)

	# save the results
	try:
		return '111'
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
		return {"error": errors}


@codetest.route('/codetestindex', methods=['GET', 'POST'])
def codetestindex():
	results = {}
	from app.redis_worker import conn
	q = Queue(connection=conn)
	if request.method == "POST":
		# get url that the person has entered
		url = request.form['url']
		if 'http://' not in url[:7]:
			url = 'http://' + url
		job = q.enqueue_call(
			func=count_and_save_words, args=(url,), result_ttl=30
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


from flask import current_app
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
		# return self._rv[0](self._rv[2][0],self._rv[2][1])
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


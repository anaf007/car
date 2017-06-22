#coding=utf-8
'''
实现在线用户的统计  源自http://flask.pocoo.org/snippets/71/
只是显示了统计ip   并没有显示个数  还没有count个数
time：2017-06-19
author：anaf
'''
from app import redis_store
from datetime import datetime
import time
from flask import current_app


def mark_online(user_id):
	now = int(time.time())
	expires = now + (current_app.config['ONLINE_LAST_MINUTES'] * 60) + 10
	all_users_key = 'online-users/%d' % (now // 60)
	user_key = 'user-activity/%s' % user_id
	p = redis_store.pipeline()
	p.sadd(all_users_key, user_id)
	p.set(user_key, now)
	p.expireat(all_users_key, expires)
	p.expireat(user_key, expires)
	p.execute()


def get_user_last_activity(user_id):
	last_active = redis_store.get('user-activity/%s' % user_id)
	if last_active is None:
		return None
	return datetime.utcfromtimestamp(int(last_active))

def get_online_users():
	current = int(time.time()) // 60
	minutes = xrange(current_app.config['ONLINE_LAST_MINUTES'])
	return redis_store.sunion(['online-users/%d' % (current - x) for x in minutes])




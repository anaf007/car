

from . import codetest
from app import redis_store
import random,time

@codetest.route('/')
def index():
	redis_store.set('color','red')
	return redis_store.get('color')

@codetest.route('/ramdom')
def ramdom():
	choice_str = 'ABCDEFGHJKLNMPQRSTUVWSXYZ'
	return_str = ''
	str_time =  time.time()
	return_str = str(int(int(str_time)*1.347))+return_str
	for i in range(10):
		return_str += random.choice(choice_str)
	
	return return_str
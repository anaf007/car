#coding=utf-8
from threading import Thread
from flask_mail import Message
from app import mail,app,db
from flask_login import current_user
from sqlalchemy import inspect
def send_async_email(msg):
	with app.app_context():
		try:
			mail.send(msg)
			insp = inspect(current_user)
			insp.persistent
		except Exception, e:
			print str(e)
		

def send_email(body):
	msg = Message(subject=u'公众号调度猿错误邮件提醒',sender=app.config['MAIL_USERNAME'],recipients=['6471750@qq.com'])
	msg.html = body
	mail.send(msg)
	# thr = Thread(target=send_async_email(msg))
	# thr.start()
	# return thr

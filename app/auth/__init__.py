#coding=utf-8
"""filename:app/auth/__init__.py
Created 2017-05-30
Author: by anaf
note:auth初始化函数
"""

from flask import Blueprint,current_app,session

auth = Blueprint('auth',__name__)

from . import views 


import random,string
from datetime import datetime
try:
	from PIL import Image,ImageDraw,ImageFont,ImageFilter
except Exception, e:
	import Image,ImageDraw,ImageFont,ImageFilter


# 随机字母:
def rndChar():
	str = ''
	for i in range(4):
		str += chr(random.randint(65, 90))
	return str

# 随机颜色1:
def rndColor():
    return (random.randint(64, 255), random.randint(64, 255), random.randint(64, 255))

# 随机颜色2:
def rndColor2():
    return (random.randint(32, 127), random.randint(32, 127), random.randint(32, 127))


def generate_verification_code():
	width = 70
	height = 30
	image = Image.new('RGB',(width,height),(255,255,255))
	#字体对象
	font = ImageFont.truetype('Arial.ttf', 18)
	draw = ImageDraw.Draw(image)
	for x in range(width):
		for y in range(height):
			draw.point((x, y), fill=rndColor())
	verify_str = rndChar() 

	draw.text((10, 5),verify_str, font=font, fill=rndColor2())

	#模糊
	# image = image.filter(ImageFilter.BLUR)
	li = []
	for i in range(10):
		temp = random.randrange(65,90)
		c = chr(temp)
		li.append(c)
	filename = "".join(li)
	

	image.save(current_app.static_folder+'/code/'+filename+'.jpg', 'jpeg');
	session['verify'] = verify_str
	return '/static/code/'+filename+'.jpg'


#请求上下文 ，获取验证码
@auth.context_processor
def get_verify():
    def get():
    	return generate_verification_code()
    return dict(get_verify=get)
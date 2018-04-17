#coding=utf-8
"""filename:app/main/views.py
Created 2017-05-29
Author: by anaf
"""

from flask import render_template,redirect,url_for,request,\
flash,current_app,make_response,Response,abort,session,jsonify
from . import main
from .. import db
from ..models import Permission,Goods,User_msg,Order_pay,User,Position,Driver_post,Driver_self_order
from  flask_login import login_required,current_user
from ..decorators import admin_required,permission_required
from .forms import PostForm,CommentForm
import os,random,datetime,hashlib,functools,json
# from app.online_user import get_online_users,mark_online

from app import wechat,flask_wechat
from flask_wechatpy import Wechat, wechat_required
from wechatpy.replies import TextReply,ArticlesReply,create_reply
from wechatpy.utils import check_signature
from wechatpy.crypto import WeChatCrypto
from wechatpy import parse_message
from wechatpy.pay import WeChatPay
import xml.etree.ElementTree as ET
# from app import client
from wechatpy.oauth import WeChatOAuth



#微信文件读取 根目录
@main.route('/<path>')
def MP_verify_iyiVrtXIRP2uczyn(path):
    try:
        if path =="MP_verify_iyiVrtXIRP2uczyn.txt":
            resp = make_response(open('/home/www/car/'+path).read())
            resp.headers["Content-type"]="application/json;charset=UTF-8"
            return resp
        else:   
            return ''
    except Exception, e:
        return ''

@main.route('/')
@login_required
def index():
    msg = current_user.user_msgs.filter_by(state=0).first()
    return render_template('main/index.html',msg=msg)

@main.route('/index')
def index_main():
    return 'index'

@main.route('/driver_postion/<lng>/<lat>')
def driver_postion(lng='',lat=''):
    try:
        if lng:
            db.session.add(Position(latitude=lat,longitude=lng,precision='1',user=current_user))
            db.session.commit()
    except Exception, e:
        return ''
    
    return ''



#司机支付订单，显示
@main.route('/sijizhifu/')
@login_required
def sijizhifu():
    try:
        orderpay = Order_pay.query.filter(Order_pay.user==current_user).filter(Order_pay.state==0).first()
        if not orderpay:
            flash(u'该订单已支付。','error') 
            return redirect(url_for('main.index'))
        pay = WeChatPay(appid='wxbdd2d9798f27f33a',\
            api_key='lY4TatJV1W2XhqYmdP2McP8JtrE1mTCk',mch_id='1488590922',\
            mch_cert=r'/home/www/car_cert/apiclient_cert.pem',\
            mch_key=r'/home/www/car_cert/apiclient_key.pem')
        price = int(float(orderpay.pay_price)*100)
        result = pay.order.create(trade_type='JSAPI',body=u'司机定金支付订单：%s'%orderpay.order,\
            total_fee=price,notify_url='http://car.anaf.cn/sijizhifu_confirm',\
            user_id=current_user.wx_open_id,out_trade_no=orderpay.order)
        params = pay.jsapi.get_jsapi_params(result['prepay_id'])
        return render_template('main/sijizhifu.html',op=orderpay, params=json.dumps(params))
    except Exception, e:
        print str(e)
        flash(u'该订单已支付。%s'%str(e),'error') 
        return redirect(url_for('main.index'))
    
        
    


#确认支付 此处应该有定时任务 微信支付链接
@main.route('/sijizhifu_confirm', methods=['GET', 'POST'])
@login_required
def zhifudingjin_confirm():
    try:
        op = Order_pay.query.filter(Order_pay.user==current_user).filter(Order_pay.state==0).first()
        pay = WeChatPay(appid='wxbdd2d9798f27f33a',\
        api_key='lY4TatJV1W2XhqYmdP2McP8JtrE1mTCk',mch_id='1488590922',\
        mch_cert=r'/home/www/car_cert/apiclient_cert.pem',\
        mch_key=r'/home/www/car_cert/apiclient_key.pem')
        result = []
        if op:
            result = pay.order.query(out_trade_no=op.order)


        if result.get('return_code') == 'SUCCESS':
            #获取未订单            
            op.state = 2 #支付完成
            op.goodsed.state = 2 #已支付完成
            # msg = User_msg.query.filter(User_msg.state==0).filter(User_msg.user==current_user).first()
            db.session.add(op)
            # msg.state = 2  #已经支付定金确认用户消息
            # msg.body = u'您已经确认支付了该条支付信息。原信息：'+msg.body
            flask_wechat.message.send_text(op.goodsed.consignor.user.wx_open_id,u'司机已经确认了您的货物信息，将在指定时间前来装货，如果超时未到，您可进行投诉将视为司机违约将返还您一定的损失。')

            # db.session.add(msg)
            db.session.commit()

    except Exception, e:
        print str(e)
        return abort(404)
    
    # return 'FAIL'
    return render_template('main/zhifudingjin_confirm.html')


#货主支付订单，显示
@main.route('/huozhuzhifu/')
@login_required
def huozhuzhifu():
    try:
        orderpay = Order_pay.query.filter(Order_pay.user==current_user).filter(Order_pay.state==0).first()
        pay = WeChatPay(appid='wxbdd2d9798f27f33a',\
            api_key='lY4TatJV1W2XhqYmdP2McP8JtrE1mTCk',mch_id='1488590922',\
            mch_cert=r'/home/www/car_cert/apiclient_cert.pem',\
            mch_key=r'/home/www/car_cert/apiclient_key.pem')
        price = int(float(orderpay.pay_price)*100)
        result = pay.order.create(trade_type='JSAPI',body=u'货主运费支付，订单：%s'%orderpay.order,\
            total_fee=price,notify_url='http://car.anaf.cn/sijizhifu_confirm',\
            user_id=current_user.wx_open_id,out_trade_no=orderpay.order)
        params = pay.jsapi.get_jsapi_params(result['prepay_id'])
        return render_template('main/huozhuzhifu.html',op=orderpay, params=json.dumps(params))
    except Exception, e:
        print str(e)
        return ''


@main.route('/huozhuzhifu_confirm')
@login_required
def huozhuzhifu_confirm():
    try:
        op = Order_pay.query.filter(Order_pay.user==current_user).filter(Order_pay.state==0).first()
        pay = WeChatPay(appid='wxbdd2d9798f27f33a',\
        api_key='lY4TatJV1W2XhqYmdP2McP8JtrE1mTCk',mch_id='1488590922',\
        mch_cert=r'/home/www/car_cert/apiclient_cert.pem',\
        mch_key=r'/home/www/car_cert/apiclient_key.pem')
        result = []
        if op:
            result = pay.order.query(out_trade_no=op.order)

        if result.get('return_code') == 'SUCCESS':
            #获取未订单            
            op.state = 2 #支付完成
            op.goodsed.state = 2 #已支付完成
            op.goodsed.price_is_pay = 1 # 货主已经付款
            # msg = User_msg.query.filter(User_msg.state==0).filter(User_msg.user==current_user).first()
            
            op.driver.user.lock_price += op.pay_price
            db.session.add(op)

            flask_wechat.message.send_text(op.driver.user.wx_open_id,u'货主完成了运费的在线支付，您的账户已入账：%s元。'%op.pay_price)

            # db.session.add(msg)
            db.session.commit()

    except Exception, e:
        print str(e)
        return ''
    
    return render_template('main/huozhuzhifu_confirm.html')
    
    
    


@main.route('/driver_self_confirm/<int:id>')
def driver_self_confirm(id=0):
    goods = Goods.query.get_or_404(id)
    if goods.state ==2:
        goods.state=3
        db.session.add(goods)
        db.session.commit()
        flask_wechat.message.send_text(goods.consignor.user.wx_open_id,u'司机完成了您的运输，请及时到“个人中心-货运信息”里查看确认。')

    else:
        return redirect(url_for('main.index'))
    
    
    return redirect(url_for('usercenter.selforder'))


#ckeditor图片上传
def gen_rnd_filename():
    filename_prefix = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    return '%s%s' % (filename_prefix, str(random.randrange(1000, 10000)))

@main.route('/main/upload', methods=['GET','POST'])
@login_required
def UploadFileImage():
    """CKEditor file upload"""
    error = ''
    url = ''
    callback = request.args.get("CKEditorFuncNum")
    if request.method == 'POST' and 'upload' in request.files:
        fileobj = request.files['upload']
        fname, fext = os.path.splitext(fileobj.filename)
        rnd_name = '%s%s' % (gen_rnd_filename(), fext)
        filepath = os.path.join(current_app.static_folder, 'uploads/main', rnd_name)
        
        dirname = os.path.dirname(filepath)
        if not os.path.exists(dirname):
            try:
                os.makedirs(dirname)
            except:
                error = 'ERROR_CREATE_DIR'
        elif not os.access(dirname, os.W_OK):
            error = 'ERROR_DIR_NOT_WRITEABLE'
        if not error:
            fileobj.save(filepath)
            url = url_for('static', filename='%s/%s' % ('uploads/main', rnd_name))
    else:
        error = 'post error'
    res = """

        <script type="text/javascript">
          window.parent.CKEDITOR.tools.callFunction(%s, '%s', '%s');
        </script>

 """ % (callback, url, error)
    response = make_response(res)
    response.headers["Content-Type"] = "text/html"
    return response



#请求上下文 栏目的上级目录的读取
@main.context_processor
def Get_Nav():
    def get(id):
        pid =  Category.query.filter_by(category_top_id=url).first().pid
        if pid ==0:
            return []
        return Navcat.query.filter_by(pid=pid).order_by('sort').all()
        
    return dict(Get_Nav=get)






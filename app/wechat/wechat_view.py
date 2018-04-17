#coding=utf-8

from flask import render_template,abort,request,current_app,url_for,make_response,flash,redirect,session
from . import wechat
from flask_wechatpy import wechat_required
from app import db,app,flask_wechat
from wechatpy.replies import TextReply,ArticlesReply,create_reply,ImageReply
from app.models import User,Position,Haoyoutuijian,Role,Driver,Driver_self_order
from flask_login import current_user
import time,random
from ..errorSendMail import send_email
def createmenu():
    flask_wechat.menu.create({"button":[
        {"type":"view","name":u"我要找货","sub_button":[
            {
                "type":"view",
                "name":u"我发布的车",
                "url":'http://car.anaf.cn/usercenter/show_order'
            },
            {
                "type":"view",
                "name":u"发布车信息",
                "url":'http://car.anaf.cn/driver/add_post'
            },
            {
                "type":"view",
                "name":u"货物列表",
                "url":'http://car.anaf.cn/consignor'
            },
            ]},\
        {"type":"view","name":u"我要找车","sub_button":[
        {
                "type":"view",
                "name":u"我发布的货",
                "url":'http://car.anaf.cn/usercenter/show_order'
            },
            {
                "type":"view",
                "name":u"发布货信息",
                "url":'http://car.anaf.cn/consignor/send_goods'
            },
            {
                "type":"view",
                "name":u"车辆列表",
                "url":'http://car.anaf.cn/driver'
            },
            ]},\
        {"type":"view","name":u"我的服务","sub_button":[
        {
                "type":"view",
                "name":u"平台简介",
                "url":'https://s.wcd.im/v/2efu6Z37/'
            },
            {
                "type":"click",
                "name":u"联系方式",
                "key":'contact_us'
            },
            {
                "type":"view",
                "name":u"个人中心",
                "url":'http://car.anaf.cn/usercenter'
            },
            ]},\
        ]})



def autoregister(wx_id):
    if User.query.filter_by(wx_open_id=wx_id).first():
        return
    
    choice_str = 'ABCDEFGHJKLNMPQRSTUVWSXYZ'
    username_str = ''
    password_str = ''
    str_time =  time.time()
    username_str = 'AU'
    username_str += str(int(int(str_time)*1.301))
    for i in range(2):
        username_str += random.choice(choice_str)

    for i in range(6):
        password_str += random.choice(choice_str)

    username = username_str
    password = password_str

    user = User.query.filter_by(username=username).first()
    if user is None:
        user = User(username=username,password=password,wx_open_id=wechat_id,pay_pwd='111111')
        user_info = User_info(user=user)
        db.session.add(user)
        db.session.add(user_info)
        db.session.commit()
    else:
        rautoregister()

#微信获取token
@wechat.route('/token',methods=['GET'])
@wechat_required
def get_token():
    signature = request.args.get('signature','')
    timestamp = request.args.get('timestamp','')
    nonce = request.args.get('nonce','')
    echostr = request.args.get('echostr','')
    token = 'wx_get_token_1234567890acb'
    sortlist = [token, timestamp, nonce]
    sortlist.sort()
    sha1 = hashlib.sha1()
    map(sha1.update, sortlist)
    hashcode = sha1.hexdigest()
    try:
        check_signature(token, signature, timestamp, nonce)
    except InvalidSignatureException:
        abort(403)
    return echostr



#微信调用 位置和token等其他相关
@wechat.route('/token',methods=['POST'])
@wechat_required
def post_post():
    msg = request.wechat_msg
    reply = TextReply(content='欢迎关注调度猿.\
           \n如果您是司机想要拉货，<a href="http://car.anaf.cn/consignor">请点击这里</a>.\
           \n如果您是货主想要找车，<a href="http://car.anaf.cn/driver">请点击这里</a>.', message=msg)
    

    # 获取到的文本信息
    if msg.type == 'text':
        reply = reply
        user_id = msg.content[0:-13]
        juese = msg.content[-13:-11]
        haoma = msg.content[-11:]
        if juese== u'司机':
            if user_id.isdigit() and haoma.isdigit():
                try:
                    
                    tuijianren = User.query.get_or_404(int(user_id))
                    beituijianren = User.query.filter_by(wx_open_id=msg.source).first()
                    if not beituijianren:
                        return reply
                    shifouyituijian = Haoyoutuijian.query.filter(Haoyoutuijian.tuijianren==tuijianren.id).filter(Haoyoutuijian.beituijianren==beituijianren.id).first()
                    if shifouyituijian:
                        return reply
                    savetuijianren = Haoyoutuijian()
                    savetuijianren.tuijianren = tuijianren.id
                    savetuijianren.beituijianren = beituijianren.id
                    r = Role.query.filter_by(name=u'司机').first()
                    beituijianren.role = r
                    beituijianren.phone = haoma
                    tuijianren.user_infos.recommended += 1 


                    d = Driver()
                    d.user = beituijianren #创建者
                    d.phone = haoma
                    d.number = u'未知车牌、'
                    d.length = u'未知车长'
                    d.note = u'默认车辆信息，联系电话'+haoma
                    d.driver_user = beituijianren 


                    db.session.add(d)
                    db.session.add(tuijianren)
                    db.session.add(beituijianren)
                    db.session.add(savetuijianren)
                    db.session.commit()


                    try:
                        flask_wechat.message.send_text(tuijianren.wx_open_id,\
                        u'好友%s已经确认了您的推荐信息。</a>'%haoma)
                    except Exception, e:
                        pass
                    reply = TextReply(content='您已经确认了好友的推荐.\
            \n<a href="http://car.anaf.cn/consignor">点击这里开始拉货.', message=msg)
    
                except Exception, e:
                    db.session.rollback()
                    return reply
        # if juese== u'货主':
        #     if user_id.isdigit() and haoma.isdigit():
        #         try:
        #             tuijianren = User.query.get_or_404(int(user_id))
        #             tuijianren = User.query.get_or_404(int(user_id))
        #             current_user.role.name = u'货主'
        #             current_user.phone = haoma
        #             db.session.add(current_user)
        #             db.session.commit()
        #         except Exception, e:
        #             return reply
        #货预约货主同意价格
        if msg.content[0:2] == 'cy':
            try:
                stoid = msg.content[2:]
                dso = Driver_self_order.query.get(stoid)
                if not dso:
                    reply = TextReply(content=u'输入错误',message=msg)
                    return reply
                if dso.goodsed.consignor.user.wx_open_id != msg.source:
                    reply = TextReply(content=u'输入错误',message=msg)
                    return reply
                if dso.state != 0:
                    reply = TextReply(content=u'输入错误',message=msg)
                    return reply
            except Exception, e:
                reply = TextReply(content=u'输入错误',message=msg)
                return reply
            
            dso.state = 3
            db.session.add(dso) 
            db.session.commit()
            #推送消息给管理员或指定客服。
            try:
                flask_wechat.message.send_text('otCWCxPJxCSn6xuEE9UHzO544SvA',u'货物编号:%s 的货主同意了司机的预约请求，请进入后台查看双方身份信息认证。'%(dso.goodsed.id))
            except Exception, e:
                send_email(u'货主同意预约价格通知错误。%s'%(current_user.phone,str(e)))
            reply = TextReply(content=u'您已经确认了该预约的价格，客服正在联系司机。稍后会电话联系您。',message=msg)
            return  reply

        if msg.content[0:2] == 'hw':
            reply = TextReply(content=u'<a href="http://car.anaf.cn/consignor/show_goods/%s">点击查看货物信息</a>'%msg.content[2:],message=msg)
                
    try:
        if msg.key =='contact_us':
            # reply = ImageReply(message=msg)
            # reply.media_id = 'AgFuILMkm_Xo_UdtuZDwqrHPwUbQCxi3ay1aCI9vxtQ'
            reply = TextReply(content=u'欢迎关注调度猿.\n您的支持给予了我们动力，\n我们的电话是：<a href="tel:15907711863">15907711863</a>.任何问题您都可以电话咨询我们，\n我们竭诚为您服务。',message=msg)
    except Exception, e:
        pass


    try:
        msg.event
    except Exception, e:
        return reply

    #扫描二维码关注事件
    if msg.event == 'subscribe_scan':
        autoregister(msg.source)

        try:
            reply = TextReply(content='欢迎关注调度猿.\
            \n如果您是司机,请回复“%s司机+您的手机号”\
            \n如果您是货主,请回复“%s货主+您的手机号”\
            \n如：%s司机15907711863'%(str(msg.scene_id),str(msg.scene_id),str(msg.scene_id)), message=msg)
            #创建菜单
            createmenu()
        except Exception, e:
            pass
    
        
    #关注事件
    if msg.event == 'subscribe':
        autoregister(msg.source)
        reply = TextReply(content='欢迎关注调度猿.\
            \n如果您是司机想要拉货，<a href="http://car.anaf.cn/consignor">请点击这里</a>.\
            \n如果您是货主想要找车，<a href="http://car.anaf.cn/driver">请点击这里</a>.\
            \n <a href="https://hd.faisco.cn/15080030/Uuhfnzv3KkQ35xQRFUCppg/load.html?style=2">点击砸金蛋赢奖品</a>', message=msg)
        #创建菜单
        createmenu()
        
    #取消关注事件
    if msg.event == 'unsubscribe':
        try:
            user = User.query.filter_by(wx_open_id=msg.source).first() 
            user.is_location = 0
            db.session.add(user)
            db.session.commit()
        except Exception, e:
            reply = ''
        reply = ''
        
            
    #定位事件
    if msg.event =='location': 
        try:
            user = User.query.filter_by(wx_open_id=msg.source).first() 
        except Exception, e:
            user = []
        #不发送
        reply = ''
        #图文消息
        # reply = ArticlesReply(message=msg,articles=[])
        # reply.add_article({'title': u'标题3','description': u'描述3','url': u'http://www.qq.com',})
        try:
            #如果已经注册，添加位置
            if user:
                if user.is_location == 0:
                    user.is_location = 1
                    db.session.add(user)
                db.session.add(Position(latitude=msg.latitude,longitude=msg.longitude,precision=msg.precision,user=user))
                db.session.commit()
        except Exception, e:
            reply = ''

    
        
    
    return reply








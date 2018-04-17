#coding=utf-8
"""filename:app/main/views.py
Created 2017-05-29
Author: by anaf
"""

from flask import render_template,redirect,url_for,request,flash,current_app,make_response,Response,abort,session,jsonify
from . import main
from .. import db
from ..models import Article,Comment,Permission,CategoryTop,\
    Category,Goods,User_msg,Order_pay,User,Position
from  flask_login import login_required,current_user
from ..decorators import admin_required,permission_required
from .forms import PostForm,CommentForm
import os,random,datetime,hashlib,functools
from app.online_user import get_online_users,mark_online

from app import wechat
from flask_wechatpy import Wechat, wechat_required,oauth
from wechatpy.replies import TextReply,ArticlesReply,create_reply
from wechatpy.utils import check_signature
from wechatpy.crypto import WeChatCrypto
from wechatpy import parse_message
import xml.etree.ElementTree as ET



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

@main.route('/wxinfo')
@oauth(scope='snsapi_userinfo')
def fwxinfo():
    print 'id:',session.get('wechat_user_id')
    user = wechat.user.get(session.get('wechat_user_id'))
    try:
    	print user['nickname']
    except Exception, e:
    	print 'nickname null'
    	
    return session.get('wechat_user_id')





#微信获取token
@main.route('/wx/wx_get_token',methods=['GET'])
@wechat_required
def wx_token():
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

# def reply_text(to_user, from_user, content):
#     return """<xml>
#         <ToUserName><![CDATA[{}]]></ToUserName>
#         <FromUserName><![CDATA[{}]]></FromUserName>
#         <CreateTime>{}</CreateTime>
#         <MsgType><![CDATA[text]]></MsgType>
#         <Content><![CDATA[{}]]></Content>
#         </xml>
#         """.format(to_user, from_user, int(time.time() * 1000), content)
# def reply(openid, msg):
#     return msg[::-1]

#微信调用 位置和token等其他相关
@main.route('/wx/wx_get_token',methods=['POST'])
@wechat_required
def wx_post():
    msg = request.wechat_msg
    try:
        user = User.query.filter_by(wx_open_id=msg.source).first() 
    except Exception, e:
        user = []
    
    if user:
        if user.role.name == u'普通用户':
            wechat.menu.create({"button":[\
                {"type":"view","name":u"找车","url":url_for('driver.index',_external=True)},\
                {"type":"view","name":u"找货","url":url_for('goods.index',_external=True)}]})
        elif user.role.name == u'司机':
            wechat.menu.create({"button":[\
                {"type":"view","name":u"发布信息","url":url_for('driver.add_post',_external=True)},\
                {"type":"view","name":u"我要找货","url":url_for('goods.index',_external=True)},\
                {"type":"view","name":u"个人中心","url":url_for('usercenter.index',_external=True)},\
                ]})
        elif user.role.name == u'货主':
            wechat.menu.create({"button":[\
                {"type":"view","name":u"发布信息","url":url_for('goods.send_goods',_external=True)},\
                {"type":"view","name":u"我要找车","url":url_for('driver.index',_external=True)},\
                {"type":"view","name":u"个人中心","url":url_for('usercenter.index',_external=True)},\
                ]})
        else:
            wechat.menu.create({"button":[\
                {"type":"view","name":u"找车","url":url_for('driver.index',_external=True)},\
                {"type":"view","name":u"找货","url":url_for('goods.index',_external=True)},\
                {"type":"view","name":u"个人中心","url":url_for('usercenter.index',_external=True)}]})


    
    
    
    
    if msg.type == 'text':
        reply = create_reply(msg.content, message=msg)
    elif msg.event =='location':  #进入公众号事件
        text = u"欢迎关注调度猿,平台已有7801辆车签约，今日已成交189个订单。"
        #文字消息
        # reply = TextReply(content=text, message=msg)
        #不发送
        reply = ''
        #图文消息
        # reply = ArticlesReply(message=msg,articles=[])
        # reply.add_article({'title': u'标题3','description': u'描述3','url': u'http://www.qq.com',})
        try:
            #如果已经注册，添加位置
            if user:
                db.session.add(Position(latitude=msg.latitude,longitude=msg.longitude,precision=msg.precision,user_position=user))
                db.session.commit()
        except Exception, e:
            print str(e)
    else:
        reply = TextReply(content='欢迎关注调度猿.', message=msg)
    return reply



#顶级栏目
@main.route('/nav_top/<int:id>')
def nav_top(id=0):
    #
    one = CategoryTop.query.get_or_404(id)
    categorts = CategoryTop.query.all()
    #获取父栏目下子栏目下所有文章
    article = Article.query.join(Category,Category.id==Article.category_id).\
        join(CategoryTop,CategoryTop.id==Category.category_top_id).\
        filter(Category.category_top_id==one.id).all()
    return render_template(one.template,one=one,nav=categorts,articles=article,one_top=one)

#栏目
@main.route('/nav/<int:id>')
def nav(id=0):
    one = Category.query.get_or_404(id)
    categorts = CategoryTop.query.all()
    one_top = CategoryTop.query.get_or_404(one.category_top_id)
    article_list = Article.query.filter_by(category_id=one.id).all()
    return render_template(one.template,one=one,nav=categorts,one_top=one_top,article=article_list)

#文章
@main.route('/article/<int:id>')
def article(id=0):
    articles = Article.query.get_or_404(id)
    categorts = CategoryTop.query.all()
    one = Category.query.get_or_404(articles.category_id)
    one_top = CategoryTop.query.get_or_404(one.category_top_id)
    return render_template('article.html',
                        article=articles,nav=categorts,
                        one=one,one_top=one_top)
 
@main.route('/')
@login_required
def index():
    return render_template('main/index.html')

@main.route('/index')
def index_main():
    print url_for('driver.index',_external=True)
    print url_for('driver.add_post',_external=True)
    print url_for('goods.send_goods',_external=True)
    print url_for('usercenter.index',_external=True)
    return 'index'

#需要登陆访问
@main.route('/main_login/')
@login_required
def main_login():
    return render_template('main/index.html')


#需要登陆，且需要管理员权限
@main.route('/admin_main')
@login_required
@admin_required
def for_admin_only():
	return "for admin"


#需要登陆，且定义权限的函数
@main.route('/moderator')
@login_required
@permission_required(Permission.WRITE_ARTICLES)
def for_moderators_only():
	return "for coment moderators"



@main.route('/post',methods=['GET','POST'])
@main.route('/post/<int:page>',methods=['GET','POST'])
def post(page=1):
	form = PostForm()
	if current_user.can(Permission.WRITE_ARTICLES) and \
		form.validate_on_submit():
		post = Article(title=form.title.data,body=form.body.data,author=current_user._get_current_object())
		db.session.add(post)
		db.session.commit()
		return redirect(url_for('.post'))
	pagination = Article.query.order_by(Article.timestamp.desc()).paginate(page,per_page=10,error_out=False)
	posts = pagination.items
	return render_template('post.html',form=form,posts=posts,pagination=pagination)

@main.route('/show_post/<int:id>',methods=['GET', 'POST'])
def show_post(id):
	post = Article.query.get_or_404(id)
	form = CommentForm()
	if form.validate_on_submit():
		comment = Comment(body=form.body.data,post=post,author=current_user._get_current_object())
		db.session.add(comment)
		db.session.commit()
		flash('Your comment has been published.')
		return redirect(url_for('.show_post', id=post.id, page=-1))
	page = request.args.get('page', 1, type=int)
	if page == -1:
		page = (post.comments.count() - 1) / 10 + 1
	pagination = post.comments.order_by(Comment.timestamp.asc()).paginate(page, per_page=10,error_out=False)
	comments = pagination.items
	return render_template('_post.html', post=post, form=form,comments=comments, pagination=pagination)



#支付订单，显示
@main.route('/zhifudingjin')
@login_required
def zhifudingjin():
    op = Order_pay.query.filter(Order_pay.order_pay_user==current_user).filter(Order_pay.state==0).first()
    print op
    # msg = User_msg.query.filter(User_msg.user_msg==current_user).filter(User_msg.state==0).first()
    return render_template('main/zhifudingjin.html',op=op)

#确认支付 此处应该有定时任务 微信支付链接
@main.route('/zhifudingjin_confirm')
@login_required
def zhifudingjin_confirm():
    #获取未订单
    op = Order_pay.query.filter(Order_pay.order_pay_user==current_user).filter(Order_pay.state==0).first()
    op.state = 2 #支付完成
    op.goods_order_pay.state = 2 #订单完成
    msg = User_msg.query.filter(User_msg.state==0).filter(User_msg.user_msg==current_user).first()
    db.session.add(op)
    msg.state = 2
    msg.body = u'您已经确认支付了该条支付信息'
    
    db.session.add(msg)
    db.session.commit()
    return render_template('main/zhifudingjin_confirm.html')

@main.route('/driver_self_confirm/<int:id>')
def driver_self_confirm(id=0):
    goods = Goods.query.get_or_404(id)
    goods.state=3
    db.session.add(goods)
    db.session.commit()
    return redirect(url_for('usercenter.index'))


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


#在线人数 但是并不是显示总是  未使用G
@main.route('/online')
def online():
    return Response('Online: %s' % ', '.join(get_online_users()),mimetype='text/plain')

@main.route('/mark_online')
def mark_online():
    return Response('Online: %s' % ', '.join(mark_online()))





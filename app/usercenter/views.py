#coding=utf-8
"""filename:app/users/views.py
Created 2017-05-29
Author: by anaf
"""

from flask import render_template,abort,request,current_app,url_for,make_response,flash,redirect,session
from . import usercenter
from .. import db
import random,os,datetime
from  flask_login import login_required,current_user
from  ..models import Permission,User,Driver,Order_pay,Tixianchengqing,Goods
from app.decorators import permission_required
from app import flask_wechat

@usercenter.route('/index')
@usercenter.route('/')
@usercenter.route('/<username>')
@login_required
def index(username=''):
    if current_user.role.name==u'普通用户':
        return redirect(url_for('main.index'))
    try:
        user = flask_wechat.user.get(current_user.wx_open_id)
        if user['headimgurl']:
            headimgurl = user['headimgurl']
        else:
            headimgurl = ''
    except Exception, e:
        headimgurl = ''
    return render_template('user/index.html',user=current_user,headimgurl=headimgurl)

@usercenter.route('/edit_profile')
def edit_profile():
	return render_template('user/edit_profile.html',form=current_user)

@usercenter.route('/edit_profile',methods=['POST'])
def edit_profile_post():
	users = User.query.get_or_404(current_user.id)
	users.about_me = request.form.get('about_me')
	users.name = request.form.get('name')
	db.session.add(users)
	db.session.commit()
	flash(u'修改完成')
	return redirect(url_for('.edit_profile'))


#ckeditor图片上传
def gen_rnd_filename():
    filename_prefix = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    return '%s%s' % (filename_prefix, str(random.randrange(1000, 10000)))

@usercenter.route('/upload', methods=['GET', 'POST'])
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
        filepath = os.path.join(current_app.static_folder, 'upload/user', rnd_name)
        
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
            url = url_for('static', filename='%s/%s' % ('upload/user', rnd_name))
    else:
        error = 'post error'
    res = """

        <script type="text/javascript">
          window.parent.CKEDITOR.tools.callFunction(%s, '%s', '%s');
        </script>

        """% (callback, url, error)
    response = make_response(res)
    response.headers["Content-Type"] = "text/html"
    return response



#货运信息
@usercenter.route('/huoyunxinxi')
@login_required
def huoyunxinxi():
    op = Order_pay.query.filter(Order_pay.user==current_user).order_by(Order_pay.id.desc()).all()
    return render_template('user/huoyunxinxi.html',op=op)

#显示订单
@usercenter.route('/show_order')
@login_required
def show_order():
    return render_template('user/show_order.html')

#用小消息列表
@usercenter.route('/msg_list')
@login_required
def msg_list():
    return render_template('user/msg_list.html')

#预约信息
@usercenter.route('/mark')
@login_required
def mark():
    return render_template('user/mark.html')

#车辆信息
@usercenter.route('/car')
@login_required
def car():
    return render_template('user/car.html')


#我的信息
@usercenter.route('/userinfo')
@login_required
def userinfo():
    return render_template('user/userinfo.html')

#我的钱包
@usercenter.route('/apay')
@login_required
def apay():
    return render_template('user/apay.html')

#货运专线
@usercenter.route('/freight_line')
@login_required
def freight_line():
    return render_template('user/freight_line.html')

#推荐拿奖
@usercenter.route('/tuijiannajiang')
@login_required
def tuijiannajiang():
    res = flask_wechat.qrcode.create({
        'expire_seconds': 1800,
        'action_name': 'QR_SCENE',
        'action_info': {
            'scene': {'scene_id': current_user.id},
            }
        })
    # return '<img src="%s" width="300" height="300">'%flask_wechat.qrcode.get_url(res)
    imgstr = flask_wechat.qrcode.get_url(res)
    return render_template('user/tuijiannajiang.html',imgstr=imgstr)

#用户设置
@usercenter.route('/setting')
@login_required
def setting():
    return render_template('user/setting.html')

#自身接单下单
@usercenter.route('/self_order')
def selforder():
    op = Order_pay.query.filter(Order_pay.user==current_user).order_by(Order_pay.id.desc()).all()
    return render_template('user/selforder.html',op=op)

#修改支付密码
@usercenter.route('/change_pay_pwd')
@login_required
def change_pay_pwd():
    return render_template('user/change_pay_pwd.html')


#修改支付密码
@usercenter.route('/change_pay_pwd',methods=['POST'])
@login_required
def change_pay_pwd_p():
    old_pwd = request.form.get('old_pwd','')
    new_pwd = request.form.get('new_pwd','')
    re_new_pwd = request.form.get('re_new_pwd','')
    if not old_pwd or not new_pwd or not re_new_pwd or len(new_pwd)<6 or len(new_pwd)>18 or not current_user.verify_pay_pwd(old_pwd) or new_pwd!=re_new_pwd:
        flash(u'输入错误或验证错误，请重新输入','error')
        return redirect(url_for('.change_pay_pwd'))
    current_user.pay_pwd = new_pwd
    db.session.add(current_user)
    db.session.commit()
    flash(u'支付密码修改成功。','success')
    return redirect(url_for('.change_pay_pwd'))

#银行卡
@usercenter.route('/yinhangka')
@login_required
def yinhangka():
    return render_template('user/yinhangka.html')

@usercenter.route('/yinhangka',methods=['POST'])
@login_required
def yinhangka_p():
    suoshuyinhang = request.form.get('suoshuyinhang','')
    kaihuhang = request.form.get('kaihuhang','')
    kahao = request.form.get('kahao','')
    if not current_user.user_infos.kahao:
        current_user.user_infos.kahao = kahao
        current_user.user_infos.suoshuyinhang = suoshuyinhang
        current_user.user_infos.kaihuhang = kaihuhang
    try:
        db.session.add(current_user)
        db.session.commit()
        flash(u'添加银行卡完成。','success')
    except Exception, e:
        flash(u'添加银行卡失败。','error')
    return redirect(url_for('.yinhangka'))

#提现申请
@usercenter.route('/tixianshenqing',methods=['POST'])
@login_required
def tixianshenqing():
    zhifumima = request.form.get('zhifumima','')
    try:
        if session['zhifumima']>=5:
            flash(u'输入错误次数过多，请明天再试。','error')
            return redirect(url_for('.apay'))
    except Exception, e:
        session['zhifumima'] = 0
    if current_user.verify_pay_pwd(zhifumima):
        tcq = Tixianchengqing()
        tcq.user = current_user
        tcq.price = current_user.price
        current_user.price = 0
        tcq.note = current_user.user_infos.kahao+ u" 金额："+str(tcq.price) + '.'
        try:
            db.session.add(tcq)
            db.session.add(current_user)
            db.session.commit()
            flash(u'提现申请成功，款项将在3天内打进您的银行账户','success')
        except Exception, e:
            flash(u'提现失败','error')
            db.session.rollback()
        session['zhifumima'] = 0
    else:
        session['zhifumima'] = session['zhifumima']+1
    return redirect(url_for('.apay'))


#货主确认完成
@usercenter.route('/consignor_finish/<int:opid>',methods=['GET'])
@login_required
def consignor_finish(opid=0):
    try:
        op = Order_pay.query.get_or_404(opid)
        if op.goodsed.consignor != current_user.consignors or op.goodsed.state !=3:
            return redirect(url_for('main.index'))
        # gqf = Goods.query.filter((Goods.state==3)&(Goods.consignor==current_user.consignors)).first()
        # if gqf ==3:
        op.goodsed.state =4
        aprice = op.driver.user.lock_price
        op.driver.user.price += aprice
        op.driver.user.lock_price = 0
        db.session.add(op)
        db.session.commit()
        if aprice > 0.00:
            flask_wechat.message.send_text(op.driver.user.wx_open_id,u'货主已确认货物安全抵达，您的钱包已增加%s元。'%aprice)

        # else:
        #     return redirect(url_for('main.index'))
    except Exception, e:
        pass
    return redirect(url_for('usercenter.huoyunxinxi'))


@usercenter.route('/huoyunxinxi_show/<int:id>',methods=['GET'])
@login_required
def huoyunxinxi_show(id=0):
    return render_template('user/huoyunxinxi_show.html',op=Order_pay.query.get_or_404(id))
    

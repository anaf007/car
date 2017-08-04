#coding=utf-8
"""filename:app/users/views.py
Created 2017-05-29
Author: by anaf
"""

from flask import render_template,abort,request,current_app,url_for,make_response,flash,redirect
from . import usercenter
from .. import db
import random,os,datetime
from  flask.ext.login import login_required,current_user
from  ..models import Permission,User,Driver,Order_pay
from app.decorators import permission_required

@usercenter.route('/index')
@usercenter.route('/')
@usercenter.route('/<username>')
def index(username=''):
    d = Driver.query.filter_by(users=current_user).first()
    return render_template('user/index.html',user=current_user)

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


#用户关注
@usercenter.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(u'关注失败')
        return redirect(url_for('.index'))
    if current_user.is_following(user):
        flash(u'您已经关注过该用户了')
        return redirect(url_for('.index', username=username))
    current_user.follow(user)
    return redirect(url_for('.index',username=username))


#关注
@usercenter.route('/followers/<username>')
def followers(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followers.paginate(page, per_page=10,error_out=False)
    follows = [{'user': item.follower, 'timestamp': item.timestamp} 
                for item in pagination.items]
    return render_template('followers.html', user=user, title="Followers of",endpoint='.followers', pagination=pagination,follows=follows)


#取消关注
@usercenter.route('/unfollow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(u'取消关注失败')
        return redirect(url_for('.index'))
    if current_user.is_following(user):
        current_user.unfollow(user)
        return redirect(url_for('.index', username=username))
    
    return redirect(url_for('.index',username=username))



@usercenter.route('/show_order')
@login_required
def show_order():
    return render_template('user/show_order.html')


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

#大客户
@usercenter.route('/dakehu')
@login_required
def dakehu():
    return render_template('user/dakehu.html')

#用户设置
@usercenter.route('/setting')
@login_required
def setting():
    return render_template('user/setting.html')

#自身接单下单
@usercenter.route('/self_order')
def selforder():
    op = Order_pay.query.filter(Order_pay.order_pay_user==current_user).order_by(Order_pay.id.desc()).all()
    print op
    return render_template('user/selforder.html',op=op)

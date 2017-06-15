#coding=utf-8
"""filename:app/main/views.py
Created 2017-05-29
Author: by anaf
"""

from flask import render_template,redirect,url_for,request,flash,current_app,make_response
from . import main
from .. import db
from ..models import Article,Comment,Permission,CategoryTop,Category
from  flask.ext.login import login_required,current_user
from ..decorators import admin_required,permission_required
from .forms import PostForm,CommentForm
import os,random,datetime


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
def index():
    categorts = CategoryTop.query.all()
    return render_template('main/index.html',nav=categorts)

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

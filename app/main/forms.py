#coding=utf-8
"""filename:app/main/forms.py
Created 2017-05-30
Author: by anaf
"""
from flask.ext.wtf import Form
from wtforms import StringField,PasswordField,BooleanField,SubmitField,TextAreaField
from wtforms.validators import Required,Length,Email

class PostForm(Form):
	title = StringField(u'文章标题',validators=[Required(),Length(1,64)])
	body = TextAreaField('what`s on your mind?',validators=[Required()])
	submit = SubmitField(u'Submit')

class CommentForm(Form):
	body = StringField('', validators=[Required()])
	submit = SubmitField('Submit')




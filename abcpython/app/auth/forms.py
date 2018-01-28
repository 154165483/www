# 引入Form基类
from flask_wtf import FlaskForm
# 引入Form元素父类
from wtforms import StringField, PasswordField, SubmitField, BooleanField
# 引入Form验证父类
from wtforms.validators import DataRequired, Length, Required, Email, Regexp, EqualTo, ValidationError

# 引入USERS对象
from app.models import Users

__author__ = 'wulang'


# 登录表单类,继承与Form类
class LoginForm(FlaskForm):
	# 用户名
	# name = StringField('Name', validators=[DataRequired(message=u"用户名不能为空")
	#     , Length(8, 20, message=u'长度位于8~20之间')], render_kw={'placeholder': u'输入用户名'})
	# 邮件
	email = StringField('Email', validators=[DataRequired(message=u"E-mail address can not be empty"), Length(1, 64, message=u'The length is between 1 and 64'), Email()],
						render_kw={'placeholder': u'邮箱'})
	# 密码
	password = PasswordField('Password', validators=[DataRequired(message=u"Password can not be empty")
		, Length(1, 20, message=u'The length is between 8 and 20')], render_kw={'placeholder': u'密码'})
	# 邮件
	# email = StringField('Email', validators=[DataRequired(message=u"地址不能为空"), Length(1, 64), Email()],render_kw={'placeholder': u'输入邮件'})
	remember_me = BooleanField('Keep me logged in')
	submit = SubmitField('Log In')


# 用户注册表单
class RegistrationForm(FlaskForm):
	email = StringField('Email', validators=[DataRequired(message=u"E-mail address can not be empty"), Length(1, 64, message=u'The length is between 1 and 64'), Email()],
						render_kw={'placeholder': u'Enter your email'})
	username = StringField('Username', validators=[DataRequired(message=u"Username address can not be empty"), Length(1, 64, message=u'The length is between 1 and 64'),
												   Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
														  'Usernames must have only letters, ''numbers, dots or underscores')],
						   render_kw={'placeholder': u'Enter your username'})
	password = PasswordField('Password', validators=[DataRequired(message=u"Password can not be empty"), EqualTo('password2', message='Passwords must match.')],
							 render_kw={'placeholder': u'Enter your password'})
	password2 = PasswordField('Confirm password', validators=[DataRequired(message=u"Password can not be empty")], render_kw={'placeholder': u'Enter the password again'})
	submit = SubmitField('Register')

	# 验证邮箱是否重名
	def validate_email(self, field):
		if Users.query.filter_by(email=field.data).first():
			raise ValueError('Email already registered!')

	# 验证账号是否重复
	def validate_username(self, field):
		if Users.query.filter_by(username=field.data).first():
			raise ValueError('Username already in use!')


# 修改密码表单
class ChangePasswordForm(FlaskForm):
	old_password = PasswordField('Old password', validators=[Required()])
	new_password = PasswordField('New password', validators=[
		Required(), EqualTo('new_password2', message='Passwords must match')])
	new_password2 = PasswordField('Confirm new password', validators=[Required()])
	submit = SubmitField('Update Password')


# 修改邮箱表单
class ChangeEmailForm(FlaskForm):
	email = StringField('New Email', validators=[Required(), Length(1, 64),
												 Email()])
	password = PasswordField('Password', validators=[Required()])
	submit = SubmitField('Update Email Address')

	def validate_email(self, field):
		if Users.query.filter_by(email=field.data).first():
			raise ValidationError('Email already registered.')


# 找回密码表单
class PasswordResetRequestForm(FlaskForm):
	email = StringField('Email Address', validators=[Required(), Length(1, 64), Email()])
	submit = SubmitField('Send out')

	def validate_email(self, field):  # 这里前面学过的东西差点又忘记了，以validate_开头的函数，会和普通验证函数一起被调用
		if Users.query.filter_by(email=field.data).first() is None:
			raise ValidationError('Unknown email address.')


# 修改密码表单
class PasswordResetForm(FlaskForm):
	email = StringField('Email Address', validators=[Required(), Email()])  # 这一行特别注意，如果没有这一行的话，你到最后路由里面，没有办法定位你的具体账号的。
	renew_password = PasswordField('Newpassowrd',
								   validators=[Required(), EqualTo('renew_password2', message='Password must match.')])
	renew_password2 = PasswordField('Confirm Newpassowrd', validators=[Required()])
	submit = SubmitField('Save Change')

from flask import url_for, flash, redirect, render_template, request, current_app, make_response
from flask_login import logout_user, login_required, login_user, current_user
from app.auth.forms import LoginForm, RegistrationForm, ChangePasswordForm, ChangeEmailForm, PasswordResetForm, \
	PasswordResetRequestForm
from app.email import send_email
from app import db, create_app
from app.models import Users, Post, Source, Menu, BlogCount
from config import Config
from . import auth


# 过滤未确认的账户
# 对蓝本来说，before_request 钩子只能应用到属于蓝本的请求上。
# 若想在 蓝本中使用针对程序全局请求的钩子，
# 必须使用 before_app_request 修饰器。
@auth.before_app_request
def before_request():
	# 如果用户是认证过的，
	# 但是confirmed属性为False
	# 而且，request的网址不是以auth和static开头-------------------------------------->
	# 就返回到一个未确认的路由
	if current_user.is_authenticated:
		current_user.ping()
		if not current_user.confirmed \
				and request.endpoint[:5] != 'auth.' \
				and request.endpoint != 'static':
			return redirect(url_for('auth.unconfirmed'))


# 未确认路由,作用：将未确认邮箱用户限制在一个固定界面
@auth.route('/unconfirmed')
def unconfirmed():
	if current_user.is_anonymous or current_user.confirmed:
		return redirect(url_for('main.index', username=current_user.username))
	# flash('Please confirm your account!')
	return render_template('auth/unconfirmed.html')


# 定义主页
@auth.route('/', methods=['GET', 'POST'])
def index():
	BlogCount.add_blogview(db)
	menus = Menu.query.all()
	page = request.args.get('page', 1, type=int)
	pagination = Post.query.order_by(Post.update_time.desc()).paginate(
		page, per_page=current_app.config['FLASKY_POSTS_INFO_PAGE'],
		error_out=False)
	posts = pagination.items
	return render_template('index.html', posts=posts, menus=menus,
						   pagination=pagination, endpoint='.index')


# 标题分类查看
@auth.route('/source/<int:id>', methods=['GET', 'POST'])
def source(id):
	BlogCount.add_blogview(db)
	page = request.args.get('page', 1, type=int)
	pagination = Source.query.get_or_404(id).posts.order_by(
            Post.update_time.desc()).paginate(
            page, per_page=current_app.config['FLASKY_POSTS_INFO_PAGE'],
            error_out=False)
	posts = pagination.items
	return render_template('index.html', posts=posts,
                           pagination=pagination, endpoint='.source',
                           id=id)


# 形式分类  原创、转载、翻译
@auth.route('/menu/<int:id>', methods=['GET', 'POST'])
def menu(id):
	BlogCount.add_blogview(db)
	page = request.args.get('page', 1, type=int)
	pagination = Menu.query.get_or_404(id).posts.order_by(
            Post.update_time.desc()).paginate(
            page, per_page=current_app.config['FLASKY_POSTS_INFO_PAGE'],
            error_out=False)
	posts = pagination.items
	return render_template('index.html', posts=posts,
                           pagination=pagination, endpoint='.menu',
                           id=id)





# 定义登录处理函数和路由规则，接收GET和POST请求
@auth.route('/login', methods=('POST', 'GET'))
def login():
	BlogCount.add_blogview(db)
	form = LoginForm()
	# 判断是否是验证提交
	if form.validate_on_submit():
		user = Users.query.filter_by(email=form.email.data).first()
		if user is not None and user.verify_password(form.password.data):
			login_user(user, form.remember_me.data)
			flash('Login Success')
			return redirect(request.args.get('next') or url_for('auth.index'))
		flash('Invalid username or password!')
	return render_template('auth/login.html', form=form)


# 定义登出处理函数和路由规则，接收GET和POST请求
@auth.route('/logout')
@login_required
def logout():
	logout_user()
	flash('You hava been logged out!')
	return redirect(url_for('.index'))


# 定义注册处理函数和路由规则，接收GET和POST请求
@auth.route('/zc154165483', methods=['GET', 'POST'])
def zc154165483():
	BlogCount.add_blogview(db)
	form = RegistrationForm()
	if form.validate_on_submit():
		user = Users(email=form.email.data,
					 username=form.username.data,
					 password=form.password.data,
					 )
		db.session.add(user)
		db.session.commit()  # 写入数据库
		token = user.generate_confirmation_token()  # 获取用户的token令牌
		# 发送确认邮件
		send_email(user.email, 'Confirm Your Account', 'auth/email/confirm', user=user, token=token)
		flash('A confirmation email has been sent to you by email.')
		return redirect(url_for('auth.login'))
	return render_template('auth/register.html', form=form)


# 确认用户账户
@auth.route('/confirm/<token>')
@login_required
def confirm(token):
	if current_user.confirmed:
		return redirect(url_for('main.index', username=current_user.username))
	if current_user.confirm(token):
		flash('You have confirmed your account. Thanks!')
		# 确认完成后发邮件告知管理员，用户已经加入
		if create_app(Config()).config['FLASKY_ADMIN']:
			send_email(create_app(Config()).config['FLASKY_ADMIN'], create_app(Config()).config['FLASKY_MAIL_SUBJECT'],
					   'auth/email/new_user',
					   user=current_user.username)
	else:
		flash('The confirmation link is invalid or has expired.')
	return redirect(url_for('main.index', username=current_user.username))


# 重新发送账户确认邮件路由
@auth.route('/resend_confirmation')
@login_required
def resend_confirmation():
	token = current_user.generate_confirmation_token()
	send_email(current_user.email, 'Confirm Your Account', 'auth/email/confirm', user=current_user, token=token)
	flash('A new confirmation email has been sent to you by email.')
	return redirect(url_for('auth.unconfirmed'))


# 修改密码
@auth.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
	form = ChangePasswordForm()
	if form.validate_on_submit():
		if current_user.verify_password(form.old_password.data):
			new_password = form.new_password.data
			token = current_user.gengenerate_password_change_token(new_password)
			send_email(current_user.email, 'Confirm your password',
					   'auth/email/change_password',
					   user=current_user, token=token)
			flash('An email with instructions to confirm your new password has been sent to you.')
			return render_template("auth/change_password.html", form=form)
		else:
			flash('Invalid password.')
	return render_template("auth/change_password.html", form=form)


# 修改密码确认邮箱
@auth.route('/change_password/<token>')
@login_required
def change_password_token(token):
	if current_user.change_password(token):
		flash('Your password has been updated.')
	else:
		flash('Invalid request.')
	return redirect(url_for('main.index'))


# 修改邮箱
@auth.route('/change_email', methods=['GET', 'POST'])
@login_required
def change_email():
	form = ChangeEmailForm()
	if form.validate_on_submit():
		if current_user.verify_password(form.password.data):
			new_email = form.email.data
			token = current_user.generate_email_change_token(new_email)
			send_email(new_email, 'Confirm your email address',
					   'auth/email/change_email',
					   user=current_user, token=token)
			flash('An email with instructions to confirm your new email '
				  'address has been sent to you.')
			return render_template("auth/change_email.html", form=form)
		else:
			flash('Invalid email or password.')
	return render_template("auth/change_email.html", form=form)


# 修改邮箱确认路由
@auth.route('/change_email/<token>')
@login_required
def change_email_token(token):
	if current_user.change_email(token):
		flash('Your email address has been updated.')
	else:
		flash('Invalid request.')
	return redirect(url_for('main.index'))


# 密码重置路由
@auth.route('/password_reset_request', methods=['GET', 'POST'])
def password_reset_request():
	if not current_user.is_anonymous:
		render_template(url_for('main.index'))
	form = PasswordResetRequestForm()
	if form.validate_on_submit():
		user = Users.query.filter_by(email=form.email.data).first()
		if user:
			token = user.gengenerate_password_reset_token()
			send_email(user.email, 'Reset Password', 'auth/email/reset_password', user=user, token=token,
					   next=request.args.get('next'))
			flash('Please check the Reset Password Email in your inbox !')
			return redirect(url_for('auth.login'))
		else:
			flash('Email address does not exist !')
	return render_template('auth/password_reset_request.html', form=form)


@auth.route('/password_reset/<token>', methods=['GET', 'POST'])
def password_reset_token(token):
	if not current_user.is_anonymous:
		return redirect(url_for('main.index'))
	form = PasswordResetForm()
	if form.validate_on_submit():
		user = Users.query.filter_by(email=form.email.data).first()
		if user is None:
			return redirect(url_for('main.index'))
		if user.reset_password(token, form.renew_password.data):
			flash('Your password has been updated.')
			return redirect(url_for('auth.login'))
		else:
			return redirect(url_for('auth.index'))
	return render_template('auth/reset_password.html', form=form)

#关于本博客
@auth.route('/about',methods=['GET', 'POST'])
def about():
	BlogCount.add_blogview(db)
	return render_template('about.html')
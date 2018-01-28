import hashlib
from datetime import datetime

import bleach
from flask import current_app, request
from flask_login import UserMixin, AnonymousUserMixin
from markdown import markdown
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from app import db
from app import login_manager
from sqlalchemy import or_


class Permission:
	FOLLOW = 0X01
	COMMENT = 0X02
	WRITE_ARTICLES = 0X04
	MODERATE_COMMENTS = 0X08
	ADMINISTER = 0X80


# 关注者
class Follow(db.Model):
	__tablename__ = 'follows'
	follower_id = db.Column(db.Integer, db.ForeignKey('users.id'),
							primary_key=True)
	followed_id = db.Column(db.Integer, db.ForeignKey('users.id'),
							primary_key=True)
	timestamp = db.Column(db.DateTime, default=datetime.utcnow)


# 定义匿名类
class AnonymousUser(AnonymousUserMixin):
	def can(self, permissions):
		return False

	def is_administrator(self):
		return False


login_manager.anonymous_user = AnonymousUser


# 将login_manager.anonymous_user设为AnonymousUser类对象，实际上就是未登录状态的current_user

# 用户回掉函数
@login_manager.user_loader
def load_user(user_id):
	return Users.query.get(int(user_id))







# 用户角色模型
class Role(db.Model):
	__tablename__ = 'roles'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(64), nullable=True, unique=True)
	default = db.Column(db.Boolean, default=False, index=True)  # 用户默认角色,default是False
	permissions = db.Column(db.Integer)  # 用户权限设置，是一个数值
	users = db.relationship('Users', backref='role', lazy='dynamic')  # 和Users类来进行连接

	@staticmethod  # 静态方法 允许不创建实例就运行
	def insert_roles():
		roles = {
			'User': (Permission.FOLLOW | Permission.COMMENT | Permission.WRITE_ARTICLES, True),
			'Moderator': (
				Permission.FOLLOW | Permission.COMMENT | Permission.WRITE_ARTICLES | Permission.MODERATE_COMMENTS,
				False),
			'ADMINISTER': (0xff, False)
		}
		for r in roles:  # 历遍roles字典
			role = Role.query.filter_by(name=r).first()  # 查询Role类里是否存在这种name的角色
			if role is None:  # 如果Role类里面没有找到
				role = Role(name=r)  # 则新建角色，以r的值为名字(其实是用户组的名字)
			role.permissions = roles[r][0]  # 为该role的权限组分配值，从字典取值
			role.default = roles[r][1]  # 为该role的默认权限组分配布尔值，默认是False
			db.session.add(role)  # 增加角色
		db.session.commit()  # 提交申请

	def __repr__(self):
		return '<Role %r>' % self.name





class Source(db.Model):
	__tablename__ = 'sources'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(64), unique=True)
	posts = db.relationship('Post', backref='source', lazy='dynamic')
	@staticmethod
	def insert_sources():
		sources = (u'原创',
			   	u'转载',
			   	u'翻译')
		for s in sources:
			source = Source.query.filter_by(name=s).first()
			if source is None:
				source = Source(name=s)
			db.session.add(source)
		db.session.commit()
	def __repr__(self):
		return '<Source %r>' % self.name


# 博客模型
class Post(db.Model):
	__tablename__ = 'posts'
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.Text)
	summary = db.Column(db.Text)
	body = db.Column(db.Text)
	body_html = db.Column(db.Text)
	create_time = db.Column(db.DateTime, index=True, default=datetime.utcnow)
	update_time = db.Column(db.DateTime, index=True, default=datetime.utcnow)
	num_of_view = db.Column(db.Integer, default=0)
	author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
	source_id = db.Column(db.Integer, db.ForeignKey('sources.id'))
	menu_id = db.Column(db.Integer, db.ForeignKey('menus.id'))
	comments = db.relationship('Comment', backref='post', lazy='dynamic')

	# 统计点击次数
	@staticmethod
	def add_view(post, db):
		post.num_of_view += 1
		db.session.add(post)
		db.session.commit()


	@staticmethod
	def on_changed_body(target, value, oldvalue, initiator):
		allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
						'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul', 'h1',
						'h2', 'h3', 'p', 'img', 'sup', 'color', 'font-weight',
						'height', 'width', 's', 'span', 'pre', 'u', 'table',
						'td', 'tr', 'tbody', 'caption', 'span', 'strong','font-size']
		attrs = {
			'*': ['style'],
			'a': ['href', 'rel'],
			'style': ['font-size','color', 'font-weight', 'height', 'width', 'px', 'border-style', 'solid', 'border-width', 'float',
					  'left', 'margin', 'background-color', 'caption', 'span', 'strong', 'python'],
			'img': ['src', 'alt'],
			'table': ['border', 'cellpadding', 'cellspacing', 'style', 'summary',
					  'caption', 'tbody', 'tr', 'td'],

		}
		styles = ['color', 'font-weight', 'height', 'width', 'px', 'border-style', 'solid', 'border-width', 'float',
				  'left', 'margin', 'background-color', 'caption', 'span', 'strong','font-size']

		target.body_html = bleach.linkify(
			bleach.clean(markdown(value, output_format='html'), tags=allowed_tags, attributes=attrs, styles=styles,
						 strip=True))

	def __repr__(self):
		return '<Post %r>' % self.title
db.event.listen(Post.body, 'set', Post.on_changed_body)



class Comment(db.Model):
	__tablename__ = 'comments'
	id = db.Column(db.Integer, primary_key=True)
	body = db.Column(db.Text)
	body_html = db.Column(db.Text)
	timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
	disabled = db.Column(db.Boolean, default=False)
	author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
	post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))

	@staticmethod
	def on_changed_body(target, value, oldvalue, initiator):
		allowed_tags = ['a', 'abbr', 'acronym', 'b', 'code', 'em', 'i',
						'strong', 'pre']
		target.body_html = bleach.linkify(bleach.clean(
			markdown(value, output_format='html'),
			tags=allowed_tags, strip=True))


db.event.listen(Comment.body, 'set', Comment.on_changed_body)


# 用户表
class Users(UserMixin, db.Model):
	__tablename__ = 'users'
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(64), unique=True, index=True)
	email = db.Column(db.String(64), unique=True, index=True)
	role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
	password_hash = db.Column(db.String(128))
	confirmed = db.Column(db.Boolean, default=False)
	name = db.Column(db.String(64))
	location = db.Column(db.String(64))
	about_me = db.Column(db.Text())
	member_since = db.Column(db.DateTime(), default=datetime.utcnow)
	last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
	avatar_hash = db.Column(db.String(32))
	posts = db.relationship('Post', backref='author', lazy='dynamic')

	# 关联关注者
	followed = db.relationship('Follow',
							   foreign_keys=[Follow.follower_id],
							   backref=db.backref('follower', lazy='joined'),
							   lazy='dynamic',
							   cascade='all, delete-orphan')
	followers = db.relationship('Follow',
								foreign_keys=[Follow.followed_id],
								backref=db.backref('followed', lazy='joined'),
								lazy='dynamic',
								cascade='all, delete-orphan')
	comments = db.relationship('Comment', backref='author', lazy='dynamic')

	# 四个函数来处理关联
	def follow(self, user):
		if not self.is_following(user):
			f = Follow(follower=self, followed=user)
			db.session.add(f)

	def unfollow(self, user):
		f = self.followed.filter_by(followed_id=user.id).first()
		if f:
			db.session.delete(f)

	def is_following(self, user):
		return self.followed.filter_by(
			followed_id=user.id).first() is not None

	def is_followed_by(self, user):
		return self.followers.filter_by(
			follower_id=user.id).first() is not None

	# 单独调用password返回错误————password不可读（数据库根本就没有存储）
	@property
	def password(self):
		raise AttributeError('password is not a readable attribute')

	# 用户输入的password转化为hash并存储数据库
	@password.setter
	def password(self, password):
		self.password_hash = generate_password_hash(password)

	# 将用户输入的密码，跟hash比对，一致返回true
	def verify_password(self, password):
		return check_password_hash(self.password_hash, password)

	# 生成一个注册令牌，有效期半个小时
	def generate_confirmation_token(self, expiration=1800):
		s = Serializer(current_app.config['SECRET_KEY'], expiration)
		return s.dumps({'confirm': self.id})

	# 检验令牌是否通过，通过把confirmed字段设置为True
	def confirm(self, token):
		s = Serializer(current_app.config['SECRET_KEY'])
		try:
			data = s.loads(token)
		except:
			return False
		if data.get('confirm') != self.id:
			return False
		self.confirmed = True
		db.session.add(self)
		db.session.commit()
		return True

	# 生成一个更改密码的令牌
	def gengenerate_password_change_token(self, new_password, expiration=1800):
		s = Serializer(current_app.config['SECRET_KEY'], expiration)
		return s.dumps({'change_password': self.id, 'new_password': new_password})

	# 验证密码更改令牌
	def change_password(self, token):
		s = Serializer(current_app.config['SECRET_KEY'])
		try:
			data = s.loads(token)
		except:
			return False
		if data.get('change_password') != self.id:
			return False
		new_password = data.get('new_password')
		if new_password is None:
			return False
		self.password_hash = generate_password_hash(new_password)
		db.session.add(self)
		db.session.commit()
		return True

	# 生成一个更改Email的令牌
	def generate_email_change_token(self, new_email, expiration=1800):
		s = Serializer(current_app.config['SECRET_KEY'], expiration)
		return s.dumps({'change_email': self.id, 'new_email': new_email})

	# 验证Email更改令牌
	def change_email(self, token):
		s = Serializer(current_app.config['SECRET_KEY'])
		try:
			data = s.loads(token)
		except:
			return False
		if data.get('change_email') != self.id:
			return False
		new_email = data.get('new_email')
		if new_email is None:
			return False
		if self.query.filter_by(email=new_email).first() is not None:
			return False
		self.email = new_email
		self.avatar_hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()
		db.session.add(self)
		db.session.commit()
		return True

	# def is_authenticated(self): 如果用户已经登录，必须返回 True，否则返回 False
	#     return True
	# def is_active(self):如果允许用户登录，必须返回 True，否则返回 False。如果要禁用账户，可以返回 False
	#     return True
	# def is_anonymous(self):对普通用户必须返回 False
	#     return False
	# def get_id(self):必须返回用户的唯一标识符，使用 Unicode 编码字符串
	#     return self.id
	# 这 4 个方法可以在模型类中作为方法直接实现，不过还有一种更简单的替代方案。FlaskLogin 提供了一个 UserMixin 类，其中包含这些方法的默认实现，且能满足大多数需求。

	# 生成一个重置密码的令牌---密码
	def gengenerate_password_reset_token(self, expiration=1800):
		s = Serializer(current_app.config['SECRET_KEY'], expiration)
		return s.dumps({'reset_password': self.id})

	# 验证重置密码更改令牌--密码
	def reset_password(self, token, renew_password):
		s = Serializer(current_app.config['SECRET_KEY'])
		try:
			data = s.loads(token)
		except:
			return False
		if data.get('reset_password') != self.id:
			return False
		renew_password = renew_password
		if renew_password is None:
			return False
		self.password_hash = generate_password_hash(renew_password)
		db.session.add(self)
		db.session.commit()
		return True

	# 定义默认的用户角色
	def __init__(self, **kwargs):
		super(Users, self).__init__(**kwargs)
		if self.role is None:
			if self.email == current_app.config['FLASKY_ADMIN']:
				self.role = Role.query.filter_by(permissions=0xff).first()

			# if self.role is None:
			else:
				self.role = Role.query.filter_by(default=True).first()
		if self.email is not None and self.avatar_hash is None:
			self.avatar_hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()

	# 角色进行验证
	def can(self, permissions):
		return self.role is not None and (self.role.permissions & permissions) == permissions

	# 检测对象的role属性不是None的同时，对象的权限数值和要求检验的数值符合

	def is_administrator(self):
		return self.can(Permission.ADMINISTER)

	# 直接赋值管理员的权限数值，看是否符合要求

	# 刷新用户登录时间
	def ping(self):
		self.last_seen = datetime.utcnow()  # 刷新登录时间
		db.session.add(self)
		db.session.commit()

	# 用户头像
	def gravatar(self, size=100, default='identicon', rating='g'):
		if request.is_secure:  # 判断request是否为https
			url = 'https://secure.gravatar.com/avatar'
		else:
			url = 'http://www.gravatar.com/avatar'
		hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()  # 生成hash值
		return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(url=url, hash=hash, size=size, default=default,
																	 rating=rating)

	# 关注者文章列表
	@property
	def followed_posts(self):

		# return Post.query.join(Follow, Follow.followed_id == Post.author_id)\        显示关注用户文章
		#      .filter(Follow.follower_id == self.id)

		# 显示用户关注文章，以及自己的文章
		return Post.query.join(Follow, Follow.followed_id == Post.author_id) \
			.filter(or_(Follow.follower_id == self.id, Post.author_id == self.id))

	def __repr__(self):
		return '<Users %r>' % self.username


# 导航栏
class Menu(db.Model):
	__tablename__ = 'menus'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(64), unique=True)
	posts = db.relationship('Post', backref='menu', lazy='dynamic')
	order = db.Column(db.Integer, default=0, nullable=False)

	# 删除导航栏分类
	def sort_delete(self):
		for menu in Menu.query.order_by(Menu.order).offset(self.order).all():
			menu.order -= 1
			db.session.add(menu)

	# 初始化导航栏
	@staticmethod
	def insert_menus():
		menus = [u'Python', u'Flask', u'Mysql',
				 u'CentOS', u'Life', ]
		for name in menus:
			menu = Menu(name=name)
			db.session.add(menu)
			db.session.commit()
			menu.order = menu.id
			db.session.add(menu)
			db.session.commit()

	@staticmethod
	def return_menus():
		menus = [(m.id, m.name) for m in Menu.query.all()]
		menus.append((-1, u'不选择导航（该分类将单独成一导航）'))
		return menus

	def __repr__(self):
		return '<Menu %r>' % self.name


#博客统计
class BlogCount(db.Model):
	__tablename__ = 'blogcount'
	id = db.Column(db.Integer, primary_key=True)
	blog_view = db.Column(db.Integer, default=0)
	blog_comment = db.Column(db.Integer, default=0)
	blog_post = db.Column(db.Integer, default=0)

	#初始化统计
	@staticmethod
	def insert_count():
		blogcount = BlogCount(blog_view=0,blog_post=0,blog_comment=0)
		db.session.add(blogcount)
		db.session.commit()

	# 统计网站点击次数
	@staticmethod
	def add_blogview(db):
		blogview = BlogCount.query.first()
		blogview.blog_view = blogview.blog_view + 1
		db.session.add(blogview)
		db.session.commit()

	#统计网站评论数
	@staticmethod
	def add_blogcomment(db):
		blogcoment = BlogCount.query.first()
		blogcoment.blog_comment = blogcoment.blog_comment + 1
		db.session.add(blogcoment)
		db.session.commit()

	#统计网站博文数量
	@staticmethod
	def add_blogpost(db):
		blogpost = BlogCount.query.first()
		blogpost.blog_post = blogpost.blog_post + 1
		db.session.add(blogpost)
		db.session.commit()
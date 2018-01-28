class Config:
	CSRF_ENABLED = True
	SECRET_KEY = '154165483'
	SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:wulang2@XUYA@localhost:4357/abcpython'
	SQLALCHEMY_TRACK_MODIFICATIONS = True
	DEBUG = False
	MAIL_DEBUG = True
	MAIL_SERVER = 'smtp.sendgrid.net'
	MAIL_PORT = 465
	MAIL_USE_SSL = True
	MAIL_USE_TLS = False
	MAIL_USERNAME = 'apikey'
	MAIL_PASSWORD = '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'
	FLASKY_MAIL_SUBJECT_PREFIX = '[初学python网]'
	FLASKY_MAIL_SENDER = 'admin@abcpython.com'
	FLASKY_ADMIN = 'admin@abcpython.com'
	FLASKY_MAIL_SUBJECT = 'New User'
	FLASKY_POSTS_INFO_PAGE = 4
	FLASKY_COMMENTS_PER_PAGE = 5

	@staticmethod
	def init_app(app):
		pass

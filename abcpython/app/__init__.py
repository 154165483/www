# 导入包
from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_moment import Moment
from flask_pagedown import PageDown
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

# 定义Bootstrap对象
bootstrap = Bootstrap()

# 定义数据库对象
db = SQLAlchemy()

# 定义令牌对象
csrf = CSRFProtect()

# 定义邮箱对象
mail = Mail()

# 定义数据库迁移对象
migrate = Migrate()

# 处理富文本
pagedown = PageDown()
# 定义时间
moment = Moment()

# 登录管理
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'


# 工厂
def create_app(config_name):
	app = Flask(__name__)
	app.config.from_object(config_name)
	config_name.init_app(app)
	csrf.init_app(app)
	bootstrap.init_app(app)
	db.init_app(app)
	mail.init_app(app)
	moment.init_app(app)
	login_manager.init_app(app)
	migrate.init_app(app, db)
	pagedown.init_app(app)

	@app.errorhandler(404)
	def page_not_found(e):
		return render_template('404.html'), 404

	@app.errorhandler(500)
	def internal_server_error(e):
		return render_template('500.html'), 500

	from app.auth import auth as auth_blueprint
	app.register_blueprint(auth_blueprint)
	from app.main import main as main_blueprint
	app.register_blueprint(main_blueprint, url_prefix='/main')
	from app.admin import admin as admin_blueprint
	app.register_blueprint(admin_blueprint, url_prefix='/admin')
	return app

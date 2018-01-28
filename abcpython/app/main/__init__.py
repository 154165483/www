from flask import Blueprint
from app.models import Permission

main = Blueprint('main', __name__, static_folder='../static', template_folder='templates', static_url_path='app/static')


@main.app_context_processor
def inject_permissions():
	return dict(Permission=Permission)


from . import views

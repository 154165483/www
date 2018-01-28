from app import create_app, db
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand
from config import Config
from app.models import Users, Role, Permission, Source, Menu, BlogCount

app = create_app(Config())
manager = Manager(app)
migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)


def make_shell_context():
	return dict(app=app, db=db, Users=Users, Role=Role, Permission=Permission,
				Source=Source, Menu=Menu, BlogCount=BlogCount)


manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
	manager.run()

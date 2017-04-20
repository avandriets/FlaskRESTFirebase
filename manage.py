import os
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from app import create_app
from app.database import Base

app = create_app('config')

# app.config.from_object(os.environ['APP_SETTINGS'])

migrate = Migrate(app, Base)
manager = Manager(app)

manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    manager.run()
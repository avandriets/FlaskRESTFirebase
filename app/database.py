from flask import current_app
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def init_db():
    # TODO Add other modules here
    import app.users_manager.models

    db.init_app(current_app)
    db.create_all()
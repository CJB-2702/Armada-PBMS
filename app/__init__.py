from flask import Flask
from app.models.BaseModels import initialize_database_and_extensions, migrate, login_manager
from app.routes import register_blueprints


def create_and_configure_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'dev'  # Change in production
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    return app

def create_app():
    app = create_and_configure_app()
    initialize_database_and_extensions(app)
    register_blueprints(app)
    return app 
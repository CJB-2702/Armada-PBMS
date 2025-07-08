from flask import Flask
from flask_migrate import Migrate
from flask_login import LoginManager
from app.utils.logger import get_logger, init_logger
from app.extensions import db
from app.routes.main import bp as main_bp
from app.routes.users import bp as users_bp
from app.routes.assets import bp as assets_bp
from app.routes.events import bp as events_bp
from app.routes.locations import bp as locations_bp


migrate = Migrate()
login_manager = LoginManager()

@login_manager.user_loader
def load_user(user_id):
    from app.models.BaseModels.Users import User
    return User.query.get(int(user_id))

def initialize_database_and_extensions(app):
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    logger = get_logger()
    logger.info("Logger initialized")
    with app.app_context():
        db.create_all()
        from app.models.BaseModels.Users import ensure_required_users
        ensure_required_users()
        from app.models.BaseModels.Asset import ensure_required_asset_types
        ensure_required_asset_types()
        from app.models.BaseModels.Event import ensure_required_event_types, create_initial_user_events
        ensure_required_event_types()
        create_initial_user_events()

def create_and_configure_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'dev'  # Change in production
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    return app

def register_blueprints(app):
    app.register_blueprint(main_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(assets_bp)
    app.register_blueprint(events_bp)
    app.register_blueprint(locations_bp)

def create_app():
    app = create_and_configure_app()
    initialize_database_and_extensions(app)
    register_blueprints(app)
    return app 
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import os

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///asset_management.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    # Import and register blueprints
    from app.models import core, assets, dispatching
    
    # Import models to ensure they're registered with SQLAlchemy
    from app.models.core.user import User
    from app.models.core.user_created_base import UserCreatedBase
    from app.models.core.major_location import MajorLocation
    from app.models.core.asset_type import AssetType
    from app.models.core.make_model import MakeModel
    from app.models.core.asset import Asset
    from app.models.core.event import Event
    
    # Import dispatching models to ensure they're registered
    from app.models.dispatching.dispatch import Dispatch
    from app.models.dispatching.dispatch_status_history import DispatchStatusHistory
    from app.models.dispatching.all_dispatch_details import AllDispatchDetail
    from app.models.dispatching.dispatch_detail_virtual import DispatchDetailVirtual
    from app.models.dispatching.detail_table_sets.asset_type_dispatch_detail_table_set import AssetTypeDispatchDetailTableSet
    from app.models.dispatching.detail_table_sets.model_additional_dispatch_detail_table_set import ModelAdditionalDispatchDetailTableSet
    from app.models.dispatching.dispatch_details.vehicle_dispatch import VehicleDispatch
    from app.models.dispatching.dispatch_details.truck_dispatch_checklist import TruckDispatchChecklist
    
    # Register blueprints
    from app.auth import auth
    from app.routes import main
    from app.routes import init_app as init_routes
    
    app.register_blueprint(auth)
    app.register_blueprint(main)
    
    # Initialize tiered routes system (without re-registering main)
    init_routes(app)
    
    return app 
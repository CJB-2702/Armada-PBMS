from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import os
from app.logger import setup_logging_from_config, get_logger

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    
    # Get singleton logger
    logger = get_logger("asset_management")
    logger.info("Initializing Flask application")
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///asset_management.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    logger.debug(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    logger.debug("Extensions initialized")
    
    # Import and register blueprints
    from app.models import core, assets, supply_items
    
    # Import models to ensure they're registered with SQLAlchemy
    from app.models.core.user import User
    from app.models.core.user_created_base import UserCreatedBase
    from app.models.core.major_location import MajorLocation
    from app.models.core.asset_type import AssetType
    from app.models.core.make_model import MakeModel
    from app.models.core.asset import Asset
    from app.models.core.event import Event
    
    # Import new dispatching models (rebuilt minimal set)
    try:
        from app.models.dispatching.request import DispatchRequest
        from app.models.dispatching.outcomes.standard_dispatch import StandardDispatch
        from app.models.dispatching.outcomes.contract import Contract
        from app.models.dispatching.outcomes.reimbursement import Reimbursement
    except Exception:
        # Dispatching module may be unavailable during certain phases; skip registration
        pass
    
    # Import supply models to ensure they're registered
    from app.models.supply_items.part import Part
    from app.models.supply_items.tool import Tool
    from app.models.supply_items.issuable_tool import IssuableTool
    
    # Import maintenance models to ensure they're registered
    from app.models.maintenance.templates.template_action_set import TemplateActionSet
    from app.models.maintenance.templates.template_action_item import TemplateActionItem
    from app.models.maintenance.base.maintenance_plan import MaintenancePlan
    from app.models.maintenance.base.maintenance_action_set import MaintenanceActionSet
    from app.models.maintenance.maintenance_event import MaintenanceEvent
    from app.models.maintenance.template_maintenance_event import TemplateMaintenanceEvent
    from app.models.maintenance.base.action import Action
    from app.models.maintenance.base.part_demand import PartDemand
    
    logger.debug("Models imported and registered")
    
    # Register blueprints
    from app.auth import auth
    from app.routes import main
    from app.routes import init_app as init_routes
    
    app.register_blueprint(auth)
    app.register_blueprint(main)
    
    # Initialize tiered routes system (without re-registering main)
    init_routes(app)
    
    logger.info("Flask application initialization complete")
    
    return app 
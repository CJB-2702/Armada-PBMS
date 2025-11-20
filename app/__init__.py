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
    import os
    from pathlib import Path
    
    # Get the base directory (app's parent)
    base_dir = Path(__file__).parent.parent
    
    # Set template and static folders to new presentation folder structure
    template_folder = str(base_dir / 'app' / 'presentation' / 'templates')
    static_folder = str(base_dir / 'app' / 'presentation' / 'static')
    
    app = Flask(__name__, 
                template_folder=template_folder,
                static_folder=static_folder)
    
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
    from app.data import core, assets, supply_items
    
    # Import models to ensure they're registered with SQLAlchemy
    from app.data.core.user_info.user import User
    from app.data.core.user_created_base import UserCreatedBase
    from app.data.core.major_location import MajorLocation
    from app.data.core.asset_info.asset_type import AssetType
    from app.data.core.asset_info.make_model import MakeModel
    from app.data.core.asset_info.asset import Asset
    from app.data.core.event_info.event import Event
    
    # Import new dispatching models (rebuilt minimal set)
    try:
        from app.data.dispatching.request import DispatchRequest
        from app.data.dispatching.outcomes.standard_dispatch import StandardDispatch
        from app.data.dispatching.outcomes.contract import Contract
        from app.data.dispatching.outcomes.reimbursement import Reimbursement
    except Exception:
        # Dispatching module may be unavailable during certain phases; skip registration
        pass
    
    # Import supply models to ensure they're registered
    from app.data.supply_items.part import Part
    from app.data.supply_items.tool import Tool
    from app.data.supply_items.issuable_tool import IssuableTool
    
    # Import maintenance models to ensure they're registered
    from app.data.maintenance.templates.template_action_set import TemplateActionSet
    from app.data.maintenance.templates.template_action_item import TemplateActionItem
    from app.data.maintenance.base.maintenance_plan import MaintenancePlan
    from app.data.maintenance.base.maintenance_action_set import MaintenanceActionSet
    from app.buisness.maintenance.maintenance_event import MaintenanceEvent
    from app.buisness.maintenance.template_maintenance_event import TemplateMaintenanceEvent
    from app.data.maintenance.base.action import Action
    from app.data.maintenance.base.part_demand import PartDemand
    
    logger.debug("Models imported and registered")
    
    # Register blueprints
    from app.auth import auth
    from app.presentation.routes import main
    from app.presentation.routes import init_app as init_routes
    
    app.register_blueprint(auth)
    app.register_blueprint(main)
    
    # Initialize tiered routes system (without re-registering main)
    init_routes(app)
    
    logger.info("Flask application initialization complete")
    
    return app 
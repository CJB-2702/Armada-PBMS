"""
Routes package for the Asset Management System
Organized in a tiered structure mirroring the model organization
"""

from flask import Blueprint
from app.logger import get_logger

logger = get_logger("asset_management.routes")

# Create main blueprint
main = Blueprint('main', __name__)

# Import route modules
from . import core, assets, main_routes

def init_app(app):
    """Initialize all route blueprints with the Flask app"""
    logger.debug("Initializing route blueprints")
    
    # Don't register main again - it's already registered in app/__init__.py
    app.register_blueprint(core.bp, url_prefix='/core')
    app.register_blueprint(assets.bp, url_prefix='/assets')
    
    # Register individual core route blueprints
    from .core import events, assets as core_assets, locations, asset_types, make_models, users
    
    app.register_blueprint(events.bp, url_prefix='/core')
    app.register_blueprint(core_assets.bp, url_prefix='/core', name='core_assets')
    app.register_blueprint(locations.bp, url_prefix='/core')
    app.register_blueprint(asset_types.bp, url_prefix='/core')
    app.register_blueprint(make_models.bp, url_prefix='/core')
    app.register_blueprint(users.bp, url_prefix='/core')
    
    # Register comments and attachments blueprints
    from . import comments, attachments
    
    app.register_blueprint(comments.bp, url_prefix='')
    app.register_blueprint(attachments.bp, url_prefix='')
    
    # Register dispatching blueprint
    from .dispatching import dispatches
    
    app.register_blueprint(dispatches.dispatching_bp, url_prefix='/dispatching')
    
    # Register supply blueprints
    from .supply import parts, tools, part_demands, supply_main
    
    app.register_blueprint(parts.bp, url_prefix='/supply', name='supply.parts')
    app.register_blueprint(tools.bp, url_prefix='/supply', name='supply.tools')
    app.register_blueprint(part_demands.bp, url_prefix='/supply', name='supply.part_demands')
    app.register_blueprint(supply_main.bp, url_prefix='/supply', name='supply')
    
    logger.info("All route blueprints registered successfully") 
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
    
    # Register maintenance blueprints
    from .maintenance.main import maintenance_bp
    from .maintenance import (
        maintenance_plans, 
        maintenance_action_sets,
        actions, 
        part_demands, 
        delays,
        template_action_sets,
        template_action_items,
        template_part_demands,
        template_action_tools
    )
    
    app.register_blueprint(maintenance_bp)
    app.register_blueprint(maintenance_plans.bp, url_prefix='/maintenance', name='maintenance_plans')
    app.register_blueprint(maintenance_action_sets.bp, url_prefix='/maintenance', name='maintenance_action_sets')
    app.register_blueprint(actions.bp, url_prefix='/maintenance', name='actions')
    app.register_blueprint(part_demands.bp, url_prefix='/maintenance', name='part_demands')
    app.register_blueprint(delays.bp, url_prefix='/maintenance', name='delays')
    app.register_blueprint(template_action_sets.bp, url_prefix='/maintenance', name='template_action_sets')
    app.register_blueprint(template_action_items.bp, url_prefix='/maintenance', name='template_action_items')
    app.register_blueprint(template_part_demands.bp, url_prefix='/maintenance', name='template_part_demands')
    app.register_blueprint(template_action_tools.bp, url_prefix='/maintenance', name='template_action_tools')
    
    # Register supply blueprints (using new implementations)
    from .supply.main import supply_bp
    from .supply import parts as new_parts, tools as new_tools
    
    app.register_blueprint(supply_bp)
    app.register_blueprint(new_parts.bp, url_prefix='/supply', name='supply.new_parts')
    app.register_blueprint(new_tools.bp, url_prefix='/supply', name='supply.new_tools')
    
    logger.info("All route blueprints registered successfully") 
"""
Assets routes package for asset detail system
Includes routes for asset detail tables and model details
"""

from flask import Blueprint

bp = Blueprint('assets', __name__)

# Import asset detail routes
from . import detail_tables, model_details

# Register the blueprints
bp.register_blueprint(detail_tables.bp, url_prefix='/detail-tables')
bp.register_blueprint(model_details.bp, url_prefix='/model-details') 
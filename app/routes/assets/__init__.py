"""
Assets routes package for asset detail system
Includes routes for asset detail tables and model details
"""

from flask import Blueprint

bp = Blueprint('assets', __name__)

# Import asset detail routes
from . import detail_tables, model_details 
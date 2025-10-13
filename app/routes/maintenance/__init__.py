"""
Maintenance routes package
Includes CRUD operations for all maintenance-related models
"""

from flask import Blueprint
from app.logger import get_logger

bp = Blueprint('maintenance', __name__)
logger = get_logger("asset_management.routes.maintenance")

# Import all maintenance route modules
from . import (
    main,
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

"""
Supply routes package for the Asset Management System
CRUD operations for supply models (parts, tools, part demands)
"""

from flask import Blueprint
from app.logger import get_logger

logger = get_logger("asset_management.routes.supply")

# Create supply blueprint
supply_bp = Blueprint('supply', __name__)

# Import route modules
from . import parts, tools, part_demands
from . import main as supply_main

__all__ = ['supply_bp', 'parts', 'tools', 'part_demands', 'main']

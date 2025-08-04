"""
Core routes package for core foundation models
Includes CRUD operations for User, MajorLocation, AssetType, MakeModel, Asset, Event
"""

from flask import Blueprint

bp = Blueprint('core', __name__)

# Import all core route modules
from . import users, locations, asset_types, make_models, assets, events 
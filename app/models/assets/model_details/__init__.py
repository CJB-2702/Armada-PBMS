#!/usr/bin/env python3
"""
Model Details Package
"""

from sqlalchemy import event
from app.models.assets.model_detail_virtual import set_row_id_after_insert

# Import all model detail classes
from .emissions_info import EmissionsInfo
from .model_info import ModelInfo

# Event listeners removed - will handle row_id setting manually for now

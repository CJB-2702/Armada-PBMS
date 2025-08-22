#!/usr/bin/env python3
"""
Part Demand Virtual Mixin
Mixin class for part demand models providing common functionality
"""

from app.models.core.user_created_base import UserCreatedBase
from app import db

class PartDemandVirtual(UserCreatedBase):
    """
    Virtual mixin class for part demands
    Provides common functionality and interface for all part demand types
    """
    __abstract__ = True
    part_name = db.Column(db.String(200), nullable=False)
    part_number = db.Column(db.String(100), nullable=True)
    quantity = db.Column(db.Float, nullable=False, default=1.0)
    unit = db.Column(db.String(50), nullable=False, default='each')
    notes = db.Column(db.Text, nullable=True)

    @property
    def total_cost(self):
        """Calculate total cost based on quantity and unit cost"""
        unit_cost = getattr(self, 'unit_cost', 0)
        quantity = getattr(self, 'quantity', 0)
        return unit_cost * quantity
    
    @property
    def is_consumable(self):
        """Check if this part is consumable"""
        return getattr(self, 'is_consumable', False)
    
    @property
    def is_required(self):
        """Check if this part is required"""
        return getattr(self, 'is_required', True)
    
    def get_formatted_quantity(self):
        """Get formatted quantity string"""
        quantity = getattr(self, 'quantity', 0)
        unit = getattr(self, 'unit', 'each')
        return f"{quantity} {unit}"
    
    def get_status_color(self):
        """Get status color for UI display"""
        status = getattr(self, 'status', 'Requested')
        status_colors = {
            'Requested': 'warning',
            'Ordered': 'info',
            'Received': 'success',
            'Used': 'secondary',
            'Cancelled': 'danger'
        }
        return status_colors.get(status, 'secondary')
    
    def __repr__(self):
        """String representation of the part demand"""
        return f'<{self.__class__.__name__} {getattr(self, "part_name", "Unknown")} x{getattr(self, "quantity", 0)} {getattr(self, "unit", "each")}>'

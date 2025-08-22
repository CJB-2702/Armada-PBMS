#!/usr/bin/env python3
"""
Template Part Demand Model
Represents part requirements defined in template action items
"""

from app.models.core.user_created_base import UserCreatedBase
from app.models.maintnence.part_demand_virtual import PartDemandVirtual
from app import db

class TemplatePartDemand(UserCreatedBase, PartDemandVirtual):
    """
    Part requirements defined in template action items
    """
    __tablename__ = 'template_part_demands'
    
    # Core fields
    part_name = db.Column(db.String(200), nullable=False)
    part_number = db.Column(db.String(100), nullable=True)
    quantity = db.Column(db.Float, nullable=False, default=1.0)
    unit = db.Column(db.String(50), nullable=False, default='each')
    notes = db.Column(db.Text, nullable=True)
    
    # Relationships
    template_action_item_id = db.Column(db.Integer, db.ForeignKey('template_action_items.id'), nullable=False)
    template_action_item = db.relationship('TemplateActionItem', back_populates='part_demands')
    
    def __repr__(self):
        """String representation of the template part demand"""
        return f'<TemplatePartDemand {self.part_name} x{self.quantity} {self.unit}>'
    


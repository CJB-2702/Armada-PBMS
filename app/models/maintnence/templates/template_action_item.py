#!/usr/bin/env python3
"""
Template Action Item Model
Represents standardized maintenance action items that can be used in action sets
"""

from app.models.core.user_created_base import UserCreatedBase
from app.models.maintnence.action_item_virtual import ActionItemVirtual
from app import db

class TemplateActionItem(ActionItemVirtual):
    """
    Standardized maintenance action items that can be used in action sets
    """
    __tablename__ = 'template_action_items'
    
    # Relationships
    template_action_set_id = db.Column(db.Integer, db.ForeignKey('template_action_sets.id'), nullable=False)
    template_action_set = db.relationship('TemplateActionSet', back_populates='action_items')
    part_demands = db.relationship('TemplatePartDemand', back_populates='template_action_item', cascade='all, delete-orphan')
    
    def __repr__(self):
        """String representation of the template action item"""
        return f'<TemplateActionItem {self.sequence_number}: {self.action_description}>'

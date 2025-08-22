#!/usr/bin/env python3
"""
Additional Scheduled Task Plan Model
Represents asset-specific maintenance requirements that override or supplement standard plans
"""

from app.models.core.user_created_base import UserCreatedBase
from app.models.maintnence.scheduled_task_plan_virtual import ScheduledTaskPlanVirtual
from app import db

class AdditionalScheduledTaskPlan(ScheduledTaskPlanVirtual):
    """
    Asset-specific maintenance requirements that override or supplement the standard plans
    """
    __tablename__ = 'additional_scheduled_task_plans'
    
    # Core fields
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    interval_meter1 = db.Column(db.Integer, nullable=True)
    interval_meter2 = db.Column(db.Integer, nullable=True)
    interval_meter3 = db.Column(db.Integer, nullable=True)
    interval_meter4 = db.Column(db.Integer, nullable=True)
    interval_days = db.Column(db.Integer, nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # Relationships
    asset_id = db.Column(db.Integer, db.ForeignKey('assets.id'), nullable=False)
    template_action_set_id = db.Column(db.Integer, db.ForeignKey('template_action_sets.id'), nullable=False)
    
    # Relationships
    asset = db.relationship('Asset')
    template_action_set = db.relationship('TemplateActionSet')
    
    def __repr__(self):
        """String representation of the additional scheduled task plan"""
        return f'<AdditionalScheduledTaskPlan {self.name} for {self.asset.name}>'
    
    def applies_to_asset(self, asset):
        """Check if this plan applies to a specific asset"""
        return self.is_active and self.asset_id == asset.id

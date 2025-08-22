#!/usr/bin/env python3
"""
Generic Scheduled Task Plan Model
Represents maintenance schedules that can apply to asset types, make/models, or both
"""

from app.models.core.user_created_base import UserCreatedBase
from app.models.maintnence.scheduled_task_plan_virtual import ScheduledTaskPlanVirtual
from app import db

class GenericScheduledTaskPlan(ScheduledTaskPlanVirtual):
    """
    Generic maintenance schedules that can apply to asset types, make/models, or both
    Both asset_type_id and make_model_id can be nullable, allowing flexible targeting
    """
    __tablename__ = 'generic_scheduled_task_plans'
    
    # Core fields
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    interval_meter1 = db.Column(db.Integer, nullable=True)
    interval_meter2 = db.Column(db.Integer, nullable=True)
    interval_meter3 = db.Column(db.Integer, nullable=True)
    interval_meter4 = db.Column(db.Integer, nullable=True)
    interval_days = db.Column(db.Integer, nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # Relationships - both nullable to allow flexible targeting
    asset_type_id = db.Column(db.Integer, db.ForeignKey('asset_types.id'), nullable=True)
    make_model_id = db.Column(db.Integer, db.ForeignKey('make_models.id'), nullable=True)
    template_action_set_id = db.Column(db.Integer, db.ForeignKey('template_action_sets.id'), nullable=False)
    
    # Relationships
    asset_type = db.relationship('AssetType')
    make_model = db.relationship('MakeModel')
    template_action_set = db.relationship('TemplateActionSet')
    
    def __repr__(self):
        """String representation of the generic scheduled task plan"""
        return f'<GenericScheduledTaskPlan {self.name} for {self.target_description}>'
    
    @property
    def plan_scope(self):
        """Get the scope of this plan (asset_type, make_model, both, or general)"""
        if self.asset_type_id and self.make_model_id:
            return 'specific_combination'
        elif self.asset_type_id:
            return 'asset_type'
        elif self.make_model_id:
            return 'make_model'
        else:
            return 'general'
    
    @property
    def scope_description(self):
        """Get a human-readable description of the plan scope"""
        if self.plan_scope == 'specific_combination':
            return f"Asset Type: {self.asset_type.name}, Make/Model: {self.make_model.make} {self.make_model.model}"
        elif self.plan_scope == 'asset_type':
            return f"Asset Type: {self.asset_type.name}"
        elif self.plan_scope == 'make_model':
            return f"Make/Model: {self.make_model.make} {self.make_model.model}"
        else:
            return "General (applies to all assets)"
    
    def applies_to_asset(self, asset):
        """Check if this plan applies to a specific asset"""
        if not self.is_active:
            return False
            
        # Check asset type match
        if self.asset_type_id and asset.asset_type_id != self.asset_type_id:
            return False
            
        # Check make/model match
        if self.make_model_id and asset.make_model_id != self.make_model_id:
            return False
            
        return True
    
    def get_applicable_assets(self):
        """Get all assets that this plan applies to"""
        from app.models.core import Asset
        
        query = Asset.query
        
        if self.asset_type_id:
            query = query.filter(Asset.asset_type_id == self.asset_type_id)
            
        if self.make_model_id:
            query = query.filter(Asset.make_model_id == self.make_model_id)
            
        return query.all()

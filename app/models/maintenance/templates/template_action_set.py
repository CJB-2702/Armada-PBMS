from app.models.core.user_created_base import UserCreatedBase
from app.models.maintenance.virtual_action_set import VirtualActionSet
from app import db
from datetime import datetime

class TemplateActionSet(VirtualActionSet):
    __tablename__ = 'template_action_sets'
    
    # Template-specific fields
    required_tools = db.Column(db.Text, nullable=True)  # comma-separated list
    required_parts = db.Column(db.Text, nullable=True)  # comma-separated list
    
    # Foreign Keys
    maintenance_plan_id = db.Column(db.Integer, db.ForeignKey('maintenance_plans.id'), nullable=True)
    
    # Relationships
    template_action_items = db.relationship('TemplateActionItem', lazy='dynamic')
    
    def __repr__(self):
        return f'<TemplateActionSet {self.task_name}>'
    
    def get_required_tools_list(self):
        """Get required tools as a list"""
        if self.required_tools:
            return [tool.strip() for tool in self.required_tools.split(',') if tool.strip()]
        return []
    
    def get_required_parts_list(self):
        """Get required parts as a list"""
        if self.required_parts:
            return [part.strip() for part in self.required_parts.split(',') if part.strip()]
        return []
    
    def get_total_estimated_duration(self):
        """Calculate total estimated duration from all action items"""
        total = 0
        for action_item in self.template_action_items:
            if action_item.estimated_duration:
                total += action_item.estimated_duration
        return total

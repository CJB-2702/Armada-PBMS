from app.models.core.user_created_base import UserCreatedBase
from app.models.maintenance.virtual_action_set import VirtualActionSet
from app import db
from datetime import datetime
from app.models.maintenance.templates.template_action_tool import TemplateActionTool
from app.models.maintenance.templates.template_part_demand import TemplatePartDemand
from sqlalchemy import func
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship


class TemplateActionSet(VirtualActionSet):
    __tablename__ = 'template_action_sets'
    # Foreign Keys
    maintenance_plan_id = db.Column(db.Integer, db.ForeignKey('maintenance_plans.id'), nullable=True)
    
    # Improved relationships with proper loading strategies
    maintenance_plans = relationship(
        'MaintenancePlan', 
        back_populates='template_action_set'
    )
    template_action_items = relationship(
        'TemplateActionItem', 
        back_populates='template_action_set',
        lazy='selectin',
        order_by='TemplateActionItem.sequence_order'
    )
    
    # Association proxies for easier access
    required_parts = association_proxy(
        'template_action_items', 
        'template_part_demands'
    )
    required_tools = association_proxy(
        'template_action_items',
        'template_action_tools'
    )
    action_names = association_proxy('template_action_items', 'action_name')

    
    def __repr__(self):
        return f'<TemplateActionSet {self.task_name}>'
    
    # Hybrid property for calculated fields
    @hybrid_property
    def total_estimated_duration(self):
        return sum(item.estimated_duration or 0 for item in self.template_action_items)
    
    @total_estimated_duration.expression
    def total_estimated_duration(cls):
        from app.models.maintenance.templates.template_action_item import TemplateActionItem
        return (
            db.session.query(func.coalesce(func.sum(TemplateActionItem.estimated_duration), 0))
            .filter(TemplateActionItem.template_action_set_id == cls.id)
            .scalar_subquery()
        )
    
    # Efficient aggregation using existing relationships
    def get_tools_summary(self):
        """Get tools summary using existing relationships - tools are reusable so we take max quantity"""
        tools_summary = {}
        
        # Use the relationship to iterate through action items and their tools
        for action_item in self.template_action_items:
            for template_tool in action_item.template_action_tools:
                tool_name = template_tool.tool.tool_name
                quantity = template_tool.quantity_required
                
                # For tools, we take the maximum quantity required across all actions
                # (since tools are reusable between actions)
                if tool_name in tools_summary:
                    tools_summary[tool_name] = max(tools_summary[tool_name], quantity)
                else:
                    tools_summary[tool_name] = quantity
        
        return tools_summary
    
    def get_parts_summary(self):
        """Get parts summary using existing relationships - parts are consumable so we sum quantities"""
        parts_summary = {}
        
        # Use the relationship to iterate through action items and their parts
        for action_item in self.template_action_items:
            for template_part in action_item.template_part_demands:
                part_name = template_part.part.part_name
                quantity = template_part.quantity_required
                
                # For parts, we sum the quantities (since parts are consumed by each action)
                if part_name in parts_summary:
                    parts_summary[part_name] += quantity
                else:
                    parts_summary[part_name] = quantity
        
        return parts_summary
    
    
    

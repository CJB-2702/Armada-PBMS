from app.models.core.user_created_base import UserCreatedBase
from app.models.maintenance.virtual_action_item import VirtualActionItem
from app import db
from datetime import datetime

class TemplateActionItem(VirtualActionItem):
    __tablename__ = 'template_action_items'
    
    is_required = db.Column(db.Boolean, default=True)
    minimum_staff_count = db.Column(db.Integer, nullable=False, default=1)
    instructions = db.Column(db.Text, nullable=True)
    instructions_type = db.Column(db.String(20), nullable=True)
    required_skills = db.Column(db.Text, nullable=True)

    # Foreign Keys
    template_action_set_id = db.Column(db.Integer, db.ForeignKey('template_action_sets.id'), nullable=False)
    
    # Relationships
    template_action_set = db.relationship('TemplateActionSet', back_populates='template_action_items')
    actions = db.relationship('Action', back_populates='template_action_item')
    template_action_attachments = db.relationship('TemplateActionAttachment', 
                                                foreign_keys='TemplateActionAttachment.attached_to_id',
                                                lazy='dynamic')
    template_part_demands = db.relationship('TemplatePartDemand', lazy='dynamic')
    template_action_tools = db.relationship('TemplateActionTool', lazy='dynamic')
    
    def __repr__(self):
        return f'<TemplateActionItem {self.action_name}>'
    
 
    
    def get_simple_tools_dict(self):
        """Get a simple dictionary of tools and their quantities"""
        tools_dict = {}
        for tool_template in self.template_action_tools:
            if tool_template.is_required:
                #because tools are reusable we need to get the max quantity required
                tools_dict[tool_template.tool.id] = max(tools_dict.get(tool_template.tool.id, 0), tool_template.quantity_required)
        return tools_dict
    
    def get_simple_parts_dict(self):
        """Get a simple dictionary of parts and their quantities"""
        parts_dict = {}
        for part_demand in self.template_part_demands:
            if not part_demand.is_optional:
                #because parts are not reusable we need to add the quantity required
                parts_dict[part_demand.part.id] = parts_dict.get(part_demand.part.id, 0) + part_demand.quantity_required
        return parts_dict



    #-------------------------------- additional Getters --------------------------------
    def get_required_skills_list(self):
        """Get required skills as a list"""
        if self.required_skills:
            return [skill.strip() for skill in self.required_skills.split(',') if skill.strip()]
        return []

    def get_required_parts(self):
        """Get all required parts from template part demands"""
        return [demand.part for demand in self.template_part_demands if demand.is_optional == False]
    
    def get_optional_parts(self):
        """Get all optional parts from template part demands"""
        return [demand.part for demand in self.template_part_demands if demand.is_optional == True]
    
    def get_required_tools(self):
        """Get all required tools from template action tools"""
        return [tool.tool for tool in self.template_action_tools if tool.is_required == True]
    
    def get_optional_tools(self):
        """Get all optional tools from template action tools"""
        return [tool.tool for tool in self.template_action_tools if tool.is_required == False]
    

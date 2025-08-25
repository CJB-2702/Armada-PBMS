from app.models.core.user_created_base import UserCreatedBase
from app.models.maintenance.virtual_action_item import VirtualActionItem
from app import db
from datetime import datetime

class TemplateActionItem(VirtualActionItem):
    __tablename__ = 'template_action_items'
    
    # Template-specific fields
    
    is_required = db.Column(db.Boolean, default=True)
    minimum_staff_count = db.Column(db.Integer, nullable=False, default=1)
    instructions = db.Column(db.Text, nullable=True)
    instructions_type = db.Column(db.String(20), nullable=True)
    required_skills = db.Column(db.Text, nullable=True)

    # Foreign Keys
    template_action_set_id = db.Column(db.Integer, db.ForeignKey('template_action_sets.id'), nullable=False)
    
    # Relationships
    template_action_attachments = db.relationship('TemplateActionAttachment', 
                                                foreign_keys='TemplateActionAttachment.template_action_item_id',
                                                lazy='dynamic')
    template_part_demands = db.relationship('TemplatePartDemand', lazy='dynamic')
    
    def __repr__(self):
        return f'<TemplateActionItem {self.action_name}>'
    
    def get_required_skills_list(self):
        """Get required skills as a list"""
        if self.required_skills:
            return [skill.strip() for skill in self.required_skills.split(',') if skill.strip()]
        return []
    
    def get_attachments_by_type(self, attachment_type=None):
        """Get attachments, optionally filtered by type"""
        if attachment_type:
            return self.template_action_attachments.filter_by(attachment_type=attachment_type)
        return self.template_action_attachments
    
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
    
    def get_tools_by_sequence(self):
        """Get all tools ordered by sequence order"""
        return sorted(self.template_action_tools, key=lambda x: x.sequence_order)
from app.models.core.user_created_base import UserCreatedBase
from app.models.maintenance.virtual_action_item import VirtualActionItem
from app import db

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
                                                back_populates='template_action_item',
                                                lazy='dynamic')
    template_part_demands = db.relationship('TemplatePartDemand', back_populates='template_action_item', lazy='dynamic')
    template_action_tools = db.relationship('TemplateActionTool', back_populates='template_action_item', lazy='dynamic')
    
    def __repr__(self):
        return f'<TemplateActionItem {self.action_name}>'

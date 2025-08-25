from app.models.core.attachment import VirtualAttachmentRefrence
from app import db
from datetime import datetime

class TemplateActionSetAttachment(VirtualAttachmentRefrence):
    __tablename__ = 'template_action_set_attachments'
    
    description = db.Column(db.Text, nullable=True)
    sequence_order = db.Column(db.Integer, nullable=False, default=1)
    is_required = db.Column(db.Boolean, default=False)
    
    # Foreign Keys
    template_action_set_id = db.Column(db.Integer, db.ForeignKey('template_action_sets.id'), nullable=False)
    
    # Set the attached_to_id and attached_to_type for the parent class
    attached_to_id = db.Column(db.Integer, db.ForeignKey('template_action_sets.id'), nullable=False)
    attached_to_type = db.Column(db.String(20), nullable=False, default='TemplateActionSet')
    
    # Relationships
    template_action_set = db.relationship('TemplateActionSet', 
                                        foreign_keys=[template_action_set_id])
    
    def __init__(self, *args, **kwargs):
        # Set attached_to_id from template_action_item_id if not provided
        if 'attached_to_id' not in kwargs and 'template_action_set_id' in kwargs:
            kwargs['attached_to_id'] = kwargs['template_action_set_id']
        super().__init__(*args, **kwargs)
    
    def __repr__(self):
        return f'<TemplateActionAttachment {self.attachment_type}: {self.description}>'

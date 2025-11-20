from app.data.core.event_info.attachment import VirtualAttachmentReference
from app import db
from datetime import datetime

class TemplateActionAttachment(VirtualAttachmentReference):
    __tablename__ = 'template_action_attachments'
    
    description = db.Column(db.Text, nullable=True)
    sequence_order = db.Column(db.Integer, nullable=False, default=1)
    is_required = db.Column(db.Boolean, default=False)
    

    
    # Set the attached_to_id and attached_to_type for the parent class
    attached_to_id = db.Column(db.Integer, db.ForeignKey('template_action_items.id'), nullable=False)
    attached_to_type = db.Column(db.String(20), nullable=False, default='TemplateActionItem')
    
    # Relationships
    template_action_item = db.relationship('TemplateActionItem', 
                                         foreign_keys=[attached_to_id],
                                         back_populates='template_action_attachments')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.attached_to_type = 'TemplateActionItem'
    
    def __repr__(self):
        return f'<TemplateActionAttachment {self.attachment_type}: {self.description}>'

from app.data.core.event_info.attachment import VirtualAttachmentReference
from app import db
from sqlalchemy.orm import relationship

class TemplateActionSetAttachment(VirtualAttachmentReference):
    """
    Attachments for template action sets
    Some information applies to the entire template, not individual actions
    """
    __tablename__ = 'template_action_set_attachments'
    
    # Parent reference - REQUIRED (serves as attached_to_id)
    template_action_set_id = db.Column(db.Integer, db.ForeignKey('template_action_sets.id'), nullable=False)
    
    # Additional fields
    description = db.Column(db.Text, nullable=True)
    sequence_order = db.Column(db.Integer, nullable=False, default=1)
    is_required = db.Column(db.Boolean, default=False)
    
    # Set attached_to_type for parent class
    attached_to_type = db.Column(db.String(20), nullable=False, default='TemplateActionSet')
    
    # Relationships
    template_action_set = relationship('TemplateActionSet', back_populates='template_action_set_attachments')
    attachment = relationship('Attachment', foreign_keys='TemplateActionSetAttachment.attachment_id', lazy='select')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.attached_to_type:
            self.attached_to_type = 'TemplateActionSet'
    
    def __repr__(self):
        return f'<TemplateActionSetAttachment {self.id}: {self.attachment_type}>'


from app.models.core.user_created_base import UserCreatedBase
from app import db
from datetime import datetime

class CommentAttachment(UserCreatedBase):
    __tablename__ = 'comment_attachments'
    
    # Relationships
    comment_id = db.Column(db.Integer, db.ForeignKey('comments.id'), nullable=False)
    attachment_id = db.Column(db.Integer, db.ForeignKey('attachments.id'), nullable=False)
    
    # Additional metadata
    display_order = db.Column(db.Integer, default=0)  # For ordering attachments in comments
    caption = db.Column(db.String(255), nullable=True)  # Optional caption for the attachment
    
    # Relationships
    comment = db.relationship('Comment', backref='comment_attachments')
    attachment = db.relationship('Attachment')
    
    def __repr__(self):
        return f'<CommentAttachment Comment:{self.comment_id} -> Attachment:{self.attachment_id}>' 
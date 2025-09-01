from app.models.core.user_created_base import UserCreatedBase
from app import db
from datetime import datetime

class MaintenanceDelay(UserCreatedBase):
    __tablename__ = 'maintenance_delays'

    maintenance_event_set_id = db.Column(db.Integer, db.ForeignKey('maintenance_event_sets.id'), nullable=True)
    delay_type = db.Column(db.String(20), nullable=True)
    delay_reason = db.Column(db.Text, nullable=True)
    delay_start_date = db.Column(db.DateTime, nullable=True)
    delay_end_date = db.Column(db.DateTime, nullable=True)
    delay_billable_hours = db.Column(db.Float, nullable=True)
    delay_notes = db.Column(db.Text, nullable=True)
    
    # Relationships
    maintenance_event_set = db.relationship('MaintenanceEventSet', backref='delays')
    
    def __repr__(self):
        return f'<MaintenanceDelay {self.id}: {self.delay_type} - {self.delay_reason}>'
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Note: create_delay_comment() should be called manually with user_id when needed
    
    def create_delay_comment(self, user_id):
        """Create a comment on the maintenance event set's event about this delay"""
        if self.maintenance_event_set:
            from app.models.maintenance.base.maintenance_event_set import MaintenanceEventSet
            from app.models.core.comment import Comment
            
            if self.maintenance_event_set.event_id:
                event_id = self.maintenance_event_set.event_id
                # Create comment content
                comment_content = f"Maintenance Delay: {self.delay_type}"
                if self.delay_reason:
                    comment_content += f"\n\nReason: {self.delay_reason}"
                if self.delay_start_date:
                    comment_content += f"\nStart Date: {self.delay_start_date.strftime('%Y-%m-%d %H:%M')}"
                if self.delay_end_date:
                    comment_content += f"\nEnd Date: {self.delay_end_date.strftime('%Y-%m-%d %H:%M')}"
                if self.delay_billable_hours:
                    comment_content += f"\nBillable Hours: {self.delay_billable_hours}"
                if self.delay_notes:
                    comment_content += f"\n\nAdditional Notes: {self.delay_notes}"
                
                # Create the comment
                comment = Comment(
                    content=comment_content,
                    event_id=event_id,
                    created_by_id=user_id
                )
                db.session.add(comment)
                db.session.commit()


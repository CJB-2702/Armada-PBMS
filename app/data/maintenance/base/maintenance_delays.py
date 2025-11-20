from app.data.core.user_created_base import UserCreatedBase
from app import db
from datetime import datetime

class MaintenanceDelay(UserCreatedBase):
    __tablename__ = 'maintenance_delays'

    maintenance_action_set_id = db.Column(db.Integer, db.ForeignKey('maintenance_action_sets.id'), nullable=True)
    delay_type = db.Column(db.String(20), nullable=True)
    delay_reason = db.Column(db.Text, nullable=True)
    delay_start_date = db.Column(db.DateTime, nullable=True)
    delay_end_date = db.Column(db.DateTime, nullable=True)
    delay_billable_hours = db.Column(db.Float, nullable=True)
    delay_notes = db.Column(db.Text, nullable=True)
    
    # Relationships
    maintenance_action_set = db.relationship('MaintenanceActionSet', back_populates='delays')
    
    def __repr__(self):
        return f'<MaintenanceDelay {self.id}: {self.delay_type} - {self.delay_reason}>'
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    #-------------------------------- Getters and Setters --------------------------------
    
    def _set_delay_type(self, value, user_id=None):
        """Set delay type with comment tracking"""
        old_value = self.delay_type
        self.delay_type = value
        if user_id and old_value != value:
            self._add_comment_to_maintenance_event(user_id, f"Delay type changed from '{old_value}' to '{value}'")
    
    def _set_delay_reason(self, value, user_id=None):
        """Set delay reason with comment tracking"""
        old_value = self.delay_reason
        self.delay_reason = value
        if user_id and old_value != value:
            self._add_comment_to_maintenance_event(user_id, f"Delay reason updated")
    
    def _set_delay_start_date(self, value, user_id=None):
        """Set delay start date with comment tracking"""
        old_value = self.delay_start_date
        self.delay_start_date = value
        if user_id and old_value != value:
            old_str = old_value.strftime('%Y-%m-%d %H:%M') if old_value else 'None'
            new_str = value.strftime('%Y-%m-%d %H:%M') if value else 'None'
            self._add_comment_to_maintenance_event(user_id, f"Delay start date changed from '{old_str}' to '{new_str}'")
    
    def _set_delay_end_date(self, value, user_id=None):
        """Set delay end date with comment tracking"""
        old_value = self.delay_end_date
        self.delay_end_date = value
        if user_id and old_value != value:
            old_str = old_value.strftime('%Y-%m-%d %H:%M') if old_value else 'None'
            new_str = value.strftime('%Y-%m-%d %H:%M') if value else 'None'
            self._add_comment_to_maintenance_event(user_id, f"Delay end date changed from '{old_str}' to '{new_str}'")
    
    def _add_comment_to_maintenance_event(self, user_id, comment_content):
        """Add comment to the maintenance action set"""
        if self.maintenance_action_set:
            self.maintenance_action_set.add_comment_to_event(user_id, comment_content)
    
    # Properties for getters
    @property
    def is_active(self):
        """Check if delay is currently active"""
        return self.delay_start_date and not self.delay_end_date
    
    @property
    def is_resolved(self):
        """Check if delay is resolved"""
        return self.delay_end_date is not None
    
    @property
    def duration_hours(self):
        """Calculate delay duration in hours"""
        if self.delay_start_date and self.delay_end_date:
            return (self.delay_end_date - self.delay_start_date).total_seconds() / 3600
        return None
    
    @property
    def is_billable(self):
        """Check if delay has billable hours"""
        return self.delay_billable_hours is not None and self.delay_billable_hours > 0
    
    #-------------------------------- Delay Methods --------------------------------
    
    def create_delay_comment(self, user_id):
        """Create a comment on the maintenance action set's event about this delay"""
        if self.maintenance_action_set:
            comment_content = (
                f"Maintenance Delay: {self.delay_type}"
                f"\n\nReason: {self.delay_reason}"
                f"\nStart Date: {(self.delay_start_date.strftime('%Y-%m-%d %H:%M') if self.delay_start_date else 'None')}"
                f"\nEnd Date: {(self.delay_end_date.strftime('%Y-%m-%d %H:%M') if self.delay_end_date else 'None')}"
                f"\nBillable Hours: {self.delay_billable_hours}"
                f"\n\nAdditional Notes: {self.delay_notes}"
            )
            self.maintenance_action_set.add_comment_to_event(user_id, comment_content)
    
    def resolve_delay(self, user_id, end_date=None, billable_hours=None):
        """Resolve the delay"""
        if end_date:
            self._set_delay_end_date(end_date, user_id)
        else:
            self._set_delay_end_date(datetime.utcnow(), user_id)
        
        if billable_hours is not None:
            self.delay_billable_hours = billable_hours
        
        self.updated_by_id = user_id
        self.create_delay_comment(user_id)

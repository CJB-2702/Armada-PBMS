from app.models.maintenance.virtual_action_item import VirtualActionItem
from app import db
from sqlalchemy.orm import relationship
from datetime import datetime

class Action(VirtualActionItem):
    """Base class for all actions"""
    __tablename__ = 'actions'
    
    # Action-specific fields
    status = db.Column(db.String(20), nullable=False, default='Not Started')
    scheduled_start_time = db.Column(db.DateTime, nullable=True)
    start_time = db.Column(db.DateTime, nullable=True)
    end_time = db.Column(db.DateTime, nullable=True)
    billable_hours = db.Column(db.Float, nullable=True) 
    completion_notes = db.Column(db.Text, nullable=True)
    
    # Foreign Keys
    maintenance_action_set_id = db.Column(db.Integer, db.ForeignKey('maintenance_action_sets.id'), nullable=False)
    template_action_item_id = db.Column(db.Integer, db.ForeignKey('template_action_items.id'), nullable=True)
    
    # Relationships
    maintenance_action_set = relationship('MaintenanceActionSet', back_populates='actions')
    template_action_item = relationship('TemplateActionItem', back_populates='actions')
    part_demands = relationship('PartDemand', back_populates='action', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Action {self.action_name}: {self.status}>'
    
    #-------------------------------- Getters and Setters --------------------------------
    
    def _set_status(self, value, user_id=None):
        """Set status with comment tracking"""
        old_value = self.status
        self.status = value
        if user_id and old_value != value:
            self._add_comment_to_maintenance_event(user_id, f"Action '{self.action_name}' status changed from '{old_value}' to '{value}'")
    
    def _set_start_time(self, value, user_id=None):
        """Set start time with comment tracking"""
        old_value = self.start_time
        self.start_time = value
        if user_id and old_value != value:
            old_str = old_value.strftime('%Y-%m-%d %H:%M') if old_value else 'None'
            new_str = value.strftime('%Y-%m-%d %H:%M') if value else 'None'
            self._add_comment_to_maintenance_event(user_id, f"Action '{self.action_name}' start time changed from '{old_str}' to '{new_str}'")
    
    def _set_end_time(self, value, user_id=None):
        """Set end time with comment tracking"""
        old_value = self.end_time
        self.end_time = value
        if user_id and old_value != value:
            old_str = old_value.strftime('%Y-%m-%d %H:%M') if old_value else 'None'
            new_str = value.strftime('%Y-%m-%d %H:%M') if value else 'None'
            self._add_comment_to_maintenance_event(user_id, f"Action '{self.action_name}' end time changed from '{old_str}' to '{new_str}'")
    
    def _set_completion_notes(self, value, user_id=None):
        """Set completion notes with comment tracking"""
        old_value = self.completion_notes
        self.completion_notes = value
        if user_id and old_value != value:
            self._add_comment_to_maintenance_event(user_id, f"Action '{self.action_name}' completion notes updated")
    
    def _add_comment_to_maintenance_event(self, user_id, comment_content):
        """Add comment to the maintenance action set"""
        if self.maintenance_action_set:
            self.maintenance_action_set.add_comment_to_event(user_id, comment_content)
    
    # Properties for getters
    @property
    def is_not_started(self):
        return self.status == 'Not Started'
    
    @property
    def is_in_progress(self):
        return self.status == 'In Progress'
    
    @property
    def is_completed(self):
        return self.status == 'Completed'
    
    @property
    def is_skipped(self):
        return self.status == 'Skipped'
    
    @property
    def duration_hours(self):
        """Calculate duration in hours"""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds() / 3600
        return None
    
    @property
    def is_overdue(self):
        """Check if action is overdue"""
        if self.scheduled_start_time and self.status in ['Not Started', 'In Progress']:
            return datetime.utcnow() > self.scheduled_start_time
        return False
    
    #-------------------------------- Action Methods --------------------------------
    
    def start_action(self, user_id):
        """Start the action"""
        self._set_start_time(datetime.utcnow(), user_id)
        self._set_status('In Progress', user_id)
        self.updated_by_id = user_id
    
    def complete_action(self, user_id, notes=None, status='Completed', billable_hours=None):
        """Complete the action"""
        self._set_end_time(datetime.utcnow(), user_id)
        self._set_completion_notes(notes, user_id)
        self._set_status(status, user_id)
        
        # Calculate duration if start time exists
        if not billable_hours:
            if not self.end_time:
                self._set_end_time(datetime.utcnow(), user_id)
            
            if not self.start_time:
                self.billable_hours = 0
            else:
                duration = (self.end_time - self.start_time).total_seconds() / 3600
                self.billable_hours = round(duration, 2)
        else:
            self.billable_hours = billable_hours
        
        self.updated_by_id = user_id
        comment_content = f"Action completed: {self.action_name}"
        if notes:
            comment_content += f"\n\nCompletion Notes: {notes}"
        self._add_comment_to_maintenance_event(user_id, comment_content)
    
    def skip_action(self, user_id, reason=None):
        """Skip the action"""
        self._set_status('Skipped', user_id)
        self._set_completion_notes(f"Skipped: {reason}" if reason else "Skipped", user_id)
        self.updated_by_id = user_id
        
        comment_content = f"Action skipped: {self.action_name}"
        if reason:
            comment_content += f"\n\nReason: {reason}"
        self._add_comment_to_maintenance_event(user_id, comment_content)
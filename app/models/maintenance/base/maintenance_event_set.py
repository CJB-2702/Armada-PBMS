from app.models.core.event import Event, EventDetailVirtual
from app import db
from datetime import datetime
from app.models.maintenance.virtual_action_set import VirtualActionSet

class MaintenanceEventSet(EventDetailVirtual, VirtualActionSet):
    __tablename__ = 'maintenance_event_sets'

    # Maintenance-specific fields
    maintenance_plan_id = db.Column(db.Integer, db.ForeignKey('maintenance_plans.id'), nullable=True)
    status = db.Column(db.String(20), default='Planned')  # Planned, In Progress, Completed, Cancelled
    priority = db.Column(db.String(20), default='Medium')  # Low, Medium, High, Critical
    scheduled_date = db.Column(db.DateTime, nullable=True)
    actual_start_date = db.Column(db.DateTime, nullable=True)
    actual_end_date = db.Column(db.DateTime, nullable=True)
    completed_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    completion_notes = db.Column(db.Text, nullable=True)
    delay_notes = db.Column(db.Text, nullable=True)
    
    # Relationships
    maintenance_plan = db.relationship('MaintenancePlan')
    completed_by = db.relationship('User', foreign_keys=[completed_by_id], backref='completed_maintenance_event_sets')
    
    def __repr__(self):
        return f'<MaintenanceEventSet {self.id}: {self.status}>'
    
    @property
    def is_completed(self):
        return self.status == 'Completed'
    
    @property
    def is_in_progress(self):
        return self.status == 'In Progress'
    
    @property
    def is_planned(self):
        return self.status == 'Planned'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.status = 'Planned'
        self.priority = 'Medium'
        self.scheduled_date = kwargs.get('scheduled_date') or datetime.utcnow()
        self.actual_start_date = None
        self.actual_end_date = None

    
    def create_event(self):
        """Create a maintenance event for this header"""
        from app.models.core.event import Event
        
        event = Event(
            event_type='Maintenance Event',
            description=f"Maintenance event created: {self.task_name}",
            user_id=self.created_by_id,
            asset_id=self.asset_id,
            major_location_id=self.major_location_id if hasattr(self, 'major_location_id') else None
        )
        db.session.add(event)
        db.session.flush()  # Get the event ID
        self.event_id = event.id

    
    def start_maintenance(self, user_id, notes=None):
        """Start the maintenance event"""
        self.status = 'In Progress'
        self.actual_start_date = datetime.utcnow()
        self.updated_by_id = user_id
        
        # Create comment for maintenance start
        from app.models.core.comment import Comment
        comment_content = f"Maintenance started: {self.task_name}"
        if notes:
            comment_content += f"\n\nNotes: {notes}"
        
        comment = Comment(
            content=comment_content,
            event_id=self.event_id,
            created_by_id=user_id
        )
        db.session.add(comment)
        
        # Update event details
        self.update_event_details(user_id, "Maintenance Started", comment_content)
    
    def complete_maintenance(self, user_id, notes=None):
        """Complete the maintenance event"""
        self.status = 'Completed'
        self.actual_end_date = datetime.utcnow()
        self.completed_by_id = user_id
        self.completion_notes = notes
        self.updated_by_id = user_id
        
        # Create comment for maintenance completion
        from app.models.core.comment import Comment
        comment_content = f"Maintenance completed: {self.task_name}"
        if notes:
            comment_content += f"\n\nCompletion Notes: {notes}"
        
        comment = Comment(
            content=comment_content,
            event_id=self.event_id,
            created_by_id=user_id
        )
        db.session.add(comment)
        
        # Update event details
        self.update_event_details(user_id, "Maintenance Completed", comment_content)
    
    def cancel_maintenance(self, user_id, reason=None):
        """Cancel the maintenance event"""
        self.status = 'Cancelled'
        self.completion_notes = f"Cancelled: {reason}" if reason else "Cancelled"
        self.updated_by_id = user_id
        
        # Create comment for maintenance cancellation
        from app.models.core.comment import Comment
        comment_content = f"Maintenance cancelled: {self.task_name}"
        if reason:
            comment_content += f"\n\nCancellation Reason: {reason}"
        
        comment = Comment(
            content=comment_content,
            event_id=self.event_id,
            created_by_id=user_id
        )
        db.session.add(comment)
        
        # Update event details
        self.update_event_details(user_id, "Maintenance Cancelled", comment_content)
    
    def update_event_details(self, user_id, event_type, description):
        """Update the associated event with new details"""
        if self.event_id:
            from app.models.core.event import Event
            event = Event.query.get(self.event_id)
            if event:
                event.event_type = event_type
                event.description = description
                event.updated_by_id = user_id
                event.updated_at = datetime.utcnow()

from app.models.core.event import Event, EventDetailVirtual
from app.models.maintenance.templates.template_action_set import TemplateActionSet
from app import db
from datetime import datetime
from app.models.maintenance.virtual_action_set import VirtualActionSet
from sqlalchemy import func
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import validates, relationship
from app.models.core.comment import Comment


class MaintenanceActionSet(EventDetailVirtual, VirtualActionSet):
    __tablename__ = 'maintenance_action_sets'
    
    # Table constraints and indexes removed for initial implementation

    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=True)
    asset_id = db.Column(db.Integer, db.ForeignKey('assets.id'), nullable=True)
    template_action_set_id = db.Column(db.Integer, db.ForeignKey('template_action_sets.id'), nullable=True)
    maintenance_plan_id = db.Column(db.Integer, db.ForeignKey('maintenance_plans.id'), nullable=True)

    # Maintenance-specific fields with proper constraints
    status = db.Column(db.String(20), default='Planned')
    priority = db.Column(db.String(20), default='Medium')
    scheduled_date = db.Column(db.DateTime, nullable=True)
    start_date = db.Column(db.DateTime, nullable=True)
    end_date = db.Column(db.DateTime, nullable=True)
    completed_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    completion_notes = db.Column(db.Text, nullable=True)
    delay_notes = db.Column(db.Text, nullable=True)
    
    # Improved relationships with proper loading strategies
    maintenance_plan = relationship('MaintenancePlan', back_populates='maintenance_action_sets')
    completed_by = relationship('User', foreign_keys=[completed_by_id], backref='completed_maintenance_events')
    template_action_set = relationship('TemplateActionSet', foreign_keys=[template_action_set_id], lazy='select')
    actions = relationship('Action', back_populates='maintenance_action_set', lazy='selectin', order_by='Action.sequence_order')
    delays = relationship('MaintenanceDelay', lazy='selectin')
    
    # Association proxies for easier access
    action_names = association_proxy('actions', 'action_name')
    action_statuses = association_proxy('actions', 'status')



    def __repr__(self):
        return f'<MaintenanceActionSet {self.id}: {self.status}>'
    
    #-------------------------------- Getters and Setters --------------------------------
    
    def _set_status(self, value, user_id=None):
        """Set status with comment tracking"""
        old_value = self.status
        self.status = value
        if user_id and old_value != value:
            self.add_comment_to_event(user_id, f"Status changed from '{old_value}' to '{value}'")
    
    def _set_priority(self, value, user_id=None):
        """Set priority with comment tracking"""
        old_value = self.priority
        self.priority = value
        if user_id and old_value != value:
            self.add_comment_to_event(user_id, f"Priority changed from '{old_value}' to '{value}'")
    
    def _set_scheduled_date(self, value, user_id=None):
        """Set scheduled date with comment tracking"""
        old_value = self.scheduled_date
        self.scheduled_date = value
        if user_id and old_value != value:
            old_str = old_value.strftime('%Y-%m-%d %H:%M') if old_value else 'None'
            new_str = value.strftime('%Y-%m-%d %H:%M') if value else 'None'
            self.add_comment_to_event(user_id, f"Scheduled date changed from '{old_str}' to '{new_str}'")
    
    def _set_completion_notes(self, value, user_id=None):
        """Set completion notes with comment tracking"""
        old_value = self.completion_notes
        self.completion_notes = value
        if user_id and old_value != value:
            self.add_comment_to_event(user_id, f"Completion notes updated")
    
    # Properties for getters
    @property
    def is_planned(self):
        return self.status == 'Planned'
    
    @property
    def is_in_progress(self):
        return self.status == 'In Progress'
    
    @property
    def is_completed(self):
        return self.status == 'Completed'
    
    @property
    def is_cancelled(self):
        return self.status == 'Cancelled'
    
    @property
    def is_overdue(self):
        """Check if maintenance is overdue"""
        if self.scheduled_date and self.status in ['Planned', 'In Progress']:
            return datetime.utcnow() > self.scheduled_date
        return False
    
    @property
    def duration_hours(self):
        """Calculate total duration in hours"""
        if self.start_date and self.end_date:
            return (self.end_date - self.start_date).total_seconds() / 3600
        return None
    
    @property
    def completion_percentage(self):
        """Calculate completion percentage based on actions"""
        if not self.actions:
            return 0
        completed_actions = len([a for a in self.actions if a.status == 'Completed'])
        return (completed_actions / len(self.actions)) * 100

    #-------------------------------- Init --------------------------------
    def __init__(self, **kwargs):
        # Set the event type for maintenance events before calling super().__init__
        if 'event_type' not in kwargs:
            kwargs['event_type'] = 'Maintenance'
        # Set event_type as instance attribute so it's available to create_event()
        self.event_type = kwargs.get('event_type', 'Maintenance')
        self.description = kwargs.get('description', f"Maintenance event: {kwargs.get('task_name', 'Unknown')}")
        
        # Map user_id to created_by_id for compatibility with EventDetailVirtual
        if 'user_id' in kwargs and 'created_by_id' not in kwargs:
            kwargs['created_by_id'] = kwargs['user_id']
        
        # Ensure user_id is available for create_event() method
        self.user_id = kwargs.get('created_by_id') or kwargs.get('user_id')
        
        # Remove event_type from kwargs since it's not a column in MaintenanceActionSet
        # It's only used for event creation
        if 'event_type' in kwargs:
            kwargs.pop('event_type')
        
        super().__init__(**kwargs)
        self.status = 'Planned'
        self.scheduled_date = kwargs.get('scheduled_date') or datetime.utcnow()
        # Note: template_action_set relationship and related initialization will be handled
        # after the object is committed to the database, not in __init__
        self._create_event()

    
    def _create_event(self):
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



    # Note: Creation logic moved to MaintenanceActionSetFactory
    




    #-------------------------------- Functions --------------------------------
    def get_next_sequence_order(self):
        """Get the next sequence order for actions in this maintenance event set"""
        if not self.actions:
            return 1
        max_order = max(action.sequence_order for action in self.actions)
        return max_order + 1

    def add_comment_to_event(self, user_id, comment_content):
        """Add a comment to the event"""
        
        comment = Comment(
            content=comment_content,
            event_id=self.event_id,
            created_by_id=user_id)
        db.session.add(comment)
        db.session.commit()
    
    def update_event_status(self, user_id, event_type, description):
        """Update the associated event with new details"""
        if self.event_id:
            from app.models.core.event import Event
            event = db.session.get(Event, self.event_id)
            if event:
                event.status = event_type
                event.updated_by_id = user_id
                event.updated_at = datetime.utcnow()

    def start_maintenance(self, user_id, notes=None):
        """Start the maintenance event"""
        self._set_status('In Progress', user_id)
        self.start_date = datetime.utcnow()
        self.updated_by_id = user_id
        
        comment_content = f"Maintenance started: {self.task_name}"
        if notes:
            comment_content += f"\n\nNotes: {notes}"
        self.add_comment_to_event(user_id, comment_content)
        self.update_event_status(user_id, "In Progress", comment_content)
    
    def complete_maintenance(self, user_id, notes=None):
        """Complete the maintenance event"""
        self._set_status('Completed', user_id)
        self.end_date = datetime.utcnow()
        self.completed_by_id = user_id
        self._set_completion_notes(notes, user_id)
        self.updated_by_id = user_id
        
        comment_content = f"Maintenance completed: {self.task_name}"
        if notes:
            comment_content += f"\n\nCompletion Notes: {notes}"
        self.add_comment_to_event(user_id, comment_content)
        self.update_event_status(user_id, "Completed", comment_content)
    
    def cancel_maintenance(self, user_id, reason=None):
        """Cancel the maintenance event"""
        self._set_status('Cancelled', user_id)
        self._set_completion_notes(f"Cancelled: {reason}" if reason else "Cancelled", user_id)
        self.updated_by_id = user_id
        
        # Create comment for maintenance cancellation
        from app.models.core.comment import Comment
        comment_content = f"Maintenance cancelled: {self.task_name}"
        if reason:
            comment_content += f"\n\nCancellation Reason: {reason}"
        
        self.add_comment_to_event(user_id, comment_content)
        self.update_event_status(user_id, "Cancelled", comment_content)
    

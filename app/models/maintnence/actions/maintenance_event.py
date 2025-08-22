#!/usr/bin/env python3
"""
Core Maintenance Event Model
Represents maintenance work orders and service events
"""

from app.models.core.user_created_base import UserCreatedBase
from app.models.core.event import Event
from app import db
from datetime import datetime
from sqlalchemy import event

class MaintenanceEvent(UserCreatedBase):
    """
    Core maintenance event entity representing maintenance work orders and service events
    Inherits from Event base class for consistency with the broader asset management system
    """
    __tablename__ = 'maintenance_events'
    
    # Core fields
    maintenance_number = db.Column(db.String(50), unique=True, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    priority = db.Column(db.String(20), default='Normal')  # Low, Normal, High, Critical
    maintenance_status = db.Column(db.String(50), default='Created')  # Created, In Progress, Completed, Cancelled
    
    # Timing
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    scheduled_date = db.Column(db.DateTime, nullable=True)
    started_date = db.Column(db.DateTime, nullable=True)
    completed_date = db.Column(db.DateTime, nullable=True)
    due_date = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    asset_id = db.Column(db.Integer, db.ForeignKey('assets.id'), nullable=False)
    assigned_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    
    # Template relationships
    template_action_set_id = db.Column(db.Integer, db.ForeignKey('template_action_sets.id'), nullable=True)
    
    # Relationships
    asset = db.relationship('Asset', foreign_keys=[asset_id], backref='maintenance_events')
    assigned_user = db.relationship('User', foreign_keys=[assigned_user_id], backref='assigned_maintenance_events')
    event = db.relationship('Event', foreign_keys=[event_id], backref='maintenance_event')
    template_action_set = db.relationship('TemplateActionSet', foreign_keys=[template_action_set_id], backref='maintenance_events')
    
    # Related collections
    actions = db.relationship('Action', back_populates='maintenance_event', cascade='all, delete-orphan')
    part_demands = db.relationship('PartDemand', back_populates='maintenance_event', cascade='all, delete-orphan')
    
    def __repr__(self):
        """String representation of the maintenance event"""
        return f'<MaintenanceEvent {self.maintenance_number}: {self.title}>'
    
    def __init__(self, **kwargs):
        """Initialize maintenance event with automatic event creation"""
        super().__init__(**kwargs)
        
        # Create the base event record
        if not self.event_id:
            self.create_base_event()
    
    def create_base_event(self):
        """Create the base Event record for this maintenance event"""
        event = Event(
            event_type="Maintenance Event Created",
            description=f"Maintenance event '{self.title}' ({self.maintenance_number}) was created",
            user_id=self.created_by_id,
            asset_id=self.asset_id
        )
        db.session.add(event)
        db.session.flush()  # Get the event ID
        self.event_id = event.id
    
    def update_status(self, new_status, changed_by_id, reason=None):
        """Update maintenance status and timing"""
        old_status = self.maintenance_status
        self.maintenance_status = new_status
        
        # Update timing based on status
        if new_status == 'In Progress' and not self.started_date:
            self.started_date = datetime.utcnow()
        elif new_status == 'Completed' and not self.completed_date:
            self.completed_date = datetime.utcnow()
        
        # Create status update event
        status_event = Event(
            event_type="Maintenance Status Changed",
            description=f"Maintenance status changed from '{old_status}' to '{new_status}'" + (f" - {reason}" if reason else ""),
            user_id=changed_by_id,
            asset_id=self.asset_id
        )
        db.session.add(status_event)
    
    def create_actions_from_template(self):
        """Create actions from the assigned template action set"""
        if self.template_action_set and not self.actions:
            for template_item in self.template_action_set.template_action_items:
                from app.models.maintnence.action import Action
                action = Action(
                    sequence_number=template_item.sequence_number,
                    action_description=template_item.action_description,
                    estimated_duration=template_item.estimated_duration,
                    required_skills=template_item.required_skills,
                    notes=template_item.notes,
                    maintenance_event_id=self.id,
                    template_action_item_id=template_item.id,
                    created_by_id=self.created_by_id
                )
                db.session.add(action)
                
                # Create part demands from template
                for template_part in template_item.template_part_demands:
                    from app.models.maintnence.part_demand import PartDemand
                    part_demand = PartDemand(
                        part_name=template_part.part_name,
                        part_number=template_part.part_number,
                        quantity=template_part.quantity,
                        unit=template_part.unit,
                        notes=template_part.notes,
                        maintenance_event_id=self.id,
                        action_id=action.id,
                        template_part_demand_id=template_part.id,
                        created_by_id=self.created_by_id
                    )
                    db.session.add(part_demand)
    
    @property
    def is_overdue(self):
        """Check if the maintenance event is overdue"""
        if self.due_date and self.maintenance_status not in ['Completed', 'Cancelled']:
            return datetime.utcnow() > self.due_date
        return False
    
    @property
    def progress_percentage(self):
        """Calculate completion percentage based on actions"""
        if not self.actions:
            return 0
        
        completed_actions = sum(1 for action in self.actions if action.status == 'Completed')
        total_actions = len(self.actions)
        
        return (completed_actions / total_actions) * 100 if total_actions > 0 else 0

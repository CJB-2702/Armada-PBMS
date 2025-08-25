#!/usr/bin/env python3
"""
Core Dispatch Model
Represents work orders and dispatch assignments
"""

from app.models.core.event import EventDetailVirtual
from app import db
from datetime import datetime
from sqlalchemy import event

class Dispatch(EventDetailVirtual):
    """
    Core dispatch entity representing work orders and assignments
    """
    __tablename__ = 'dispatches'
    
    # Core fields
    dispatch_number = db.Column(db.String(50), unique=True, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    priority = db.Column(db.String(20), default='Normal')  # Low, Normal, High, Critical
    status = db.Column(db.String(50), default='Created')  # Created, Assigned, In Progress, Completed, Cancelled
    
    # Timing
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    assigned_date = db.Column(db.DateTime, nullable=True)
    started_date = db.Column(db.DateTime, nullable=True)
    completed_date = db.Column(db.DateTime, nullable=True)
    due_date = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    asset_id = db.Column(db.Integer, db.ForeignKey('assets.id'), nullable=True)
    assigned_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    major_location_id = db.Column(db.Integer, db.ForeignKey('major_locations.id'), nullable=True)
    
    # Location tracking (copied from asset for historical reference)
    dispatch_location_id = db.Column(db.Integer, db.ForeignKey('major_locations.id'), nullable=True)
    
    # Relationships
    asset = db.relationship('Asset', foreign_keys=[asset_id], backref='dispatches')
    assigned_user = db.relationship('User', foreign_keys=[assigned_user_id], backref='assigned_dispatches')
    major_location = db.relationship('MajorLocation', foreign_keys=[major_location_id], backref='dispatches')
    dispatch_location = db.relationship('MajorLocation', foreign_keys=[dispatch_location_id], backref='dispatch_locations')
    
    def __repr__(self):
        """String representation of the dispatch"""
        return f'<Dispatch {self.dispatch_number}: {self.title}>'
    
    @property
    def event_type(self):
        """Event type for this dispatch"""
        return "Dispatch"
    
    def __init__(self, **kwargs):
        """Initialize dispatch with automatic location copying"""
        super().__init__(**kwargs)
        
        # Auto-set dispatch_location_id from asset if not provided
        if self.asset_id and not self.dispatch_location_id:
            from app.models.core.asset import Asset
            asset = Asset.query.get(self.asset_id)
            if asset and asset.major_location_id:
                self.dispatch_location_id = asset.major_location_id
    
    def create_event(self):
        """Create an initial event for this dispatch"""
        from app.models.core.event import Event
        event = Event(
            event_type="Dispatch Created",
            description=f"Dispatch '{self.title}' ({self.dispatch_number}) was created",
            user_id=self.created_by_id,
            asset_id=self.asset_id,
            major_location_id=self.major_location_id
        )
        db.session.add(event)
        db.session.flush()  # Get the event ID
        self.event_id = event.id
    
    def update_status(self, new_status, changed_by_id, reason=None):
        """Update dispatch status and create status history record"""
        old_status = self.status
        self.status = new_status
        
        # Update timing based on status
        if new_status == 'Assigned' and not self.assigned_date:
            self.assigned_date = datetime.utcnow()
        elif new_status == 'In Progress' and not self.started_date:
            self.started_date = datetime.utcnow()
        elif new_status == 'Completed' and not self.completed_date:
            self.completed_date = datetime.utcnow()
        
        # Create status history record
        from app.models.dispatching.dispatch_status_history import DispatchStatusHistory
        status_history = DispatchStatusHistory(
            dispatch_id=self.id,
            status_from=old_status,
            status_to=new_status,
            change_reason=reason,
            changed_by_id=changed_by_id
        )
        db.session.add(status_history)
        
        # Create event for status change
        from app.models.core.event import Event
        event = Event(
            event_type=f"Dispatch {new_status}",
            description=f"Dispatch '{self.title}' status changed from {old_status} to {new_status}",
            user_id=changed_by_id,
            asset_id=self.asset_id,
            major_location_id=self.major_location_id
        )
        db.session.add(event)
    
    @property
    def is_overdue(self):
        """Check if dispatch is overdue"""
        if self.due_date and self.status not in ['Completed', 'Cancelled']:
            return datetime.utcnow() > self.due_date
        return False
    
    @property
    def duration_hours(self):
        """Calculate total duration in hours"""
        if self.started_date and self.completed_date:
            return (self.completed_date - self.started_date).total_seconds() / 3600
        return None

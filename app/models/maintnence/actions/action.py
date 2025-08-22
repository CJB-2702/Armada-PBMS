#!/usr/bin/env python3
"""
Action Model
Represents individual maintenance actions within a maintenance event
"""

from app.models.maintnence.action_item_virtual import ActionItemVirtual
from app import db

class Action(ActionItemVirtual):
    """
    Individual maintenance actions within a maintenance event
    """
    __tablename__ = 'actions'
    
    # Core fields
    status = db.Column(db.String(50), nullable=False, default='Pending')  # Pending, In Progress, Completed, Skipped
    actual_duration = db.Column(db.Integer, nullable=True)  # in minutes
    
    # Timestamps
    started_date = db.Column(db.DateTime, nullable=True)
    completed_date = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    maintenance_event_id = db.Column(db.Integer, db.ForeignKey('maintenance_events.id'), nullable=False)
    maintenance_event = db.relationship('MaintenanceEvent', back_populates='actions')
    part_demands = db.relationship('PartDemand', back_populates='action', cascade='all, delete-orphan')
    
    def __repr__(self):
        """String representation of the action"""
        return f'<Action {self.sequence_number}: {self.action_description} ({self.status})>'

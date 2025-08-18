#!/usr/bin/env python3
"""
Dispatch Status History Model
Track status changes for dispatches
"""

from app.models.core.user_created_base import UserCreatedBase
from app import db
from datetime import datetime

class DispatchStatusHistory(UserCreatedBase, db.Model):
    """
    Track status changes for dispatches
    """
    __tablename__ = 'dispatch_status_history'
    
    # Core fields
    dispatch_id = db.Column(db.Integer, db.ForeignKey('dispatches.id'), nullable=False)
    status_from = db.Column(db.String(50), nullable=True)
    status_to = db.Column(db.String(50), nullable=False)
    change_reason = db.Column(db.Text, nullable=True)
    changed_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    changed_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    dispatch = db.relationship('Dispatch', backref='status_history')
    changed_by = db.relationship('User', foreign_keys=[changed_by_id], backref='dispatch_status_changes')
    
    def __repr__(self):
        """String representation of the status history record"""
        return f'<DispatchStatusHistory {self.dispatch_id}: {self.status_from} -> {self.status_to}>'
    
    @property
    def status_change_summary(self):
        """Get a summary of the status change"""
        if self.status_from:
            return f"Status changed from {self.status_from} to {self.status_to}"
        else:
            return f"Status set to {self.status_to}"

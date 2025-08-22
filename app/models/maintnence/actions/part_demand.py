#!/usr/bin/env python3
"""
Part Demand Model
Represents parts and materials required for specific maintenance actions
"""

from app.models.core.user_created_base import UserCreatedBase
from app.models.maintnence.part_demand_virtual import PartDemandVirtual
from app import db
from datetime import datetime

class PartDemand(UserCreatedBase, PartDemandVirtual, db.Model):
    """
    Parts and materials required for specific maintenance actions
    """
    __tablename__ = 'part_demands'
    
    # Core fields

    status = db.Column(db.String(50), nullable=False, default='Requested')  # Requested, Ordered, Received, Used
    
    
    # Timestamps for tracking
    ordered_date = db.Column(db.DateTime, nullable=True)
    received_date = db.Column(db.DateTime, nullable=True)
    used_date = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    action_id = db.Column(db.Integer, db.ForeignKey('actions.id'), nullable=False)
    action = db.relationship('Action', back_populates='part_demands')
    
    def __repr__(self):
        """String representation of the part demand"""
        return f'<PartDemand {self.part_name} x{self.quantity} {self.unit} ({self.status})>'
    
    def update_status(self, new_status, updated_by_id, notes=None):
        """Update part demand status and timing"""
        old_status = self.status
        self.status = new_status
        
        if notes:
            self.notes = notes
        
        # Update timing based on status
        if new_status == 'Ordered' and not self.ordered_date:
            self.ordered_date = datetime.utcnow()
        elif new_status == 'Received' and not self.received_date:
            self.received_date = datetime.utcnow()
        elif new_status == 'Used' and not self.used_date:
            self.used_date = datetime.utcnow()
    
    @property
    def is_available(self):
        """Check if the part is available for use"""
        return self.status in ['Received', 'Used']
    
    @property
    def is_ordered(self):
        """Check if the part has been ordered"""
        return self.status in ['Ordered', 'Received', 'Used']
    
    @property
    def is_used(self):
        """Check if the part has been used"""
        return self.status == 'Used'
    
    def get_procurement_delay(self):
        """Calculate delay between required and received dates"""
        if self.received_date and self.ordered_date:
            return (self.received_date - self.ordered_date).days
        return None
    
    def get_time_to_use(self):
        """Calculate time between received and used dates"""
        if self.used_date and self.received_date:
            return (self.used_date - self.received_date).days
        return None

#!/usr/bin/env python3
"""
Action Item Virtual Mixin
Mixin class for action item models providing common functionality
"""

from app.models.core.user_created_base import UserCreatedBase
from app import db

class ActionItemVirtual(UserCreatedBase):
    """
    Virtual mixin class for action items
    Provides common functionality and interface for all action item types
    """

    __abstract__ = True

        # Core fields
    sequence_number = db.Column(db.Integer, nullable=False)
    action_description = db.Column(db.Text, nullable=False)
    estimated_duration = db.Column(db.Integer, nullable=True)  # in minutes
    notes = db.Column(db.Text, nullable=True)
    
    @property
    def is_completed(self):
        """Check if the action is completed"""
        return getattr(self, 'status', None) in ['Completed', 'Skipped']
    
    @property
    def duration_variance(self):
        """Calculate variance between estimated and actual duration"""
        actual = getattr(self, 'actual_duration', None)
        estimated = getattr(self, 'estimated_duration', None)
        if actual and estimated:
            return actual - estimated
        return None
    
    def get_duration_variance(self):
        """Calculate duration variance"""
        return self.duration_variance
    
    def get_formatted_actual_duration(self):
        """Get formatted actual duration string"""
        actual_duration = getattr(self, 'actual_duration', None)
        if not actual_duration:
            return "Not recorded"
        
        hours = actual_duration // 60
        minutes = actual_duration % 60
        
        if hours > 0 and minutes > 0:
            return f"{hours}h {minutes}m"
        elif hours > 0:
            return f"{hours}h"
        else:
            return f"{minutes}m"
    
    def get_formatted_estimated_duration(self):
        """Get formatted estimated duration string"""
        estimated_duration = getattr(self, 'estimated_duration', None)
        if not estimated_duration:
            return "Not specified"
        
        hours = estimated_duration // 60
        minutes = estimated_duration % 60
        
        if hours > 0 and minutes > 0:
            return f"{hours}h {minutes}m"
        elif hours > 0:
            return f"{hours}h"
        else:
            return f"{minutes}m"
    
    def __repr__(self):
        """String representation of the action item"""
        return f'<{self.__class__.__name__} {getattr(self, "sequence_number", "?")}: {getattr(self, "action_description", "Unknown")}>'

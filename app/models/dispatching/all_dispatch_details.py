#!/usr/bin/env python3
"""
All Dispatch Detail Master Table
Master table that tracks all dispatch detail records
Provides a unified view of all dispatch detail types
"""

from app.models.core.user_created_base import UserCreatedBase
from app import db

class AllDispatchDetail(UserCreatedBase, db.Model):
    """
    Master table that tracks all dispatch detail records
    Provides a unified view of all dispatch detail types
    """
    __tablename__ = 'all_dispatch_details'
    
    # Core fields
    table_name = db.Column(db.String(100), nullable=False)  # Name of the detail table
    dispatch_id = db.Column(db.Integer, db.ForeignKey('dispatches.id'), nullable=False)
    
    # Relationships
    dispatch = db.relationship('Dispatch', backref='all_details')
    
    def __repr__(self):
        """String representation of the dispatch detail record"""
        return f'<AllDispatchDetail {self.table_name}:{self.dispatch_id}>'

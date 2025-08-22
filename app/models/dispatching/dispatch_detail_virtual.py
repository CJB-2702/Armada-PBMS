#!/usr/bin/env python3
"""
Dispatch Detail Virtual Base Class
Base class for all dispatch-specific detail tables
"""

from app.models.core.user_created_base import UserCreatedBase
from app import db
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy import event
from app.models.dispatching.all_dispatch_details import AllDispatchDetail

class DispatchDetailVirtual(UserCreatedBase):
    """
    Base class for all dispatch-specific detail tables
    Provides common functionality for dispatch detail tables
    """
    __abstract__ = True
    
    # Common field for all dispatch detail tables
    dispatch_id = db.Column(db.Integer, db.ForeignKey('dispatches.id'), nullable=False)
    
    # Foreign key to master table
    detail_id = db.Column(db.Integer, db.ForeignKey('all_dispatch_details.id'), nullable=False)
    
    # Relationship to master table
    @declared_attr
    def detail(cls):
        # Use the class name to create a unique backref
        backref_name = f'{cls.__name__.lower()}_records'
        return db.relationship('AllDispatchDetail', backref=backref_name)
    
    # Relationship to Dispatch
    @declared_attr
    def dispatch(cls):
        # Use the class name to create a unique backref
        backref_name = f'{cls.__name__.lower()}_details'
        return db.relationship('Dispatch', backref=backref_name)
    
    def __repr__(self):
        """String representation of the dispatch detail table"""
        return f'<{self.__class__.__name__} Dispatch:{self.dispatch_id}>'
    
    @classmethod
    def is_dispatch_detail(cls):
        """Dispatch detail tables are always dispatch details"""
        return True
    
    def __init__(self, *args, **kwargs):
        """Initialize the dispatch detail record with automatic master table integration"""
        kwargs['detail_id'] = self.create_master_table_entry(kwargs)
        super().__init__(*args, **kwargs)

    def create_master_table_entry(self, kwargs):
        """
        Create master table entry and return its ID
        This method is called from __init__ to set the foreign key
        """
        # Create master table entry
        master_record = AllDispatchDetail(
            table_name=self.__tablename__,
            dispatch_id=kwargs.get('dispatch_id'),
            created_by_id=kwargs.get('created_by_id'),
        )
        db.session.add(master_record)
        db.session.flush()  # Get the ID without committing
        
        return master_record.id
    
    def remove_from_master_table(self, detail_id):
        """
        Remove a detail record from the appropriate master table by ID
        This method is called from the custom delete() method
        """
        # Find and delete the master table entry
        master_record = AllDispatchDetail.query.get(detail_id)
        if master_record:
            db.session.delete(master_record)
    
    def delete(self):
        """
        Custom delete method that ensures master table cleanup
        Captures the ID before deletion and cleans up master table
        """
        # Capture the ID before deletion
        detail_id = self.detail_id
        super().delete()
        self.remove_from_master_table(detail_id)

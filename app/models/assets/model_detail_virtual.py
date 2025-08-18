#!/usr/bin/env python3
"""
Model Detail Virtual Base Class
Base class for all model-specific detail tables
"""

from app.models.core.user_created_base import UserCreatedBase
from app import db
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy import event
from app.models.assets.all_details import AllModelDetail

def set_row_id_after_insert(mapper, connection, target):
    """Set the row_id after the detail record is inserted"""
    if hasattr(target, 'set_row_id'):
        target.set_row_id()

class ModelDetailVirtual(UserCreatedBase, db.Model):
    """
    Base class for all model-specific detail tables
    Provides common functionality for model detail tables
    """
    __abstract__ = True
    
    # Common field for all model detail tables
    make_model_id = db.Column(db.Integer, db.ForeignKey('make_models.id'), nullable=False)
    
    # Foreign key to master table - references all_model_details.id
    detail_id = db.Column(db.Integer, db.ForeignKey('all_model_details.id'), nullable=False)
    
    # Relationship to master table
    @declared_attr
    def detail(cls):
        # Use the class name to create a unique backref
        backref_name = f'{cls.__name__.lower()}_records'
        return db.relationship('AllModelDetail', backref=backref_name)
    
    # Relationship to MakeModel
    @declared_attr
    def make_model(cls):
        # Use the class name to create a unique backref
        backref_name = f'{cls.__name__.lower()}_details'
        return db.relationship('MakeModel', backref=backref_name)
    
    def __repr__(self):
        """String representation of the model detail table"""
        return f'<{self.__class__.__name__} Model:{self.make_model_id}>'
    
    @classmethod
    def is_asset_detail(cls):
        """Model detail tables are never asset details"""
        return False
    
    @classmethod
    def is_model_detail(cls):
        """Model detail tables are always model details"""
        return True
    
    def __init__(self, *args, **kwargs):
        """Initialize the model detail record with automatic master table integration"""
        # Create the parent record in all_model_details first
        detail_id = self.create_master_table_entry(kwargs)
        kwargs['detail_id'] = detail_id
        super().__init__(*args, **kwargs)


    def create_master_table_entry(self, kwargs):
        """
        Create master table entry and return its ID
        This method is called from __init__ to set the foreign key
        """
        # Create the parent record in all_model_details
        master_record = AllModelDetail(
            table_name=self.__tablename__,
            make_model_id=kwargs.get('make_model_id'),
            created_by_id=kwargs.get('created_by_id'),
        )
        
        db.session.add(master_record)
        db.session.flush()  # Get the ID without committing
        
        return master_record.id
    
    def set_row_id(self):
        """Set the row_id after the detail record is created"""
        if hasattr(self, 'id') and self.id:
            master_record = AllModelDetail.query.filter_by(
                table_name=self.__tablename__,
                make_model_id=self.make_model_id,
                row_id=None
            ).first()
            if master_record:
                master_record.row_id = self.id
                # Don't flush here - let the main transaction handle it

    def update_row_id(self):
        """Update the row_id in the master table after the record is committed"""
        if hasattr(self, 'id') and self.id and hasattr(self, 'detail_id'):
            master_record = AllModelDetail.query.get(self.detail_id)
            if master_record and master_record.row_id is None:
                master_record.row_id = self.id
                db.session.commit()
                return True
        return False

    def remove_from_master_table(self, detail_id):
        """
        Remove a detail record from the appropriate master table by ID
        This method is called from the custom delete() method
        """
        master_record = AllModelDetail.query.get(detail_id)
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
        # Clean up the master table entry
        self.remove_from_master_table(detail_id)

# Note: Event listeners for abstract classes don't work in SQLAlchemy
# The event listener will be registered on concrete classes in their __init__.py files

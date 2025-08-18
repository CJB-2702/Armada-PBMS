#!/usr/bin/env python3
"""
Asset Detail Virtual Base Class
Base class for all asset-specific detail tables
"""

from app.models.core.user_created_base import UserCreatedBase
from app import db
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy import event
from app.models.assets.all_details import AllAssetDetail

def set_row_id_after_insert(mapper, connection, target):
    """Set the row_id after the detail record is inserted"""
    if hasattr(target, 'set_row_id'):
        target.set_row_id()

class AssetDetailVirtual(UserCreatedBase, db.Model):
    """
    Base class for all asset-specific detail tables
    Provides common functionality for asset detail tables
    """
    __abstract__ = True
    
    # Common field for all asset detail tables
    asset_id = db.Column(db.Integer, db.ForeignKey('assets.id'), nullable=False)
    
    # Foreign key to master table
    detail_id = db.Column(db.Integer, db.ForeignKey('all_asset_details.id'), nullable=False)
    
    # Relationship to master table
    @declared_attr
    def detail(cls):
        # Use the class name to create a unique backref
        backref_name = f'{cls.__name__.lower()}_records'
        return db.relationship('AllAssetDetail', backref=backref_name)
    
    # Relationship to Asset
    @declared_attr
    def asset(cls):
        # Use the class name to create a unique backref
        backref_name = f'{cls.__name__.lower()}_details'
        return db.relationship('Asset', backref=backref_name)
    
    def __repr__(self):
        """String representation of the asset detail table"""
        return f'<{self.__class__.__name__} Asset:{self.asset_id}>'
    
    @classmethod
    def is_asset_detail(cls):
        """Asset detail tables are always asset details"""
        return True
    
    @classmethod
    def is_model_detail(cls):
        """Asset detail tables are never model details"""
        return False
    
    def __init__(self, *args, **kwargs):
        """Initialize the asset detail record with automatic master table integration"""
        # Create master table entry first
        detail_id = self.create_master_table_entry(kwargs)
        kwargs['detail_id'] = detail_id
        super().__init__(*args, **kwargs)

    
    def create_master_table_entry(self, kwargs):
        """
        Create master table entry and return its ID
        This method is called from __init__ to set the foreign key
        """
        # Create master table entry
        master_record = AllAssetDetail(
            table_name=self.__tablename__,
            asset_id=kwargs.get('asset_id'),
            created_by_id=kwargs.get('created_by_id'),
        )
        db.session.add(master_record)
        db.session.flush()  # Get the ID without committing
        
        return master_record.id
    
    def set_row_id(self):
        """Set the row_id after the detail record is created"""
        if hasattr(self, 'id') and self.id:
            master_record = AllAssetDetail.query.filter_by(
                table_name=self.__tablename__,
                asset_id=self.asset_id,
                row_id=None
            ).first()
            if master_record:
                master_record.row_id = self.id
                # Don't flush here - let the main transaction handle it
    
    def update_row_id(self):
        """Update the row_id in the master table after the record is committed"""
        if hasattr(self, 'id') and self.id and hasattr(self, 'detail_id'):
            master_record = AllAssetDetail.query.get(self.detail_id)
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
        # Find and delete the master table entry
        master_record = AllAssetDetail.query.get(detail_id)
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

# Note: Event listeners for abstract classes don't work in SQLAlchemy
# The event listener will be registered on concrete classes in their __init__.py files

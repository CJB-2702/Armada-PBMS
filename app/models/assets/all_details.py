#!/usr/bin/env python3
"""
All Details Master Tables
Master tables that act as registries for all asset and model detail records
"""

from app.models.core.user_created_base import UserCreatedBase
from app import db
from sqlalchemy.ext.declarative import declared_attr

#CB yes i know this is duplicate data and this could be created using a view
# but i want to be able to query all details for an asset or model easily
# and i want them to not have collisions on row_id

class AllAssetDetail(UserCreatedBase, db.Model):
    """
    Master table that acts as a registry for all asset detail records
    Provides a single point of querying all details for an asset
    """
    __tablename__ = 'all_asset_details'
    
    # Override the default tablename from UserCreatedBase
    @declared_attr
    def __tablename__(cls):
        return 'all_asset_details'
    
    # Master table fields
    table_name = db.Column(db.String(100), nullable=False)  # e.g., 'purchase_info', 'vehicle_registration'
    row_id = db.Column(db.Integer, nullable=True)  # ID from the specific detail table (set after child creation)
    asset_id = db.Column(db.Integer, db.ForeignKey('assets.id'), nullable=False)
    
    # Relationships
    @declared_attr
    def asset(cls):
        return db.relationship('Asset', backref='all_detail_records')
    
    def __init__(self, **kwargs):
        """Initialize the master asset detail record"""
        super().__init__()
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def __repr__(self):
        """String representation of the master detail record"""
        return f'<AllAssetDetail Asset:{self.asset_id} Table:{self.table_name} Row:{self.row_id}>'
    
    @classmethod
    def get_details_for_asset(cls, asset_id):
        """Get all detail records for a specific asset"""
        return cls.query.filter_by(asset_id=asset_id).all()
    
    @classmethod
    def get_details_by_type(cls, asset_id, table_name):
        """Get detail records of a specific type for an asset"""
        return cls.query.filter_by(asset_id=asset_id, table_name=table_name).all()
    
    def set_row_id(self, row_id):
        """Set the row_id after the child record is created"""
        self.row_id = row_id
        db.session.flush()


class AllModelDetail(UserCreatedBase, db.Model):
    """
    Master table that acts as a registry for all model detail records
    Provides a single point of querying all details for a model
    """
    __tablename__ = 'all_model_details'
    
    # Override the default tablename from UserCreatedBase
    @declared_attr
    def __tablename__(cls):
        return 'all_model_details'
    
    # Master table fields
    table_name = db.Column(db.String(100), nullable=False)  # e.g., 'model_info', 'emissions_info'
    row_id = db.Column(db.Integer, nullable=True)  # ID from the specific detail table (set after child creation)
    make_model_id = db.Column(db.Integer, db.ForeignKey('make_models.id'), nullable=False)
    
    # Relationships
    @declared_attr
    def make_model(cls):
        return db.relationship('MakeModel', backref='all_detail_records')
    
    def __init__(self, **kwargs):
        """Initialize the master model detail record"""
        super().__init__()
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def __repr__(self):
        """String representation of the master detail record"""
        return f'<AllModelDetail Model:{self.make_model_id} Table:{self.table_name} Row:{self.row_id}>'
    
    @classmethod
    def get_details_for_model(cls, make_model_id):
        """Get all detail records for a specific model"""
        return cls.query.filter_by(make_model_id=make_model_id).all()
    
    @classmethod
    def get_details_by_type(cls, make_model_id, table_name):
        """Get detail records of a specific type for a model"""
        return cls.query.filter_by(make_model_id=make_model_id, table_name=table_name).all()
    
    def set_row_id(self, row_id):
        """Set the row_id after the child record is created"""
        self.row_id = row_id
        db.session.flush()

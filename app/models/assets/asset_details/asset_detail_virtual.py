#!/usr/bin/env python3
"""
Asset Detail Virtual Base Class
Base class for all asset-specific detail tables
"""

from app.models.assets.detail_virtual_template import DetailTableVirtualTemplate
from app import db
from sqlalchemy.ext.declarative import declared_attr

class AssetDetailVirtual(DetailTableVirtualTemplate):
    """
    Base class for all asset-specific detail tables
    Provides common functionality for asset detail tables
    """
    __abstract__ = True
    
    # Common field for all asset detail tables
    asset_id = db.Column(db.Integer, db.ForeignKey('assets.id'), nullable=False)
    
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
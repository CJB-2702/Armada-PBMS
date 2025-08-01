#!/usr/bin/env python3
"""
Detail Table Virtual Template System
Base classes for all detail table functionality in Phase 2
"""

from app.models.core.user_created_base import UserCreatedBase
from app import db

class DetailTableVirtualTemplate(UserCreatedBase, db.Model):
    """
    Abstract base class for all detail table functionality
    Provides common fields and methods for all detail tables
    """
    __abstract__ = True
    
    # Common fields inherited from UserCreatedBase:
    # - id (Integer, Primary Key)
    # - created_at (DateTime, Default UTC now)
    # - created_by_id (Integer, Foreign Key to User)
    # - updated_at (DateTime, Default UTC now, onupdate)
    # - updated_by_id (Integer, Foreign Key to User)
    
    # Relationships inherited from UserCreatedBase:
    # - created_by (Relationship to User)
    # - updated_by (Relationship to User)
    
    def __repr__(self):
        """String representation of the detail table"""
        return f'<{self.__class__.__name__} {self.id}>'
    
    @classmethod
    def get_detail_table_type(cls):
        """Get the detail table type identifier"""
        return cls.__name__.lower()
    
    @classmethod
    def is_asset_detail(cls):
        """Check if this is an asset detail table"""
        return hasattr(cls, 'asset_id')
    
    @classmethod
    def is_model_detail(cls):
        """Check if this is a model detail table"""
        return hasattr(cls, 'make_model_id') 
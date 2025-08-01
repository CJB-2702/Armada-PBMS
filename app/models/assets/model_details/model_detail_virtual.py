#!/usr/bin/env python3
"""
Model Detail Virtual Base Class
Base class for all model-specific detail tables
"""

from app.models.assets.detail_virtual_template import DetailTableVirtualTemplate
from app import db

class ModelDetailVirtual(DetailTableVirtualTemplate):
    """
    Base class for all model-specific detail tables
    Provides common functionality for model detail tables
    """
    __abstract__ = True
    
    # Common field for all model detail tables
    make_model_id = db.Column(db.Integer, db.ForeignKey('make_models.id'), nullable=False)
    
    # Relationship to MakeModel
    make_model = db.relationship('MakeModel', backref='model_details')
    
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
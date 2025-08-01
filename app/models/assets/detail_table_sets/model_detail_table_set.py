#!/usr/bin/env python3
"""
Model Detail Table Set
Configuration container that defines additional detail table types for a specific model beyond what the asset type provides
"""

from app.models.core.user_created_base import UserCreatedBase
from app import db

class ModelDetailTableSet(UserCreatedBase, db.Model):
    """
    Configuration container that defines additional detail table types for a specific model beyond what the asset type provides
    """
    __tablename__ = 'model_detail_table_sets'
    
    # Configuration fields
    make_model_id = db.Column(db.Integer, db.ForeignKey('make_models.id'), nullable=False)
    detail_table_type = db.Column(db.String(100), nullable=False)  # e.g., 'emissions_info', 'model_info'
    is_asset_detail = db.Column(db.Boolean, default=False)  # True for asset details, False for model details
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    make_model = db.relationship('MakeModel', backref='detail_table_sets')
    
    def __repr__(self):
        """String representation of the model detail table set"""
        detail_type = "asset" if self.is_asset_detail else "model"
        return f'<ModelDetailTableSet {self.make_model.make} {self.make_model.model}:{self.detail_table_type} ({detail_type})>'
    
    @classmethod
    def get_detail_table_types_for_model(cls, make_model_id):
        """Get all detail table types configured for a specific model"""
        return cls.query.filter_by(
            make_model_id=make_model_id,
            is_active=True
        ).all()
    
    @classmethod
    def get_asset_detail_types_for_model(cls, make_model_id):
        """Get asset detail table types configured for a specific model"""
        return cls.query.filter_by(
            make_model_id=make_model_id,
            is_asset_detail=True,
            is_active=True
        ).all()
    
    @classmethod
    def get_model_detail_types_for_model(cls, make_model_id):
        """Get model detail table types configured for a specific model"""
        return cls.query.filter_by(
            make_model_id=make_model_id,
            is_asset_detail=False,
            is_active=True
        ).all() 
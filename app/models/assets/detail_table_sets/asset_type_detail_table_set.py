#!/usr/bin/env python3
"""
Asset Type Detail Table Set
Configuration container that defines which detail table types are available for a specific asset type
"""

from app.models.core.user_created_base import UserCreatedBase
from app import db

class AssetTypeDetailTableSet(UserCreatedBase, db.Model):
    """
    Configuration container that defines which detail table types are available for a specific asset type
    """
    __tablename__ = 'asset_type_detail_table_sets'
    
    # Configuration fields
    asset_type_id = db.Column(db.Integer, db.ForeignKey('asset_types.id'), nullable=False)
    detail_table_type = db.Column(db.String(100), nullable=False)  # e.g., 'purchase_info', 'vehicle_registration'
    is_asset_detail = db.Column(db.Boolean, default=True)  # True for asset details, False for model details
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    asset_type = db.relationship('AssetType', backref='detail_table_sets')
    
    def __repr__(self):
        """String representation of the asset type detail table set"""
        detail_type = "asset" if self.is_asset_detail else "model"
        return f'<AssetTypeDetailTableSet {self.asset_type.name}:{self.detail_table_type} ({detail_type})>'
    
    @classmethod
    def get_detail_table_types_for_asset_type(cls, asset_type_id):
        """Get all detail table types configured for a specific asset type"""
        return cls.query.filter_by(
            asset_type_id=asset_type_id,
            is_active=True
        ).all()
    
    @classmethod
    def get_asset_detail_types_for_asset_type(cls, asset_type_id):
        """Get asset detail table types configured for a specific asset type"""
        return cls.query.filter_by(
            asset_type_id=asset_type_id,
            is_asset_detail=True,
            is_active=True
        ).all()
    
    @classmethod
    def get_model_detail_types_for_asset_type(cls, asset_type_id):
        """Get model detail table types configured for a specific asset type"""
        return cls.query.filter_by(
            asset_type_id=asset_type_id,
            is_asset_detail=False,
            is_active=True
        ).all() 
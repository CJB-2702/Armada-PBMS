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
    
    @classmethod
    def create_detail_table_rows(cls, asset_id, make_model_id):
        """Create detail table rows based on model configurations"""
        try:
            # Get all detail table configurations for this model
            detail_configs = cls.get_detail_table_types_for_model(make_model_id)
            
            for config in detail_configs:
                cls._create_single_detail_row(config, asset_id, make_model_id)
                
        except Exception as e:
            print(f"Error creating model detail table rows for asset {asset_id}: {e}")
    
    @classmethod
    def _create_single_detail_row(cls, config, asset_id, make_model_id):
        """Create a single detail table row based on configuration"""
        try:
            # Detail table registry mapping
            detail_table_registry = {
                'purchase_info': 'app.models.assets.asset_details.purchase_info.PurchaseInfo',
                'vehicle_registration': 'app.models.assets.asset_details.vehicle_registration.VehicleRegistration',
                'toyota_warranty_receipt': 'app.models.assets.asset_details.toyota_warranty_receipt.ToyotaWarrantyReceipt',
                'emissions_info': 'app.models.assets.model_details.emissions_info.EmissionsInfo',
                'model_info': 'app.models.assets.model_details.model_info.ModelInfo'
            }
            
            detail_table_class_path = detail_table_registry.get(config.detail_table_type)
            if not detail_table_class_path:
                print(f"Warning: Unknown detail table type '{config.detail_table_type}'")
                return
            
            # Import the detail table class
            module_path, class_name = detail_table_class_path.rsplit('.', 1)
            module = __import__(module_path, fromlist=[class_name])
            detail_table_class = getattr(module, class_name)
            
            # Create the detail table row
            if config.is_asset_detail:
                # Create asset-specific detail row
                detail_row = detail_table_class(asset_id=asset_id)
            else:
                # Create model-specific detail row (check if it already exists)
                existing_row = detail_table_class.query.filter_by(make_model_id=make_model_id).first()
                if existing_row:
                    return  # Already exists, don't create duplicate
                detail_row = detail_table_class(make_model_id=make_model_id)
            
            # Add to session (don't commit - let the main transaction handle it)
            db.session.add(detail_row)
            
        except Exception as e:
            print(f"Error creating detail row for {config.detail_table_type}: {e}")
            # Don't rollback here - let the main transaction handle it 
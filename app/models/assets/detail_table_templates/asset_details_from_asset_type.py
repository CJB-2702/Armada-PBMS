#!/usr/bin/env python3
"""
Asset Type Detail Table Set
Configuration container that defines which detail table types are available for a specific asset type
"""

from app.models.core.user_created_base import UserCreatedBase
from app.logger import get_logger
logger = get_logger("asset_management.models.assets")
from app import db

class AssetDetailTemplateByAssetType(UserCreatedBase):
    """
    Configuration container that defines which detail table types are available for a specific asset type
    """
    __tablename__ = 'asset_details_from_asset_type'
    
    # Configuration fields
    asset_type_id = db.Column(db.Integer, db.ForeignKey('asset_types.id'), nullable=False)
    detail_table_type = db.Column(db.String(100), nullable=False)  # e.g., 'purchase_info', 'vehicle_registration'

    
    # Relationships
    asset_type = db.relationship('AssetType', backref='asset_detail_templates')
    
    def __repr__(self):
        """String representation of the asset type detail table set"""
        return f'<AssetDetailTemplateByAssetType AssetType:{self.asset_type_id}:{self.detail_table_type}>'
    
    @classmethod
    def get_detail_table_types_for_asset_type(cls, asset_type_id):
        """Get all detail table types configured for a specific asset type"""
        return cls.query.filter(
            (cls.asset_type_id == asset_type_id) | (cls.asset_type_id == None)
        ).all()
    
    @classmethod
    def create_detail_table_rows(cls, asset):
        """Create detail table rows based on asset type configurations"""
        logger.debug(f"DEBUG: AssetDetailTemplateByAssetType.create_detail_table_rows called for asset {asset.id}")
        try:
            # Get the asset type ID from the asset's make_model relationship
            asset_type_id = asset.asset_type_id
            if not asset_type_id:
                logger.warning(f"DEBUG: No asset type found for asset {asset.id}")
                return
            
            # Get all detail table configurations for this asset type
            detail_configs = cls.get_detail_table_types_for_asset_type(asset_type_id)
            logger.debug(f"DEBUG: Found {len(detail_configs)} detail configurations")
            logger.debug(f"DEBUG: Detail configs: {detail_configs}")
            
            for config in detail_configs:
                logger.debug(f"DEBUG: Creating detail row for {config.detail_table_type}")
                cls._create_single_detail_row(config, asset.id)
        except Exception as e:
            logger.debug(f"Error creating asset type detail table rows for asset {asset.id}: {e}")
        
    
    @classmethod
    def _create_single_detail_row(cls, config, asset_id):
        """Create a single detail table row based on configuration"""
        logger.debug(f"DEBUG: _create_single_detail_row called for {config.detail_table_type}")
        try:
            # Detail table registry mapping
            detail_table_registry = {
                'purchase_info': 'app.models.assets.asset_details.purchase_info.PurchaseInfo',
                'vehicle_registration': 'app.models.assets.asset_details.vehicle_registration.VehicleRegistration',
                'toyota_warranty_receipt': 'app.models.assets.asset_details.toyota_warranty_receipt.ToyotaWarrantyReceipt',
            }
            
            detail_table_class_path = detail_table_registry.get(config.detail_table_type)
            if not detail_table_class_path:
                logger.debug(f"Warning: Unknown detail table type '{config.detail_table_type}'")
                return
            
            logger.debug(f"DEBUG: Detail table class path: {detail_table_class_path}")
            
            # Import the detail table class
            module_path, class_name = detail_table_class_path.rsplit('.', 1)
            module = __import__(module_path, fromlist=[class_name])
            detail_table_class = getattr(module, class_name)
            
            logger.debug(f"DEBUG: Detail table class: {detail_table_class}")
            
            # Create the detail table row
            logger.debug(f"DEBUG: Creating asset detail row for asset_id={asset_id}")
            existing_row = detail_table_class.query.filter_by(asset_id=asset_id).first()
            if existing_row:
                logger.debug(f"DEBUG: Asset detail row already exists for asset {asset_id}, skipping")
                return  # Already exists, don't create duplicate
            detail_row = detail_table_class(asset_id=asset_id)
            logger.debug(f"DEBUG: Created detail row: {detail_row}")
            
            # Add to session (don't commit - let the main transaction handle it)
            db.session.add(detail_row)
            logger.debug(f"DEBUG: Added detail row to session")

        except Exception as e:
            logger.debug(f"Error creating detail row for {config.detail_table_type}: {e}")
            # Don't rollback here - let the main transaction handle it 
            pass
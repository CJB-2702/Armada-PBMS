#!/usr/bin/env python3
"""
Asset Type Detail Table Set
Configuration container that defines which detail table types are available for a specific asset type
"""

from app.models.core.user_created_base import UserCreatedBase
from app.logger import get_logger
logger = get_logger("asset_management.models.assets")
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
    
    @classmethod
    def create_detail_table_rows(cls, asset_id, make_model_id):
        """Create detail table rows based on asset type configurations"""
        logger.debug(f"DEBUG: AssetTypeDetailTableSet.create_detail_table_rows called for asset {asset_id}")
        try:
            # Get the asset to determine its asset type
            from app.models.core.asset import Asset
            asset = Asset.query.get(asset_id)
            if not asset or not asset.asset_type:
                logger.debug(f"DEBUG: Asset or asset type not found")
                return
            
            asset_type_id = asset.asset_type.id
            logger.debug(f"DEBUG: Asset type ID: {asset_type_id}")
            
            # Get all detail table configurations for this asset type
            detail_configs = cls.get_detail_table_types_for_asset_type(asset_type_id)
            logger.debug(f"DEBUG: Found {len(detail_configs)} detail configurations")
            
            for config in detail_configs:
                logger.debug(f"DEBUG: Creating detail row for {config.detail_table_type}")
                cls._create_single_detail_row(config, asset_id, make_model_id)
                
        except Exception as e:
            logger.debug(f"Error creating asset type detail table rows for asset {asset_id}: {e}")
        
        # Update row_ids for all created detail rows
        cls._update_pending_row_ids()
    
    @classmethod
    def _update_pending_row_ids(cls):
        """Update row_ids for all pending detail rows"""
        if hasattr(cls, '_pending_detail_rows') and cls._pending_detail_rows:
            for detail_row in cls._pending_detail_rows:
                if hasattr(detail_row, 'update_row_id'):
                    detail_row.update_row_id()
            cls._pending_detail_rows = []
    
    @classmethod
    def _create_single_detail_row(cls, config, asset_id, make_model_id):
        """Create a single detail table row based on configuration"""
        logger.debug(f"DEBUG: _create_single_detail_row called for {config.detail_table_type}")
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
                logger.debug(f"Warning: Unknown detail table type '{config.detail_table_type}'")
                return
            
            logger.debug(f"DEBUG: Detail table class path: {detail_table_class_path}")
            
            # Import the detail table class
            module_path, class_name = detail_table_class_path.rsplit('.', 1)
            module = __import__(module_path, fromlist=[class_name])
            detail_table_class = getattr(module, class_name)
            
            logger.debug(f"DEBUG: Detail table class: {detail_table_class}")
            
            # Create the detail table row
            if config.is_asset_detail:
                # Create asset-specific detail row - check for duplicates first
                logger.debug(f"DEBUG: Creating asset detail row for asset_id={asset_id}")
                existing_row = detail_table_class.query.filter_by(asset_id=asset_id).first()
                if existing_row:
                    logger.debug(f"DEBUG: Asset detail row already exists for asset {asset_id}, skipping")
                    return  # Already exists, don't create duplicate
                detail_row = detail_table_class(asset_id=asset_id)
            else:
                # Create model-specific detail row (check if it already exists)
                existing_row = detail_table_class.query.filter_by(make_model_id=make_model_id).first()
                if existing_row:
                    logger.debug(f"DEBUG: Model detail row already exists, skipping")
                    return  # Already exists, don't create duplicate
                logger.debug(f"DEBUG: Creating model detail row for make_model_id={make_model_id}")
                detail_row = detail_table_class(make_model_id=make_model_id)
            
            logger.debug(f"DEBUG: Created detail row: {detail_row}")
            
            # Add to session (don't commit - let the main transaction handle it)
            db.session.add(detail_row)
            logger.debug(f"DEBUG: Added detail row to session")
            
            # Store the detail row for later row_id update
            if not hasattr(cls, '_pending_detail_rows'):
                cls._pending_detail_rows = []
            cls._pending_detail_rows.append(detail_row)
            
        except Exception as e:
            logger.debug(f"Error creating detail row for {config.detail_table_type}: {e}")
            # Don't rollback here - let the main transaction handle it 
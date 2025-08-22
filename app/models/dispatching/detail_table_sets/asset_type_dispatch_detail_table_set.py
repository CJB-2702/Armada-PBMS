#!/usr/bin/env python3
"""
Asset Type Dispatch Detail Table Set
Configuration container that defines which dispatch detail table types are available for a specific asset type
"""

from app.models.core.user_created_base import UserCreatedBase
from app.logger import get_logger
logger = get_logger("asset_management.models.dispatching")
from app import db

class AssetTypeDispatchDetailTableSet(UserCreatedBase):
    """
    Configuration container that defines which dispatch detail table types 
    are available for a specific asset type
    """
    __tablename__ = 'asset_type_dispatch_detail_table_sets'
    
    # Configuration fields
    asset_type_id = db.Column(db.Integer, db.ForeignKey('asset_types.id'), nullable=False)
    dispatch_detail_table_type = db.Column(db.String(100), nullable=False)  # e.g., 'vehicle_dispatch', 'truck_checklist'
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    asset_type = db.relationship('AssetType', backref='dispatch_detail_table_sets')
    
    def __repr__(self):
        """String representation of the asset type dispatch detail table set"""
        return f'<AssetTypeDispatchDetailTableSet {self.asset_type.name}:{self.dispatch_detail_table_type}>'
    
    @classmethod
    def get_dispatch_detail_table_types_for_asset_type(cls, asset_type_id):
        """Get all dispatch detail table types configured for a specific asset type"""
        return cls.query.filter_by(
            asset_type_id=asset_type_id,
            is_active=True
        ).all()
    
    @classmethod
    def create_dispatch_detail_table_rows(cls, dispatch_id, asset_id):
        """Create dispatch detail table rows based on asset type configurations"""
        logger.debug(f"DEBUG: AssetTypeDispatchDetailTableSet.create_dispatch_detail_table_rows called for dispatch {dispatch_id}")
        try:
            # Get the asset to determine its asset type
            from app.models.core.asset import Asset
            asset = Asset.query.get(asset_id)
            if not asset or not asset.asset_type_id:
                logger.debug(f"DEBUG: Asset or asset type not found")
                return
            
            asset_type_id = asset.asset_type_id
            logger.debug(f"DEBUG: Asset type ID: {asset_type_id}")
            
            # Get all dispatch detail table configurations for this asset type
            detail_configs = cls.get_dispatch_detail_table_types_for_asset_type(asset_type_id)
            logger.debug(f"DEBUG: Found {len(detail_configs)} dispatch detail configurations")
            
            for config in detail_configs:
                logger.debug(f"DEBUG: Creating dispatch detail row for {config.dispatch_detail_table_type}")
                cls._create_single_dispatch_detail_row(config, dispatch_id)
                
        except Exception as e:
            logger.debug(f"Error creating asset type dispatch detail table rows for dispatch {dispatch_id}: {e}")
    
    @classmethod
    def _create_single_dispatch_detail_row(cls, config, dispatch_id):
        """Create a single dispatch detail table row based on configuration"""
        logger.debug(f"DEBUG: _create_single_dispatch_detail_row called for {config.dispatch_detail_table_type}")
        try:
            # Dispatch detail table registry mapping
            dispatch_detail_table_registry = {
                'vehicle_dispatch': 'app.models.dispatching.dispatch_details.vehicle_dispatch.VehicleDispatch',
                'truck_dispatch_checklist': 'app.models.dispatching.dispatch_details.truck_dispatch_checklist.TruckDispatchChecklist'
            }
            
            dispatch_detail_table_class_path = dispatch_detail_table_registry.get(config.dispatch_detail_table_type)
            if not dispatch_detail_table_class_path:
                logger.debug(f"Warning: Unknown dispatch detail table type '{config.dispatch_detail_table_type}'")
                return
            
            logger.debug(f"DEBUG: Dispatch detail table class path: {dispatch_detail_table_class_path}")
            
            # Import the dispatch detail table class
            module_path, class_name = dispatch_detail_table_class_path.rsplit('.', 1)
            module = __import__(module_path, fromlist=[class_name])
            dispatch_detail_table_class = getattr(module, class_name)
            
            logger.debug(f"DEBUG: Dispatch detail table class: {dispatch_detail_table_class}")
            
            # Create the dispatch detail table row - check for duplicates first
            logger.debug(f"DEBUG: Creating dispatch detail row for dispatch_id={dispatch_id}")
            existing_row = dispatch_detail_table_class.query.filter_by(dispatch_id=dispatch_id).first()
            if existing_row:
                logger.debug(f"DEBUG: Dispatch detail row already exists for dispatch {dispatch_id}, skipping")
                return  # Already exists, don't create duplicate
            
            dispatch_detail_row = dispatch_detail_table_class(dispatch_id=dispatch_id)
            logger.debug(f"DEBUG: Created dispatch detail row: {dispatch_detail_row}")
            
            # Add to session (don't commit - let the main transaction handle it)
            db.session.add(dispatch_detail_row)
            logger.debug(f"DEBUG: Added dispatch detail row to session")
            
        except Exception as e:
            logger.debug(f"Error creating dispatch detail row for {config.dispatch_detail_table_type}: {e}")
            # Don't rollback here - let the main transaction handle it

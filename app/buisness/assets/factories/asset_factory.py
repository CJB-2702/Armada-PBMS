#!/usr/bin/env python3
"""
Asset Factory
Factory class for creating Asset instances with proper detail table initialization
"""

from app.logger import get_logger
from app import db

logger = get_logger("asset_management.domain.assets.factories")

class AssetFactory:
    """
    Factory class for creating Asset instances
    Ensures proper creation with detail table initialization
    """
    
    @classmethod
    def create_asset(cls, created_by_id=None, commit=True, **kwargs):
        """
        Create a new Asset with proper initialization
        
        Args:
            created_by_id (int): ID of the user creating the asset
            commit (bool): Whether to commit the transaction (default: True)
            **kwargs: Asset fields (name, serial_number, make_model_id, etc.)
            
        Returns:
            Asset: The created asset instance
            
        Raises:
            ValueError: If required fields are missing or invalid
        """
        from app.data.core.asset_info.asset import Asset
        
        # Validate required fields
        if 'name' not in kwargs:
            raise ValueError("Asset name is required")
        if 'serial_number' not in kwargs:
            raise ValueError("Asset serial number is required")
        
        # Check for duplicate serial number
        existing_asset = Asset.query.filter_by(serial_number=kwargs['serial_number']).first()
        if existing_asset:
            raise ValueError(f"Asset with serial number '{kwargs['serial_number']}' already exists")
        
        # Set audit fields if provided
        if created_by_id:
            kwargs['created_by_id'] = created_by_id
            kwargs['updated_by_id'] = created_by_id
        
        # Create the asset instance
        asset = Asset(**kwargs)
        
        logger.info(f"Creating asset: {kwargs.get('name')} ({kwargs.get('serial_number')})")
        
        # Add to session
        db.session.add(asset)
        
        # Commit if requested
        if commit:
            db.session.commit()
            logger.info(f"Asset created successfully: {asset.name} (ID: {asset.id})")
        else:
            # Flush to get the ID but don't commit
            db.session.flush()
            logger.info(f"Asset added to session: {asset.name} (ID: {asset.id}, not committed)")
        
        # The after_insert event listener will automatically create detail table rows
        # This happens in Asset._after_insert() which calls asset.create_detail_table_rows()
        
        return asset
    
    @classmethod
    def create_asset_from_dict(cls, asset_data, created_by_id=None, commit=True, lookup_fields=None):
        """
        Create an asset from a dictionary, with optional find_or_create behavior
        
        Args:
            asset_data (dict): Asset data dictionary
            created_by_id (int): ID of the user creating the asset
            commit (bool): Whether to commit the transaction
            lookup_fields (list): Fields to use for find_or_create (e.g., ['serial_number'])
            
        Returns:
            tuple: (asset, created) where created is True if asset was created
        """
        from app.data.core.asset_info.asset import Asset
        
        # If lookup_fields provided, try to find existing asset
        if lookup_fields:
            query_filters = {field: asset_data.get(field) for field in lookup_fields if field in asset_data}
            existing_asset = Asset.query.filter_by(**query_filters).first()
            
            if existing_asset:
                logger.info(f"Found existing asset: {existing_asset.name} (ID: {existing_asset.id})")
                return existing_asset, False
        
        # Create new asset
        asset = cls.create_asset(created_by_id=created_by_id, commit=commit, **asset_data)
        return asset, True
    
    @classmethod
    def update_asset(cls, asset, updated_by_id=None, commit=True, **kwargs):
        """
        Update an existing asset
        
        Args:
            asset (Asset): The asset to update
            updated_by_id (int): ID of the user updating the asset
            commit (bool): Whether to commit the transaction
            **kwargs: Fields to update
            
        Returns:
            Asset: The updated asset instance
        """
        from app.data.core.asset_info.asset import Asset
        
        # Check for duplicate serial number if serial_number is being updated
        if 'serial_number' in kwargs and kwargs['serial_number'] != asset.serial_number:
            existing_asset = Asset.query.filter_by(serial_number=kwargs['serial_number']).first()
            if existing_asset and existing_asset.id != asset.id:
                raise ValueError(f"Asset with serial number '{kwargs['serial_number']}' already exists")
        
        # Update fields
        for key, value in kwargs.items():
            if hasattr(asset, key):
                setattr(asset, key, value)
        
        # Set updated_by_id if provided
        if updated_by_id:
            asset.updated_by_id = updated_by_id
        
        logger.info(f"Updating asset: {asset.name} (ID: {asset.id})")
        
        # Commit if requested
        if commit:
            db.session.commit()
            logger.info(f"Asset updated successfully: {asset.name} (ID: {asset.id})")
        else:
            logger.info(f"Asset updates staged: {asset.name} (ID: {asset.id}, not committed)")
        
        return asset


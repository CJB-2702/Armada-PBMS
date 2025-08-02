"""
Asset detail models build module for the Asset Management System
Handles building and initializing asset detail models and data
"""
from app.models.core.build import init_essential_data, init_data
from app import db
import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

def build_models():
    """
    Build asset detail models - this is a no-op since models are imported
    when the app is created, which registers them with SQLAlchemy
    """
    import app.models.assets.asset_details.purchase_info
    import app.models.assets.asset_details.vehicle_registration
    import app.models.assets.asset_details.toyota_warranty_receipt
    import app.models.assets.model_details.emissions_info
    import app.models.assets.model_details.model_info
    import app.models.assets.detail_table_sets.asset_type_detail_table_set
    import app.models.assets.detail_table_sets.model_detail_table_set
    logger.info("build_models: Asset Models Created")
    pass

def phase_2_init_data(build_data):
    """
    Initialize Phase 2 data (Asset Detail Tables)
    
    Args:
        build_data (dict): Build data from JSON file
    """
    logger.info("Phase 2 data initialization - Asset Detail Tables")
    
    # Initialize core data first
    init_data(build_data)
    
    # Get system user for audit fields
    from app.models.core.user import User
    system_user = User.query.filter_by(username='system').first()
    if not system_user:
        logger.error("System user not found, Core Data not initialized")
        raise Exception("System user not found, Core Data not initialized")

    system_user_id = system_user.id
    
    # Initialize detail table configurations
    _init_detail_table_configurations(build_data, system_user_id)
    
    # Get all assets
    from app.models.core.asset import Asset
    assets = Asset.query.all()
    
    if not assets:
        logger.warning("No assets found for phase 2 data insertion")
        return
    
    # Get the first asset for manual testing
    first_asset = assets[0]
    logger.info(f"Phase 2: Using first asset '{first_asset.name}' for manual detail table insertion")
    
    # Import all detail table models
    from app.models.assets.asset_details.purchase_info import PurchaseInfo
    from app.models.assets.asset_details.vehicle_registration import VehicleRegistration
    from app.models.assets.asset_details.toyota_warranty_receipt import ToyotaWarrantyReceipt
    from app.models.assets.model_details.emissions_info import EmissionsInfo
    from app.models.assets.model_details.model_info import ModelInfo
    
    # Detail table registry mapping
    detail_table_registry = {
        'purchase_info': PurchaseInfo,
        'vehicle_registration': VehicleRegistration,
        'toyota_warranty_receipt': ToyotaWarrantyReceipt,
        'emissions_info': EmissionsInfo,
        'model_info': ModelInfo
    }
    
    # Get sample data from build_data
    sample_data = build_data.get('sample_data', {})
    
    # Insert data for each detail table type
    for table_type, detail_class in detail_table_registry.items():
        if table_type in sample_data:
            logger.info(f"Phase 2: Inserting data for {table_type}")
            
            # Check if this is an asset detail or model detail
            if hasattr(detail_class, 'is_asset_detail') and detail_class.is_asset_detail():
                # Asset detail - create row for the first asset
                detail_data = sample_data[table_type].copy()
                detail_data['asset_id'] = first_asset.id
                detail_data['created_by_id'] = system_user_id
                
                # Convert date strings to date objects
                for key, value in detail_data.items():
                    if isinstance(value, str) and (key.endswith('_date') or key.endswith('_expiry')):
                        try:
                            detail_data[key] = datetime.strptime(value, '%Y-%m-%d').date()
                        except ValueError:
                            pass  # Keep as string if parsing fails
                
                # Create the detail row
                detail_row = detail_class(**detail_data)
                db.session.add(detail_row)
                logger.info(f"Phase 2: Created {table_type} row for asset {first_asset.name}")
                
            elif hasattr(detail_class, 'is_model_detail') and detail_class.is_model_detail():
                # Model detail - create row for the asset's make_model
                if first_asset.make_model_id:
                    detail_data = sample_data[table_type].copy()
                    detail_data['make_model_id'] = first_asset.make_model_id
                    detail_data['created_by_id'] = system_user_id
                    
                    # Convert date strings to date objects
                    for key, value in detail_data.items():
                        if isinstance(value, str) and (key.endswith('_date') or key.endswith('_expiry')):
                            try:
                                detail_data[key] = datetime.strptime(value, '%Y-%m-%d').date()
                            except ValueError:
                                pass  # Keep as string if parsing fails
                    
                    # Check if model detail already exists
                    existing_row = detail_class.query.filter_by(make_model_id=first_asset.make_model_id).first()
                    if not existing_row:
                        detail_row = detail_class(**detail_data)
                        db.session.add(detail_row)
                        logger.info(f"Phase 2: Created {table_type} row for model {first_asset.make_model.make} {first_asset.make_model.model}")
                    else:
                        logger.info(f"Phase 2: {table_type} row already exists for model {first_asset.make_model.make} {first_asset.make_model.model}")
    
    # Commit all changes
    try:
        db.session.commit()
        logger.info("Phase 2: Successfully committed all detail table data")
    except Exception as e:
        db.session.rollback()
        logger.error(f"Phase 2: Error committing detail table data: {e}")
        raise


def _update_autogenerated_detail_table_data(table_type, asset, sample_data, system_user_id):
    """
    Update detail table data for a specific table type and asset
    
    Args:
        table_type (str): The detail table type to update
        asset (Asset): The asset to update data for
        sample_data (dict): Sample data from build_data
        system_user_id (int): System user ID for audit fields
    """
    if table_type not in sample_data:
        return
    
    # Detail table registry mapping
    detail_table_registry = {
        'purchase_info': 'app.models.assets.asset_details.purchase_info.PurchaseInfo',
        'vehicle_registration': 'app.models.assets.asset_details.vehicle_registration.VehicleRegistration',
        'toyota_warranty_receipt': 'app.models.assets.asset_details.toyota_warranty_receipt.ToyotaWarrantyReceipt',
        'emissions_info': 'app.models.assets.model_details.emissions_info.EmissionsInfo',
        'model_info': 'app.models.assets.model_details.model_info.ModelInfo'
    }
    
    detail_table_class_path = detail_table_registry.get(table_type)
    if not detail_table_class_path:
        logger.warning(f"Unknown detail table type '{table_type}'")
        return
    
    # Import the detail table class
    module_path, class_name = detail_table_class_path.rsplit('.', 1)
    module = __import__(module_path, fromlist=[class_name])
    detail_table_class = getattr(module, class_name)
    
    # Check if this is an asset detail or model detail
    if hasattr(detail_table_class, 'is_asset_detail') and detail_table_class.is_asset_detail():
        # Asset detail - find existing row or create new one
        existing_row = detail_table_class.query.filter_by(asset_id=asset.id).first()
        if existing_row:
            # Update existing row
            detail_data = sample_data[table_type].copy()
            for key, value in detail_data.items():
                if hasattr(existing_row, key):
                    # Convert date strings to date objects
                    if isinstance(value, str) and (key.endswith('_date') or key.endswith('_expiry')):
                        try:
                            value = datetime.strptime(value, '%Y-%m-%d').date()
                        except ValueError:
                            pass  # Keep as string if parsing fails
                    setattr(existing_row, key, value)
            logger.info(f"Phase 3: Updated {table_type} for asset {asset.name}")
        else:
            # Create new row
            detail_data = sample_data[table_type].copy()
            detail_data['asset_id'] = asset.id
            detail_data['created_by_id'] = system_user_id
            
            # Convert date strings to date objects
            for key, value in detail_data.items():
                if isinstance(value, str) and (key.endswith('_date') or key.endswith('_expiry')):
                    try:
                        detail_data[key] = datetime.strptime(value, '%Y-%m-%d').date()
                    except ValueError:
                        pass  # Keep as string if parsing fails
            
            detail_row = detail_table_class(**detail_data)
            db.session.add(detail_row)
            logger.info(f"Phase 3: Created {table_type} for asset {asset.name}")
            
    elif hasattr(detail_table_class, 'is_model_detail') and detail_table_class.is_model_detail():
        # Model detail - find existing row or create new one
        if asset.make_model_id:
            existing_row = detail_table_class.query.filter_by(make_model_id=asset.make_model_id).first()
            if existing_row:
                # Update existing row
                detail_data = sample_data[table_type].copy()
                for key, value in detail_data.items():
                    if hasattr(existing_row, key):
                        # Convert date strings to date objects
                        if isinstance(value, str) and (key.endswith('_date') or key.endswith('_expiry')):
                            try:
                                value = datetime.strptime(value, '%Y-%m-%d').date()
                            except ValueError:
                                pass  # Keep as string if parsing fails
                        setattr(existing_row, key, value)
                logger.info(f"Phase 3: Updated {table_type} for model {asset.make_model.make} {asset.make_model.model}")
            else:
                # Create new rowwarning
                detail_data = sample_data[table_type].copy()
                detail_data['make_model_id'] = asset.make_model_id
                detail_data['created_by_id'] = system_user_id
                
                # Convert date strings to date objects
                for key, value in detail_data.items():
                    if isinstance(value, str) and (key.endswith('_date') or key.endswith('_expiry')):
                        try:
                            detail_data[key] = datetime.strptime(value, '%Y-%m-%d').date()
                        except ValueError:
                            pass  # Keep as string if parsing fails
                
                detail_row = detail_table_class(**detail_data)
                db.session.add(detail_row)
                logger.info(f"Phase 3: Created {table_type} for model {asset.make_model.make} {asset.make_model.model}")

def _init_detail_table_configurations(build_data, system_user_id):
    """
    Initialize detail table configurations from build_data
    
    Args:
        build_data (dict): Build data from JSON file
        system_user_id (int): System user ID for audit fields
    """
    logger.info("Initializing detail table configurations...")
    
    # Import required models
    from app.models.assets.detail_table_sets.asset_type_detail_table_set import AssetTypeDetailTableSet
    from app.models.assets.detail_table_sets.model_detail_table_set import ModelDetailTableSet
    from app.models.core.asset_type import AssetType
    from app.models.core.make_model import MakeModel
    
    # Initialize asset type detail table configurations
    if 'detail_table_configurations' in build_data and 'asset_type_configs' in build_data['detail_table_configurations']:
        logger.info("Creating asset type detail table configurations...")
        for config_data in build_data['detail_table_configurations']['asset_type_configs']:
            # Get asset type
            asset_type = AssetType.query.filter_by(name=config_data['asset_type_name']).first()
            if asset_type:
                # Check if configuration already exists
                existing_config = AssetTypeDetailTableSet.query.filter_by(
                    asset_type_id=asset_type.id,
                    detail_table_type=config_data['detail_table_type']
                ).first()
                
                if not existing_config:
                    config = AssetTypeDetailTableSet(
                        asset_type_id=asset_type.id,
                        detail_table_type=config_data['detail_table_type'],
                        is_asset_detail=config_data['is_asset_detail'],
                        is_active=config_data['is_active'],
                        created_by_id=system_user_id
                    )
                    db.session.add(config)
                    logger.info(f"Created asset type config: {asset_type.name} -> {config_data['detail_table_type']}")
                else:
                    logger.info(f"Asset type config already exists: {asset_type.name} -> {config_data['detail_table_type']}")
            else:
                logger.warning(f"Asset type '{config_data['asset_type_name']}' not found for detail table configuration")
    
    # Initialize model detail table configurations
    if 'detail_table_configurations' in build_data and 'model_configs' in build_data['detail_table_configurations']:
        logger.info("Creating model detail table configurations...")
        for config_data in build_data['detail_table_configurations']['model_configs']:
            # Get make/model
            make_model = MakeModel.query.filter_by(
                make=config_data['make'],
                model=config_data['model']
            ).first()
            
            if make_model:
                # Check if configuration already exists
                existing_config = ModelDetailTableSet.query.filter_by(
                    make_model_id=make_model.id,
                    detail_table_type=config_data['detail_table_type']
                ).first()
                
                if not existing_config:
                    config = ModelDetailTableSet(
                        make_model_id=make_model.id,
                        detail_table_type=config_data['detail_table_type'],
                        is_asset_detail=config_data['is_asset_detail'],
                        is_active=config_data['is_active'],
                        created_by_id=system_user_id
                    )
                    db.session.add(config)
                    logger.info(f"Created model config: {make_model.make} {make_model.model} -> {config_data['detail_table_type']}")
                else:
                    logger.info(f"Model config already exists: {make_model.make} {make_model.model} -> {config_data['detail_table_type']}")
            else:
                logger.warning(f"Make/Model '{config_data['make']} {config_data['model']}' not found for detail table configuration")
    
    # Commit configurations
    try:
        db.session.commit()
        logger.info("Successfully committed detail table configurations")
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error committing detail table configurations: {e}")
        raise 



def phase3_insert_data(build_data):
    """
    Insert Phase 3 data (Assets with automatic detail insertion)
    
    Args:
        build_data (dict): Build data from JSON file
    """
    # Get system user for audit fields
    from app.models.core.user import User
    system_user = User.query.filter_by(username='system').first()
    if not system_user:
        logger.warning("System user not found, Core Data not initialized")
        raise Exception("System user not found, Core Data not initialized")

    system_user_id = system_user.id
    
    _init_detail_table_configurations(build_data, system_user_id)
    logger.info("Phase 3 data insertion completed")

def phase3_update_data(build_data):
    """
    Update Phase 3 data (Assets with automatic detail insertion)
    
    Args:
        build_data (dict): Build data from JSON file
    """
    # Get system user for audit fields
    from app.models.core.user import User
    from app.models.core.asset import Asset
    
    system_user = User.query.filter_by(username='system').first()
    if not system_user:
        logger.warning("System user not found, Core Data not initialized")
        raise Exception("System user not found, Core Data not initialized")

    system_user_id = system_user.id

    assets = Asset.query.all()
    
    # Get sample data from build_data
    sample_data = build_data.get('sample_data', {})

    for asset in assets:
        # Update each detail table type for this asset
        for table_type in sample_data.keys():
            _update_autogenerated_detail_table_data(table_type, asset, sample_data, system_user_id)

    # Commit all changes
    try:
        db.session.commit()
        logger.info("Phase 3: Successfully committed all detail table updates")
    except Exception as e:
        db.session.rollback()
        logger.error(f"Phase 3: Error committing detail table updates: {e}")
        raise

    logger.info("Phase 3 data update completed")
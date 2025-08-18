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

# Centralized detail table registry
DETAIL_TABLE_REGISTRY = {
    'purchase_info': {
        'is_asset_detail': True,
        'module_path': 'app.models.assets.asset_details.purchase_info',
        'class_name': 'PurchaseInfo'
    },
    'vehicle_registration': {
        'is_asset_detail': True,
        'module_path': 'app.models.assets.asset_details.vehicle_registration',
        'class_name': 'VehicleRegistration'
    },
    'toyota_warranty_receipt': {
        'is_asset_detail': True,
        'module_path': 'app.models.assets.asset_details.toyota_warranty_receipt',
        'class_name': 'ToyotaWarrantyReceipt'
    },
    'emissions_info': {
        'is_asset_detail': False,
        'module_path': 'app.models.assets.model_details.emissions_info',
        'class_name': 'EmissionsInfo'
    },
    'model_info': {
        'is_asset_detail': False,
        'module_path': 'app.models.assets.model_details.model_info',
        'class_name': 'ModelInfo'
    }
}

def build_models():
    """
    Build asset detail models - this is a no-op since models are imported
    when the app is created, which registers them with SQLAlchemy
    """
    # Import master detail tables
    import app.models.assets.all_details
    
    # Import virtual base classes
    import app.models.assets.asset_detail_virtual
    import app.models.assets.model_detail_virtual
    
    # Import asset detail models
    import app.models.assets.asset_details.purchase_info
    import app.models.assets.asset_details.vehicle_registration
    import app.models.assets.asset_details.toyota_warranty_receipt
    
    # Import model detail models
    import app.models.assets.model_details.emissions_info
    import app.models.assets.model_details.model_info
    
    # Import detail table sets
    import app.models.assets.detail_table_sets.asset_type_detail_table_set
    import app.models.assets.detail_table_sets.model_detail_table_set
    
    # Automatic detail insertion is now enabled by default when Asset class is loaded
    from app.models.core.asset import Asset
    Asset.enable_automatic_detail_insertion()
    # Create all tables to ensure they exist
    db.create_all()
    
    logger.info("build_models: Asset Models Created")
    pass

def get_detail_table_class(table_type):
    """
    Get the detail table class for a given table type
    
    Args:
        table_type (str): The detail table type (e.g., 'purchase_info')
        
    Returns:
        class: The detail table class
    """
    if table_type not in DETAIL_TABLE_REGISTRY:
        raise ValueError(f"Unknown detail table type: {table_type}")
    
    registry_entry = DETAIL_TABLE_REGISTRY[table_type]
    module_path = registry_entry['module_path']
    class_name = registry_entry['class_name']
    
    # Import the module and get the class
    module = __import__(module_path, fromlist=[class_name])
    return getattr(module, class_name)

def is_asset_detail(table_type):
    """
    Check if a detail table type is an asset detail
    
    Args:
        table_type (str): The detail table type
        
    Returns:
        bool: True if it's an asset detail, False if it's a model detail
    """
    if table_type not in DETAIL_TABLE_REGISTRY:
        raise ValueError(f"Unknown detail table type: {table_type}")
    
    return DETAIL_TABLE_REGISTRY[table_type]['is_asset_detail']

def convert_date_strings(data):
    """
    Convert date strings in data to date objects
    
    Args:
        data (dict): Data dictionary that may contain date strings
        
    Returns:
        dict: Data with date strings converted to date objects
    """
    converted_data = data.copy()
    for key, value in converted_data.items():
        if isinstance(value, str) and (key.endswith('_date') or key.endswith('_expiry')):
            try:
                converted_data[key] = datetime.strptime(value, '%Y-%m-%d').date()
            except ValueError:
                pass  # Keep as string if parsing fails
    return converted_data

def phase_2_init_data(build_data):
    """
    Initialize Phase 2 data (Asset Detail Tables) using new structured format
    
    Args:
        build_data (dict): Build data from JSON file with new structure
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
    
    # Get the first asset for testing
    first_asset = assets[0]
    logger.info(f"Phase 2: Using first asset '{first_asset.name}' for detail table insertion")
    
    # Get sample data from Asset_Details section
    sample_data = build_data.get('Asset_Details', {}).get('Sample_Data', {})
    
    # Create detail table records using the automatic insertion system
    for table_type, detail_data in sample_data.items():
        # Convert table type from PascalCase to snake_case for lookup
        table_type_snake = ''.join(['_'+c.lower() if c.isupper() else c for c in table_type]).lstrip('_')
        
        if table_type_snake in DETAIL_TABLE_REGISTRY:
            logger.info(f"Phase 2: Creating {table_type_snake} record")
            
            try:
                # Get the detail table class
                detail_class = get_detail_table_class(table_type_snake)
                
                # Convert date strings to date objects
                converted_data = convert_date_strings(detail_data)
                
                if is_asset_detail(table_type_snake):
                    # Asset detail - create for the first asset
                    converted_data['asset_id'] = first_asset.id
                    converted_data['created_by_id'] = system_user_id
                    
                    # Check if record already exists
                    existing_row = detail_class.query.filter_by(asset_id=first_asset.id).first()
                    if not existing_row:
                        detail_row = detail_class(**converted_data)
                        db.session.add(detail_row)
                        logger.info(f"Phase 2: Created {table_type_snake} for asset {first_asset.name}")
                    else:
                        logger.info(f"Phase 2: {table_type_snake} already exists for asset {first_asset.name}")
                        
                else:
                    # Model detail - create for the asset's make_model
                    if first_asset.make_model_id:
                        converted_data['make_model_id'] = first_asset.make_model_id
                        converted_data['created_by_id'] = system_user_id
                        
                        # Check if record already exists
                        existing_row = detail_class.query.filter_by(make_model_id=first_asset.make_model_id).first()
                        if not existing_row:
                            detail_row = detail_class(**converted_data)
                            db.session.add(detail_row)
                            logger.info(f"Phase 2: Created {table_type_snake} for model {first_asset.make_model.make} {first_asset.make_model.model}")
                        else:
                            logger.info(f"Phase 2: {table_type_snake} already exists for model {first_asset.make_model.make} {first_asset.make_model.model}")
                            
            except Exception as e:
                logger.error(f"Phase 2: Error creating {table_type_snake}: {e}")
                continue
    
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
    if table_type not in sample_data or table_type not in DETAIL_TABLE_REGISTRY:
        return
    
    try:
        # Get the detail table class using centralized registry
        detail_table_class = get_detail_table_class(table_type)
        
        # Convert date strings to date objects
        detail_data = convert_date_strings(sample_data[table_type])
        
        if is_asset_detail(table_type):
            # Asset detail - find existing row or create new one
            existing_row = detail_table_class.query.filter_by(asset_id=asset.id).first()
            if existing_row:
                # Update existing row
                for key, value in detail_data.items():
                    if hasattr(existing_row, key):
                        setattr(existing_row, key, value)
                logger.info(f"Phase 3: Updated {table_type} for asset {asset.name}")
            else:
                # Create new row
                detail_data['asset_id'] = asset.id
                detail_data['created_by_id'] = system_user_id
                
                detail_row = detail_table_class(**detail_data)
                db.session.add(detail_row)
                logger.info(f"Phase 3: Created {table_type} for asset {asset.name}")
                
        else:
            # Model detail - find existing row or create new one
            if asset.make_model_id:
                existing_row = detail_table_class.query.filter_by(make_model_id=asset.make_model_id).first()
                if existing_row:
                    # Update existing row
                    for key, value in detail_data.items():
                        if hasattr(existing_row, key):
                            setattr(existing_row, key, value)
                    logger.info(f"Phase 3: Updated {table_type} for model {asset.make_model.make} {asset.make_model.model}")
                else:
                    # Create new row
                    detail_data['make_model_id'] = asset.make_model_id
                    detail_data['created_by_id'] = system_user_id
                    
                    detail_row = detail_table_class(**detail_data)
                    db.session.add(detail_row)
                    logger.info(f"Phase 3: Created {table_type} for model {asset.make_model.make} {asset.make_model.model}")
                    
    except Exception as e:
        logger.error(f"Phase 3: Error updating {table_type} for asset {asset.name}: {e}")

def _init_detail_table_configurations(build_data, system_user_id):
    """
    Initialize detail table configurations from build_data using new structured format
    
    Args:
        build_data (dict): Build data from JSON file with new structure
        system_user_id (int): ID of the system user for audit fields
    """
    # Import detail table sets
    from app.models.assets.detail_table_sets.asset_type_detail_table_set import AssetTypeDetailTableSet
    from app.models.assets.detail_table_sets.model_detail_table_set import ModelDetailTableSet
    from app.models.core.asset_type import AssetType
    from app.models.core.make_model import MakeModel
    
    logger.info("Initializing detail table configurations...")
    
    # Get configurations from Asset_Details section
    if 'Asset_Details' not in build_data or 'Detail_Table_Configurations' not in build_data['Asset_Details']:
        logger.warning("No detail table configurations found in build_data")
        return
    
    configs = build_data['Asset_Details']['Detail_Table_Configurations']
    
    # Create asset type detail table configurations
    if 'Asset_Type_Configs' in configs:
        logger.info("Creating asset type detail table configurations...")
        for config_data in configs['Asset_Type_Configs']:
            # Get asset type by name
            asset_type_name = config_data.get('asset_type_name')
            asset_type = AssetType.query.filter_by(name=asset_type_name).first()
            
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
                logger.warning(f"Asset type '{asset_type_name}' not found for detail table configuration")
    
    # Create model detail table configurations
    if 'Model_Configs' in configs:
        logger.info("Creating model detail table configurations...")
        for config_data in configs['Model_Configs']:
            # Get make/model by make and model
            make = config_data.get('make')
            model = config_data.get('model')
            make_model = MakeModel.query.filter_by(make=make, model=model).first()
            
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
                logger.warning(f"Make/Model '{make} {model}' not found for detail table configuration")
    
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
    Update Phase 3 data (Assets with automatic detail insertion) using new structured format
    
    Args:
        build_data (dict): Build data from JSON file with new structure
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
    
    # Get sample data from Asset_Details section
    sample_data = build_data.get('Asset_Details', {}).get('Sample_Data', {})

    for asset in assets:
        # Update each detail table type for this asset
        for table_type in sample_data.keys():
            # Convert table type from PascalCase to snake_case for lookup
            table_type_snake = ''.join(['_'+c.lower() if c.isupper() else c for c in table_type]).lstrip('_')
            _update_autogenerated_detail_table_data(table_type_snake, asset, sample_data, system_user_id)

    # Commit all changes
    try:
        db.session.commit()
        logger.info("Phase 3: Successfully committed all detail table updates")
    except Exception as e:
        db.session.rollback()
        logger.error(f"Phase 3: Error committing detail table updates: {e}")
        raise

    logger.info("Phase 3 data update completed")
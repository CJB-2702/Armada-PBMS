"""
Asset detail models build module for the Asset Management System
Handles building and initializing asset detail models and data
"""
from app.models.core.build import init_essential_data, init_data
from app import db
from app.logger import get_logger
from datetime import datetime
from pathlib import Path

logger = get_logger("asset_management.models.assets")

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
    
    # Import detail table templates
    import app.models.assets.detail_table_templates.asset_details_from_asset_type
    import app.models.assets.detail_table_templates.asset_details_from_model_type
    import app.models.assets.detail_table_templates.model_detail_table_template
    
    # Initialize ID sequences
    from app.models.assets.detail_id_managers import AssetDetailIDManager, ModelDetailIDManager
    AssetDetailIDManager.create_sequence_if_not_exists()
    ModelDetailIDManager.create_sequence_if_not_exists()
    
    # Automatic detail insertion is now enabled by default when Asset class is loaded
    from app.models.core.asset import Asset
    Asset.enable_automatic_detail_insertion()
    
    # Enable automatic detail insertion for models
    from app.models.core.make_model import MakeModel
    MakeModel.enable_automatic_detail_insertion()
    
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

    # Insert models for automatic detail insertion
    _insert_models_for_automatic_detail_insertion(build_data, system_user_id)
    
    # Insert assets for automatic detail insertion
    _insert_assets_for_automatic_detail_insertion(build_data, system_user_id)


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
    # Import detail table templates
    from app.models.assets.detail_table_templates.asset_details_from_asset_type import AssetDetailTemplateByAssetType
    from app.models.assets.detail_table_templates.asset_details_from_model_type import AssetDetailTemplateByModelType
    from app.models.assets.detail_table_templates.model_detail_table_template import ModelDetailTableTemplate
    from app.models.core.asset_type import AssetType
    from app.models.core.make_model import MakeModel
    
    logger.info("Initializing detail table configurations...")
    
    # Get configurations from Asset_Details section
    if 'Asset_Details' not in build_data or 'Detail_Table_Templates' not in build_data['Asset_Details']:
        logger.warning("No detail table configurations found in build_data")
        return
    
    templates = build_data['Asset_Details']['Detail_Table_Templates']
    
    # Create asset type detail table configurations
    if 'Asset_details_from_asset_type' in templates:
        logger.info("Creating asset type detail table configurations...")
        for config_data in templates['Asset_details_from_asset_type']:
            # Get asset type by name
            asset_type_name = config_data.get('asset_type_name')
            asset_type = AssetType.query.filter_by(name=asset_type_name).first()
            
            if asset_type:
                # Check if configuration already exists
                existing_config = AssetDetailTemplateByAssetType.query.filter_by(
                    asset_type_id=asset_type.id,
                    detail_table_type=config_data['detail_table_type']
                ).first()
                
                if not existing_config:
                    config = AssetDetailTemplateByAssetType(
                        asset_type_id=asset_type.id,
                        detail_table_type=config_data['detail_table_type'],
                        created_by_id=system_user_id
                    )
                    db.session.add(config)
                    logger.info(f"Created asset type config: {asset_type.name} -> {config_data['detail_table_type']}")
                else:
                    logger.info(f"Asset type config already exists: {asset_type.name} -> {config_data['detail_table_type']}")
            else:
                logger.warning(f"Asset type '{asset_type_name}' not found for detail table configuration")
    
    # Create asset detail configurations from model type
    if 'Asset_details_from_model_type' in templates:
        logger.info("Creating asset detail configurations from model type...")
        for config_data in templates['Asset_details_from_model_type']:
            # Get make/model by make and model
            make = config_data.get('make')
            model = config_data.get('model')
            make_model = MakeModel.query.filter_by(make=make, model=model).first()
            
            if make_model:
                # Check if configuration already exists
                existing_config = AssetDetailTemplateByModelType.query.filter_by(
                    make_model_id=make_model.id,
                    detail_table_type=config_data['detail_table_type']
                ).first()
                
                if not existing_config:
                    config = AssetDetailTemplateByModelType(
                        make_model_id=make_model.id,
                        detail_table_type=config_data['detail_table_type'],
                        created_by_id=system_user_id
                    )
                    db.session.add(config)
                    logger.info(f"Created model type config: {make_model.make} {make_model.model} -> {config_data['detail_table_type']}")
                else:
                    logger.info(f"Model type config already exists: {make_model.make} {make_model.model} -> {config_data['detail_table_type']}")
            else:
                logger.warning(f"Make/Model '{make} {model}' not found for detail table configuration")
    
    # Create model detail table configurations
    if 'Model_detail_table_template' in templates:
        logger.info("Creating model detail table configurations...")
        for config_data in templates['Model_detail_table_template']:
            # Get asset type by name (can be null for global configs)
            asset_type_name = config_data.get('asset_type_name')
            asset_type_id = None
            if asset_type_name:
                asset_type = AssetType.query.filter_by(name=asset_type_name).first()
                if asset_type:
                    asset_type_id = asset_type.id
                else:
                    logger.warning(f"Asset type '{asset_type_name}' not found for model detail table configuration")
                    continue
            
            # Check if configuration already exists
            existing_config = ModelDetailTableTemplate.query.filter_by(
                asset_type_id=asset_type_id,
                detail_table_type=config_data['detail_table_type']
            ).first()
            
            if not existing_config:
                config = ModelDetailTableTemplate(
                    asset_type_id=asset_type_id,
                    detail_table_type=config_data['detail_table_type'],
                    created_by_id=system_user_id
                )
                db.session.add(config)
                logger.info(f"Created model detail config: {asset_type_name or 'Global'} -> {config_data['detail_table_type']}")
            else:
                logger.info(f"Model detail config already exists: {asset_type_name or 'Global'} -> {config_data['detail_table_type']}")
    
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


def _insert_models_for_automatic_detail_insertion(build_data, system_user_id):
    """
    Insert models for automatic detail insertion after templates are configured
    
    Args:
        build_data (dict): Build data from JSON file
        system_user_id (int): System user ID for audit fields
    """
    logger.info("Phase 2: Inserting models for automatic detail insertion")
    
    from app.models.core.make_model import MakeModel
    from app.models.core.asset_type import AssetType
    
    # Get models for automatic detail insertion from Asset_Details section
    models_data = build_data.get('Asset_Details', {}).get('Models_for_automatic_detail_insertion', [])
    
    if not models_data:
        logger.info("Phase 2: No models found for automatic detail insertion")
        return
    
    for model_data in models_data:
        try:
            # Check if model already exists
            existing_model = MakeModel.query.filter_by(
                make=model_data['make'],
                model=model_data['model'],
                year=model_data.get('year')
            ).first()
            
            if existing_model:
                logger.info(f"Phase 2: Model '{model_data['make']} {model_data['model']}' already exists, skipping")
                continue
            
            # Set default asset type to Vehicle if not specified
            if 'asset_type_name' not in model_data:
                asset_type = AssetType.query.filter_by(name='Vehicle').first()
                if asset_type:
                    model_data['asset_type_id'] = asset_type.id
                else:
                    logger.warning(f"Phase 2: Vehicle asset type not found for model {model_data['make']} {model_data['model']}")
                    continue
            
            # Create the model
            model = MakeModel(**model_data)
            model.created_by_id = system_user_id
            db.session.add(model)
            logger.info(f"Phase 2: Created model '{model_data['make']} {model_data['model']}' for automatic detail insertion")
            
        except Exception as e:
            logger.error(f"Phase 2: Error creating model {model_data.get('make', 'Unknown')} {model_data.get('model', 'Unknown')}: {e}")
            continue
    
    # Commit all model creations
    try:
        db.session.commit()
        logger.info("Phase 2: Successfully committed all models for automatic detail insertion")
    except Exception as e:
        db.session.rollback()
        logger.error(f"Phase 2: Error committing models for automatic detail insertion: {e}")
        raise


def _insert_assets_for_automatic_detail_insertion(build_data, system_user_id):
    """
    Insert assets for automatic detail insertion after templates are configured
    
    Args:
        build_data (dict): Build data from JSON file
        system_user_id (int): System user ID for audit fields
    """
    logger.info("Phase 2: Inserting assets for automatic detail insertion")
    
    from app.models.core.asset import Asset
    from app.models.core.major_location import MajorLocation
    from app.models.core.make_model import MakeModel
    
    # Get assets for automatic detail insertion from Asset_Details section
    assets_data = build_data.get('Asset_Details', {}).get('Assets_for_automatic_detail_insertion', [])
    
    if not assets_data:
        logger.info("Phase 2: No assets found for automatic detail insertion")
        return
    
    for asset_data in assets_data:
        try:
            # Handle major_location_name reference
            if 'major_location_name' in asset_data:
                major_location_name = asset_data.pop('major_location_name')
                major_location = MajorLocation.query.filter_by(name=major_location_name).first()
                if major_location:
                    asset_data['major_location_id'] = major_location.id
                else:
                    logger.warning(f"Phase 2: Major location '{major_location_name}' not found for asset {asset_data.get('name', 'Unknown')}")
                    continue
            
            # Handle make/model reference to assign make_model_id
            if 'make' in asset_data and 'model' in asset_data:
                make = asset_data.pop('make')
                model = asset_data.pop('model')
                year = asset_data.pop('year', None) if 'year' in asset_data else None
                
                # Find the make/model
                make_model_query = MakeModel.query.filter_by(make=make, model=model)
                if year is not None:
                    make_model_query = make_model_query.filter_by(year=year)
                
                make_model = make_model_query.first()
                if make_model:
                    asset_data['make_model_id'] = make_model.id
                    logger.info(f"Phase 2: Assigned asset {asset_data.get('name', 'Unknown')} to make/model: {make} {model}")
                else:
                    logger.warning(f"Phase 2: Make/model '{make} {model}' not found for asset {asset_data.get('name', 'Unknown')}")
                    continue
            
            # Check if asset already exists
            existing_asset = Asset.query.filter_by(name=asset_data['name']).first()
            if existing_asset:
                logger.info(f"Phase 2: Asset '{asset_data['name']}' already exists, skipping")
                continue
            
            # Create the asset
            asset = Asset(**asset_data)
            asset.created_by_id = system_user_id
            db.session.add(asset)
            logger.info(f"Phase 2: Created asset '{asset_data['name']}' for automatic detail insertion")
            
            # Create detail table rows for this asset after it's committed
            db.session.flush()  # Ensure the asset has an ID
            asset.create_detail_table_rows()
            
        except Exception as e:
            logger.error(f"Phase 2: Error creating asset {asset_data.get('name', 'Unknown')}: {e}")
            continue
    
    # Commit all asset creations
    try:
        db.session.commit()
        logger.info("Phase 2: Successfully committed all assets for automatic detail insertion")
    except Exception as e:
        db.session.rollback()
        logger.error(f"Phase 2: Error committing assets for automatic detail insertion: {e}")
        raise



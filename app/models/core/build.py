"""
Core models build module for the Asset Management System
Handles building and initializing core foundation models and data
"""

from app import db
import logging

logger = logging.getLogger(__name__)

def build_models():
    """
    Build core models - this is a no-op since models are imported
    when the app is created, which registers them with SQLAlchemy
    """
    import app.models.core.user
    import app.models.core.major_location
    import app.models.core.asset_type
    import app.models.core.make_model
    import app.models.core.asset
    import app.models.core.event
    import app.models.core.attachment
    import app.models.core.comment
    import app.models.core.comment_attachment
    
    logger.info("Core models build completed")
    pass


def create_system_initialization_event(system_user_id=None, force_create=False):
    """
    Create system initialization event only if it's the first time or if forced
    
    Args:
        system_user_id (int, optional): System user ID for audit fields
        force_create (bool): Force creation even if event exists (for system failures)
    """
    from app.models.core.event import Event
    
    # Check if system initialization event already exists
    existing_event = Event.query.filter_by(
        event_type='System',
        description='System initialized with core data'
    ).first()
    
    if existing_event and not force_create:
        logger.info("System initialization event already exists, skipping creation")
        return existing_event
    
    # Create system initialization event
    event_data = {
        'event_type': 'System',
        'description': 'System initialized with core data'
    }
    
    event = Event.find_or_create_from_dict(
        event_data,
        user_id=system_user_id,
        lookup_fields=['event_type', 'description']
    )
    
    if event[1]:  # If newly created
        logger.info("Created system initialization event")
    else:
        logger.info("System initialization event already existed")
    
    return event[0]


def create_system_failure_event(system_user_id=None, error_message=None):
    """
    Create system failure event to indicate system initialization problems
    
    Args:
        system_user_id (int, optional): System user ID for audit fields
        error_message (str, optional): Error message to include in description
    """
    from app.models.core.event import Event
    
    description = 'System initialization failed'
    if error_message:
        description += f': {error_message}'
    
    # Create system failure event
    event_data = {
        'event_type': 'System',
        'description': description
    }
    
    event = Event.find_or_create_from_dict(
        event_data,
        user_id=system_user_id,
        lookup_fields=['event_type', 'description']
    )
    
    if event[1]:  # If newly created
        logger.warning(f"Created system failure event: {description}")
    else:
        logger.warning(f"System failure event already existed: {description}")
    
    return event[0]


def init_essential_data(build_data):
    """
    Initialize essential data from build_data
    """
    """
    Initialize core data from build_data
    
    Args:
        build_data (dict): Build data from JSON file
    """
    from app.models.core.user import User
    from app.models.core.major_location import MajorLocation
    from app.models.core.asset_type import AssetType
    from app.models.core.make_model import MakeModel

    
    # Get system user for audit fields
    system_user = User.query.filter_by(username='system').first()
    if not system_user:
        logger.warning("System user not found, creating users without audit trail")
        system_user_id = None
    else:
        system_user_id = system_user.id
    
    logger.info("Initializing core data...")
    
    # Create users
    if 'core_users' in build_data:
        logger.info("Creating users...")
        for user_data in build_data['core_users']:
            User.find_or_create_from_dict(
                user_data, 
                user_id=system_user_id,
                lookup_fields=['username']
            )
    
    # Create locations
    if 'core_locations' in build_data:
        logger.info("Creating locations...")
        for location_data in build_data['core_locations']:
            MajorLocation.find_or_create_from_dict(
                location_data,
                user_id=system_user_id,
                lookup_fields=['name']
            )
    
    # Create asset types
    if 'core_asset_types' in build_data:
        logger.info("Creating asset types...")
        for asset_type_data in build_data['core_asset_types']:
            AssetType.find_or_create_from_dict(
                asset_type_data,
                user_id=system_user_id,
                lookup_fields=['name']
            )
    
    # Create make/models
    if 'core_make_models' in build_data:
        logger.info("Creating make/models...")
        for make_model_data in build_data['core_make_models']:
            # Handle asset_type_name reference
            if 'asset_type_name' in make_model_data:
                asset_type_name = make_model_data.pop('asset_type_name')
                asset_type = AssetType.query.filter_by(name=asset_type_name).first()
                if asset_type:
                    make_model_data['asset_type_id'] = asset_type.id
            
            MakeModel.find_or_create_from_dict(
                make_model_data,
                user_id=system_user_id,
                lookup_fields=['make', 'model', 'year']
            )
    

def init_assets(build_data):
    from app.models.core.event import Event
    from app.models.core.asset import Asset
    from app.models.core.user import User
    from app.models.core.major_location import MajorLocation
    from app.models.core.make_model import MakeModel

    # Get system user for audit fields
    system_user = User.query.filter_by(username='system').first()
    if not system_user:
        logger.warning("System user not found, essential data not created")
        system_user_id = None
    else:
        system_user_id = system_user.id

    if 'core_assets' in build_data:
        logger.info("Creating assets...")
        for asset_data in build_data['core_assets']:
            # Handle major_location_name reference
            if 'major_location_name' in asset_data:
                major_location_name = asset_data.pop('major_location_name')
                major_location = MajorLocation.query.filter_by(name=major_location_name).first()
                if major_location:
                    asset_data['major_location_id'] = major_location.id
                else:
                    logger.warning(f"Major location '{major_location_name}' not found for asset {asset_data.get('name', 'Unknown')}")
            
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
                    logger.info(f"Assigned asset {asset_data.get('name', 'Unknown')} to make/model: {make} {model}")
                else:
                    logger.warning(f"Make/model '{make} {model}' not found for asset {asset_data.get('name', 'Unknown')}")
            
            Asset.find_or_create_from_dict(
                asset_data,
                user_id=system_user_id,
                lookup_fields=['name']
            )
    
    # Handle system initialization event specially
    if 'core_events' in build_data:
        logger.info("Processing system events...")
        for event_data in build_data['core_events']:
            # Check if this is a system initialization event
            if (event_data.get('event_type') == 'System' and 
                event_data.get('description') == 'System initialized with core data'):
                # Use special handling for system initialization
                create_system_initialization_event(system_user_id)
            else:
                # Handle other events normally
                Event.find_or_create_from_dict(
                    event_data,
                    user_id=system_user_id,
                    lookup_fields=['event_type', 'description']
                )

def init_data(build_data): 
    init_essential_data(build_data)
    init_assets(build_data)
    
logger.info("Core data initialization completed") 
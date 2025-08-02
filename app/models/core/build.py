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
    
    logger.info("Core models build completed")
    pass


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
            Asset.find_or_create_from_dict(
                asset_data,
                user_id=system_user_id,
                lookup_fields=['name']
            )
    
    if 'core_events' in build_data:
        logger.info("Creating events...")
        for event_data in build_data['core_events']:
            Event.find_or_create_from_dict(
                event_data,
                user_id=system_user_id,
                lookup_fields=['name']
            )

def init_data(build_data): 
    init_essential_data(build_data)
    init_assets(build_data)
    
logger.info("Core data initialization completed") 
#!/usr/bin/env python3
"""
Main build orchestrator for the Asset Management System
Handles phased building of models and data insertion
"""

from app import create_app, db
from pathlib import Path
import json
from app.logger import get_logger

logger = get_logger("asset_management.build")

def check_system_initialization():
    """
    Check if the system has been properly initialized
    
    Returns:
        bool: True if system is properly initialized, False otherwise
    """
    from app.models.core.event import Event
    from app.models.core.user import User
    
    try:
        # Check if system initialization event exists
        system_event = Event.query.filter_by(
            event_type='System',
            description='System initialized with core data'
        ).first()
        
        # Check if system user exists
        system_user = User.query.filter_by(username='system').first()
        
        # Check if essential data exists
        from app.models.core.asset_type import AssetType
        asset_types = AssetType.query.first()
        
        return system_event is not None and system_user is not None and asset_types is not None
        
    except Exception as e:
        logger.error(f"Error checking system initialization: {e}")
        return False

def build_database(build_phase='all', data_phase='all'):
    """
    Main build orchestrator for the Asset Management System
    
    Args:
        build_phase (str): 'phase1', 'phase2', 'phase3', 'all', or 'none'
        data_phase (str): 'phase1', 'phase2', 'phase3', 'all', or 'none'
    """
    app = create_app()
    
    with app.app_context():
        logger.info(f"Starting database build - Build Phase: {build_phase}, Data Phase: {data_phase}")
        
        # Build models based on phase
        if build_phase != 'none':
            build_models(build_phase)
        
        # Check if system is properly initialized (after models are built)
        system_initialized = check_system_initialization()
        
        # Insert data based on phase
        if data_phase != 'none':
            try:
                insert_data(data_phase)
                
                # If this is the first time or system failed to init properly, force create system event
                if not system_initialized:
                    logger.info("System not properly initialized, forcing system initialization event creation")
                    from app.models.core.build import create_system_initialization_event
                    from app.models.core.user import User
                    
                    system_user = User.query.filter_by(username='system').first()
                    system_user_id = system_user.id if system_user else None
                    
                    create_system_initialization_event(system_user_id, force_create=True)
                    
            except Exception as e:
                logger.error(f"Error during data insertion: {e}")
                logger.info("System initialization failed, creating system failure event")
                
                # Force create system failure event to indicate system failure
                from app.models.core.build import create_system_failure_event
                from app.models.core.user import User
                
                system_user = User.query.filter_by(username='system').first()
                system_user_id = system_user.id if system_user else None
                
                create_system_failure_event(system_user_id, str(e))
                raise
        
        logger.info("Database build completed successfully")

def build_models(phase):
    """
    Build database models based on the specified phase
    
    Args:
        phase (str): 'phase1', 'phase2', 'phase3', 'phase4', 'phase5', 'phase6', or 'all'
    """
    logger.info(f"Building models for phase: {phase}")
    
    if phase in ['phase1', 'phase2', 'phase3', 'phase4', 'phase5', 'phase6', 'all']:
        logger.info("Building Phase 1 models (Core Foundation)")
        from app.models.core.build import build_models as build_core_models
        build_core_models()
    
    if phase in ['phase2', 'phase3', 'phase4', 'phase5', 'phase6', 'all']:
        logger.info("Building Phase 2 models (Asset Details)")
        from app.models.assets.build import build_models as build_asset_models
        build_asset_models()
    
    if phase in ['phase3', 'phase4', 'phase5', 'phase6', 'all']:
        logger.info("Building Phase 3 models (Dispatching)")
        from app.models.dispatching.build import build_dispatch_models
        build_dispatch_models()
    
    if phase in ['phase4', 'phase5', 'phase6', 'all']:
        logger.info("Building Phase 4 models (Supply)")
        from app.models.supply_items.build import build_models as build_supply_models
        build_supply_models()
    
    if phase in ['phase5', 'phase6', 'all']:
        logger.info("Building Phase 5 models (Maintenance)")
        from app.models.maintenance.build import build_models as build_maintenance_models
        build_maintenance_models()
    
    if phase in ['phase6', 'all']:
        logger.info("Building Phase 6 models (Inventory & Purchasing)")
        from app.models.inventory.build import build_models as build_inventory_models
        build_inventory_models()
    
    # Create all tables
    db.create_all()
    logger.info("All database tables created")

def insert_data(phase):
    """
    Insert initial data based on the specified phase
    
    Args:
        phase (str): 'phase1', 'phase2', 'phase3', 'phase4', 'phase5', 'phase6', or 'all'
    """
    logger.info(f"Inserting data for phase: {phase}")
    
    # Load build data
    build_data = load_build_data()
    
    if phase in ['phase1','phase2', 'phase3', 'phase4', 'phase5', 'phase6', 'all']:
        logger.info("Inserting Phase 1 data (Core Foundation)")
        from app.models.core.build import init_data
        init_data(build_data)
    
    if phase in ['phase2', 'phase3', 'phase4', 'phase5', 'phase6', 'all']:
        logger.info("Inserting Phase 2 data (Asset Details)")
        from app.models.assets.build import phase_2_init_data
        phase_2_init_data(build_data)
    
    if phase in ['phase3', 'phase4', 'phase5', 'phase6', 'all']:
        logger.info("Inserting Phase 3 data (Dispatching)")
        try:
            from app.models.core.asset import Asset
            from app.models.core.build import init_essential_data
            from app.models.assets.build import phase3_insert_data, phase3_update_data
            
            # Automatic detail insertion is now enabled by default in assets build
            init_essential_data(build_data)
            phase3_insert_data(build_data)
            phase3_update_data(build_data)
            
            # Create dispatching users (after core users are created)
            if 'Dispatching' in build_data and 'Users' in build_data['Dispatching']:
                logger.info("Creating dispatching users...")
                from app.models.core.user import User
                system_user = User.query.filter_by(username='system').first()
                system_user_id = system_user.id if system_user else None
                
                for user_key, user_data in build_data['Dispatching']['Users'].items():
                    User.find_or_create_from_dict(
                        user_data,
                        user_id=system_user_id,
                        lookup_fields=['username']
                    )
                    logger.info(f"Created dispatching user: {user_data.get('username')}")
            
            # Setup dispatching configurations
            from app.models.dispatching.build import create_sample_dispatch_configurations, create_example_dispatch_records
            create_sample_dispatch_configurations()
            create_example_dispatch_records()
        except ImportError as e:
            logger.error(f"Phase 3 failed to insert data: {e}")
            raise
    
    if phase in ['phase4', 'phase5', 'phase6', 'all']:
        logger.info("Inserting Phase 4 data (Supply)")
        try:
            from app.models.supply_items.build import init_data as init_supply_data
            init_supply_data(build_data)
        except ImportError as e:
            logger.error(f"Phase 4 failed to insert data: {e}")
            raise
    
    if phase in ['phase5', 'phase6', 'all']:
        logger.info("Inserting Phase 5 data (Maintenance)")
        try:
            from app.models.maintenance.build import init_data as init_maintenance_data
            init_maintenance_data(build_data)
        except ImportError as e:
            logger.error(f"Phase 5 failed to insert data: {e}")
            raise
    
    if phase in ['phase6', 'all']:
        logger.info("Phase 6 data (Inventory & Purchasing)")
        logger.info("No sample data configured for Phase 6 yet")
        # Future: Add Phase 6 sample data
        # from app.models.inventory.build import init_sample_data
        # init_sample_data()
    
    if phase in ['phase4', 'phase5', 'phase6', 'all']:
        logger.info("Setting up User Interface data")
        create_default_admin_user()


def load_build_data():
    """
    Load build data from JSON file
    
    Returns:
        dict: Build data from JSON file
    """
    config_file = Path(__file__).parent / 'utils' / 'build_data.json'
    
    if not config_file.exists():
        raise FileNotFoundError(f"Build data file not found: {config_file}")
    
    with open(config_file, 'r') as f:
        return json.load(f)

def build_models_only(phase):
    """
    Build only the models without inserting data
    
    Args:
        phase (str): 'phase1', 'phase2', 'phase3', 'phase4', 'phase5', or 'all'
    """
    build_database(build_phase=phase, data_phase='none')

def create_default_admin_user():
    """
    Create a default admin user for Phase 4 authentication
    """
    from app.models.core.user import User
    
    # Check if admin user already exists
    admin_user = User.query.filter_by(username='admin').first()
    if admin_user:
        logger.info("Admin user already exists")
        return
    
    # Create default admin user
    admin_user = User(
        username='admin',
        email='admin@assetmanagement.local',
        is_active=True,
        is_admin=True,
        is_system=False
    )
    admin_user.set_password('admin-password-change-me')
    
    db.session.add(admin_user)
    db.session.commit()
    
    logger.info("Default admin user created successfully")
    logger.info("Username: admin")
    logger.info("Password: admin-password-change-me")
    logger.warning("IMPORTANT: Change the default password in production!")

def insert_data_only(phase):
    """
    Insert only data without building models
    
    Args:
        phase (str): 'phase1', 'phase2', 'phase3', 'phase4', 'phase5', or 'all'
    """
    build_database(build_phase='none', data_phase=phase)

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        build_phase = sys.argv[1]
        data_phase = sys.argv[2] if len(sys.argv) > 2 else build_phase
        build_database(build_phase=build_phase, data_phase=data_phase)
    else:
        build_database() 
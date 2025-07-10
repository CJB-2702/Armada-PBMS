from flask_migrate import Migrate
from flask_login import LoginManager
from app.utils.logger import get_logger
from app.extensions import db
import sys

migrate = Migrate()
login_manager = LoginManager()

@login_manager.user_loader
def load_user(user_id):
    from app.models.BaseModels.Users import User
    return User.query.get(int(user_id))

def verify_data_inserted(model_class, expected_count, description):
    """Verify that expected number of records exist in a table"""
    try:
        actual_count = model_class.query.count()
        logger = get_logger()
        logger.info(f"{description}: Expected {expected_count}, Found {actual_count}")
        if actual_count < expected_count:
            raise RuntimeError(f"Expected {expected_count} {model_class.__name__} records, found {actual_count}")
        return True
    except Exception as e:
        logger = get_logger()
        logger.error(f"Error verifying {description}: {e}")
        return False

def create_tables(app):
    """Create tables without foreign key constraints for initial data insertion"""
    with app.app_context():
        logger = get_logger()
        logger.info("=== Starting table creation ===")
        
        # Import all models to ensure they're registered with SQLAlchemy
        logger.info("Importing all models...")
        try:
            from app.models.BaseModels.Users import User
            from app.models.BaseModels.Asset import AssetTypes
            from app.models.BaseModels.Locations import MajorLocation, MinorLocation
            from app.models.BaseModels.Event import Event, EventTypes
            logger.info("✓ All models imported successfully")
        except Exception as e:
            logger.error(f"Error importing models: {e}")
            logger.critical("Critical error: Failed to import required models. Application cannot continue.")
            sys.exit(1)
        
        # Create tables individually in dependency order
        # CRITICAL: This is the order of tables that must be created in order to avoid circular dependencies
        logger.info("Creating tables individually...")
        tables_to_create = [
            (User, "Users"),
            (AssetTypes, "Asset Types"),
            (MajorLocation, "Major Locations"),
            (MinorLocation, "Minor Locations"),
            (EventTypes, "Event Types"),
            (Event, "Events")
        ]
        
        for model, name in tables_to_create:
            try:
                # This will NOT throw an error if table already exists
                model.__table__.create(db.engine, checkfirst=True)
                logger.info(f"✓ Table ready: {name}")
            except Exception as e:
                logger.error(f"Failed to create {name} table: {e}")
                raise
        
        logger.info("=== Table creation completed successfully ===")

def insert_initial_data(app):
    """Insert all required initial data"""
    with app.app_context():
        logger = get_logger()
        logger.info("=== Starting initial data insertion ===")
        
        # Import models for verification
        from app.models.BaseModels.Users import User
        from app.models.BaseModels.Asset import AssetTypes
        from app.models.BaseModels.Locations import MajorLocation
        from app.models.BaseModels.Event import EventTypes, Event
        
        # Users are now created automatically via SQLAlchemy event listener
        # Just verify they exist
        logger.info("--- Step 1: Verifying users ---")
        try:
            verify_data_inserted(User, 2, "Required users (SYSTEM + admin)")
            logger.info("✓ Users verification completed successfully")
        except Exception as e:
            logger.error(f"Users verification failed: {e}")
            raise RuntimeError(f"Critical verification step failed - Users: {e}")
        
        # Insert asset types (no dependencies)
        logger.info("--- Step 2: Creating asset types ---")
        try:
            from app.models.BaseModels.Asset import ensure_required_asset_types
            ensure_required_asset_types()
            verify_data_inserted(AssetTypes, 2, "Required asset types (System + General)")
            logger.info("✓ Asset types initialization completed successfully")
        except Exception as e:
            logger.error(f"Asset types initialization failed: {e}")
            raise RuntimeError(f"Critical initialization step failed - Asset Types: {e}")
        
        # Insert system location (depends on asset types)
        logger.info("--- Step 3: Creating system location ---")
        try:
            from app.models.BaseModels.Locations import ensure_required_system_location
            ensure_required_system_location()
            verify_data_inserted(MajorLocation, 1, "System location")
            logger.info("✓ System location initialization completed successfully")
        except Exception as e:
            logger.error(f"System location initialization failed: {e}")
            raise RuntimeError(f"Critical initialization step failed - System Location: {e}")
        
        # Insert event types (no dependencies)
        logger.info("--- Step 4: Creating event types ---")
        try:
            from app.models.BaseModels.Event import ensure_required_event_types
            ensure_required_event_types()
            verify_data_inserted(EventTypes, 2, "Required event types (System + General)")
            logger.info("✓ Event types initialization completed successfully")
        except Exception as e:
            logger.error(f"Event types initialization failed: {e}")
            raise RuntimeError(f"Critical initialization step failed - Event Types: {e}")
        
        # Create initial events (depends on users, locations, and event types)
        logger.info("--- Step 5: Creating initial events ---")
        try:
            from app.models.BaseModels.Event import create_initial_events
            create_initial_events()
            verify_data_inserted(Event, 3, "Initial events (2 user events + 1 location event)")
            logger.info("✓ Initial events creation completed successfully")
        except Exception as e:
            logger.error(f"Initial events creation failed: {e}")
            raise RuntimeError(f"Critical initialization step failed - Initial Events: {e}")
        
        logger.info("=== Initial data insertion completed successfully ===")


def initialize_database_and_extensions(app):
    logger = get_logger()
    logger.info("=== Starting database initialization ===")
    
    try:
        # Initialize extensions
        db.init_app(app)
        migrate.init_app(app, db)
        login_manager.init_app(app)
        logger.info("✓ Extensions initialized")
        
        # Step 1: Create tables without foreign keys
        create_tables(app)
        
        # Step 2: Insert initial data
        insert_initial_data(app)
        
        logger.info("=== Database initialization completed successfully ===")
        
    except Exception as e:
        logger.error(f"=== Database initialization FAILED: {e} ===")
        raise

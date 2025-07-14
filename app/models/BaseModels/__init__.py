from flask_migrate import Migrate
from flask_login import LoginManager
from app.utils.logger import get_logger
from app.extensions import db
import sys
from datetime import datetime

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

def create_base_tables(app):
    """Create BaseModels tables using SQLAlchemy's automatic table creation"""
    with app.app_context():
        logger = get_logger()
        logger.info("=== Starting BaseModels table creation ===")
        
        # Import BaseModels only
        logger.info("Importing BaseModels...")
        try:
            from app.models.BaseModels.Users import User
            from app.models.BaseModels.Asset import AssetTypes, Statuses, Asset
            from app.models.BaseModels.Locations import MajorLocation, MinorLocation
            from app.models.BaseModels.Event import Event, EventTypes
            logger.info("✓ BaseModels imported successfully")
        except Exception as e:
            logger.error(f"Error importing BaseModels: {e}")
            logger.critical("Critical error: Failed to import required BaseModels. Application cannot continue.")
            sys.exit(1)
        
        # Create BaseModels tables using SQLAlchemy's automatic creation
        try:
            logger.info("Creating BaseModels tables using SQLAlchemy...")
            db.create_all()
            logger.info("✓ BaseModels tables created successfully")
        except Exception as e:
            logger.error(f"Failed to create BaseModels tables: {e}")
            raise
        
        logger.info("=== BaseModels table creation completed successfully ===")

def insert_initial_data(app):
    """Insert all required initial data using hard-coded SQL queries"""
    with app.app_context():
        logger = get_logger()
        logger.info("=== Starting initial data insertion ===")
        
        # Import required data lists
        from app.models.BaseModels.Users import required_users
        from app.models.BaseModels.Asset import required_asset_types, required_statuses
        from app.models.BaseModels.Locations import required_system_locations
        from app.models.BaseModels.Event import required_event_types
        
        # Insert Users (row_id 0 and 1)
        logger.info("--- Inserting Users ---")
        for user_data in required_users:
            db.session.execute(db.text("""
                INSERT OR IGNORE INTO users (row_id, username, email, is_admin, display_name, role, created_by, updated_by, created_at, updated_at)
                VALUES (:row_id, :username, :email, :is_admin, :display_name, :role, :created_by, :updated_by, :created_at, :updated_at)
            """), {
                'row_id': user_data['row_id'],
                'username': user_data['username'],
                'email': user_data['email'],
                'is_admin': user_data['is_admin'],
                'display_name': user_data['display_name'],
                'role': user_data['role'],
                'created_by': user_data['created_by'],
                'updated_by': user_data['created_by'],
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            })
        logger.info(f"✓ Inserted {len(required_users)} users")
        
        # Insert Asset Types (row_id 0 and 1)
        logger.info("--- Inserting Asset Types ---")
        for asset_type_data in required_asset_types:
            db.session.execute(db.text("""
                INSERT OR IGNORE INTO types_assets (row_id, value, description, created_by, updated_by, created_at, updated_at)
                VALUES (:row_id, :value, :description, :created_by, :updated_by, :created_at, :updated_at)
            """), {
                'row_id': asset_type_data['row_id'],
                'value': asset_type_data['name'],
                'description': asset_type_data['description'],
                'created_by': asset_type_data['created_by'],
                'updated_by': asset_type_data['created_by'],
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            })
        logger.info(f"✓ Inserted {len(required_asset_types)} asset types")
        
        # Insert Statuses (row_id 0, 1, 2, 3)
        logger.info("--- Inserting Statuses ---")
        for status_data in required_statuses:
            db.session.execute(db.text("""
                INSERT OR IGNORE INTO types_statuses (row_id, value, description, created_by, updated_by, created_at, updated_at)
                VALUES (:row_id, :value, :description, :created_by, :updated_by, :created_at, :updated_at)
            """), {
                'row_id': status_data['row_id'],
                'value': status_data['name'],
                'description': status_data['description'],
                'created_by': status_data['created_by'],
                'updated_by': status_data['created_by'],
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            })
        logger.info(f"✓ Inserted {len(required_statuses)} statuses")
        
        # Insert System Locations (row_id 0 and 1)
        logger.info("--- Inserting System Locations ---")
        for location_data in required_system_locations:
            db.session.execute(db.text("""
                INSERT OR IGNORE INTO MajorLocations (row_id, UID, asset_type, common_name, description, status, created_by, updated_by, created_at, updated_at)
                VALUES (:row_id, :UID, :asset_type, :common_name, :description, :status, :created_by, :updated_by, :created_at, :updated_at)
            """), {
                'row_id': location_data['row_id'],
                'UID': location_data['UID'],
                'asset_type': 'MajorLocation',
                'common_name': location_data['common_name'],
                'description': location_data['description'],
                'status': location_data['status'],
                'created_by': location_data['created_by'],
                'updated_by': location_data['created_by'],
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            })
        logger.info(f"✓ Inserted {len(required_system_locations)} system locations")
        
        # Insert Event Types (row_id 0 and 1)
        logger.info("--- Inserting Event Types ---")
        for event_type_data in required_event_types:
            db.session.execute(db.text("""
                INSERT OR IGNORE INTO types_events (row_id, value, description, created_by, updated_by, created_at, updated_at)
                VALUES (:row_id, :value, :description, :created_by, :updated_by, :created_at, :updated_at)
            """), {
                'row_id': event_type_data['row_id'],
                'value': event_type_data['name'],
                'description': event_type_data['description'],
                'created_by': event_type_data['created_by'],
                'updated_by': event_type_data['created_by'],
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            })
        logger.info(f"✓ Inserted {len(required_event_types)} event types")
        
        # Insert Initial Events
        logger.info("--- Inserting Initial Events ---")
        initial_events = [
            {
                'row_id': 0,
                'title': 'User Created: SYSTEM (ID: 0)',
                'description': 'User created.\nUsername: SYSTEM\nDisplay Name: System\nEmail: system@null.null\nRole: admin\nIs Admin: True',
                'event_type': 'System',
                'status': 'Completed',
                'location_uid': "SYSTEM",
                'created_by': 0
            },
            {
                'row_id': 1,
                'title': 'User Created: admin (ID: 1)',
                'description': 'User created.\nUsername: admin\nDisplay Name: System Administrator\nEmail: admin@null.com\nRole: admin\nIs Admin: True',
                'event_type': 'System',
                'status': 'Completed',
                'location_uid': "SYSTEM",
                'created_by': 0
            },
            {
                'row_id': 2,
                'title': 'System Location Created: System Location (ID: 0)',
                'description': 'System location created.\nUID: SYSTEM\nCommon Name: System Location\nDescription: Virtual system location for internal system operations REQUIRED FOR SYSTEM OPERATIONS\nStatus: active',
                'event_type': 'System',
                'status': 'Completed',
                'location_uid': "SYSTEM",
                'created_by': 0
            }
        ]
        
        for event_data in initial_events:
            db.session.execute(db.text("""
                INSERT OR IGNORE INTO events (row_id, title, description, event_type, status, location_UID, created_by, updated_by, created_at, updated_at)
                VALUES (:row_id, :title, :description, :event_type, :status, :location_UID, :created_by, :updated_by, :created_at, :updated_at)
            """), {
                'row_id': event_data['row_id'],
                'title': event_data['title'],
                'description': event_data['description'],
                'event_type': event_data['event_type'],
                'status': event_data['status'],
                'location_UID': event_data['location_uid'],
                'created_by': event_data['created_by'],
                'updated_by': event_data['created_by'],
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            })
        logger.info(f"✓ Inserted {len(initial_events)} initial events")
        
        # Commit all changes
        db.session.commit()
        logger.info("=== Initial data insertion completed successfully ===")

def initialize_base_models(app):
    """Initialize BaseModels - this is the new function for explicit initialization"""
    logger = get_logger()
    logger.info("=== Starting BaseModels initialization ===")
    
    try:
        # Initialize extensions (only once, during BaseModels initialization)
        db.init_app(app)
        migrate.init_app(app, db)
        login_manager.init_app(app)
        logger.info("✓ Extensions initialized")
        
        # Step 1: Create BaseModels tables
        create_base_tables(app)
        
        # Step 2: Insert initial data
        insert_initial_data(app)
        
        logger.info("=== BaseModels initialization completed successfully ===")
        
    except Exception as e:
        logger.error(f"=== BaseModels initialization FAILED: {e} ===")
        raise

def initialize_database_and_extensions(app):
    """Legacy function for backward compatibility"""
    logger = get_logger()
    logger.info("=== Starting database initialization (legacy mode) ===")
    
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

def create_tables(app):
    """Legacy function - Create tables using SQLAlchemy's automatic table creation"""
    with app.app_context():
        logger = get_logger()
        logger.info("=== Starting table creation (legacy mode) ===")
        
        # Import all models to ensure they're registered with SQLAlchemy
        logger.info("Importing all models...")
        try:
            from app.models.BaseModels.Users import User
            from app.models.BaseModels.Asset import AssetTypes, Statuses, Asset
            from app.models.BaseModels.Locations import MajorLocation, MinorLocation
            from app.models.BaseModels.Event import Event, EventTypes
            logger.info("✓ All models imported successfully")
        except Exception as e:
            logger.error(f"Error importing models: {e}")
            logger.critical("Critical error: Failed to import required models. Application cannot continue.")
            sys.exit(1)
        
        # Create all tables using SQLAlchemy's automatic creation
        try:
            logger.info("Creating tables using SQLAlchemy...")
            db.create_all()
            logger.info("✓ All tables created successfully")
        except Exception as e:
            logger.error(f"Failed to create tables: {e}")
            raise
        
        logger.info("=== Table creation completed successfully ===")

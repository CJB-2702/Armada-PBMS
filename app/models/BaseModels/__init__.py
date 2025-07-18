from flask_migrate import Migrate
from flask_login import LoginManager
from app.utils.logger import get_logger
from app.extensions import db
import sys
import json
import os
from datetime import datetime
from sqlalchemy import MetaData

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

def load_json_data(filename):
    """Load data from JSON file in the initial_data directory"""
    try:
        file_path = os.path.join(os.path.dirname(__file__), 'initial_data', filename)
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logger = get_logger()
        logger.error(f"JSON file not found: {filename}")
        raise
    except json.JSONDecodeError as e:
        logger = get_logger()
        logger.error(f"Invalid JSON in {filename}: {e}")
        raise

def validate_data_structure(data, required_fields, data_type):
    """Validate that data has the required structure"""
    if not isinstance(data, list):
        raise ValueError(f"{data_type} data must be a list")
    
    for i, item in enumerate(data):
        if not isinstance(item, dict):
            raise ValueError(f"{data_type} item {i} must be a dictionary")
        
        for field in required_fields:
            if field not in item:
                raise ValueError(f"{data_type} item {i} missing required field: {field}")

def create_base_tables(app):
    """Create BaseModels tables in controlled order"""
    with app.app_context():
        logger = get_logger()
        logger.info("=== Starting BaseModels table creation ===")
        
        # Import BaseModels, Utility models, and concrete models in order
        logger.info("Importing BaseModels, Utility models, and concrete models...")
        try:
            # Step 1: Import BaseModels (foundation tables)
            from app.models.BaseModels.Users import User
            from app.models.BaseModels.Asset import AssetTypes, Statuses, AbstractAsset, AbstractModel
            from app.models.BaseModels.Locations import MajorLocation, MinorLocation
            from app.models.BaseModels.Event import Event, EventTypes
            logger.info("✓ BaseModels imported successfully")
            
            # Step 2: Import Utility models (referenced by Assets)
            from app.models.Utility.Lists import GenericTypes, Dropdowns
            logger.info("✓ Utility models imported successfully")
            
            # Step 3: Import concrete Asset models (depend on Utility models)
            from app.models.Assets.Assets import Asset
            logger.info("✓ Concrete Asset models imported successfully")
            
            logger.info("✓ All models imported successfully in correct order")
        except Exception as e:
            logger.error(f"Error importing models: {e}")
            logger.critical("Critical error: Failed to import required models. Application cannot continue.")
            sys.exit(1)
        
        # Create BaseModels tables using SQLAlchemy's automatic creation
        try:
            logger.info("Creating BaseModels tables using SQLAlchemy...")
            # Create only the tables for imported models
            db.create_all()
            logger.info("✓ BaseModels tables created successfully")
        except Exception as e:
            logger.error(f"Failed to create BaseModels tables: {e}")
            raise
        
        logger.info("=== BaseModels table creation completed successfully ===")

def insert_initial_data(app):
    """Insert all required initial data using JSON files and proper validation"""
    with app.app_context():
        logger = get_logger()
        logger.info("=== Starting initial data insertion ===")
        
        # Start transaction
        transaction_started = False
        try:
            # Import required data lists from models
            from app.models.BaseModels.Users import required_users
            from app.models.BaseModels.Asset import required_asset_types
            from app.models.BaseModels.Locations import required_system_locations
            from app.models.BaseModels.Event import required_event_types
            
            # Load data from JSON files
            logger.info("Loading data from JSON files...")
            
            # Load statuses from JSON
            statuses_data = load_json_data('required_statuses.json')
            required_statuses = statuses_data.get('required_statuses', [])
            
            # Load initial events from JSON
            events_data = load_json_data('initial_events.json')
            initial_events = events_data.get('initial_events', [])
            
            # Validate data structures
            logger.info("Validating data structures...")
            validate_data_structure(required_users, ['row_id', 'username', 'email', 'is_admin', 'display_name', 'role', 'created_by'], 'Users')
            validate_data_structure(required_asset_types, ['row_id', 'name', 'description', 'created_by'], 'Asset Types')
            validate_data_structure(required_statuses, ['row_id', 'name', 'description', 'created_by'], 'Statuses')
            validate_data_structure(required_system_locations, ['row_id', 'UID', 'common_name', 'description', 'status', 'created_by'], 'System Locations')
            validate_data_structure(required_event_types, ['row_id', 'name', 'description', 'created_by'], 'Event Types')
            validate_data_structure(initial_events, ['row_id', 'title', 'description', 'event_type', 'status', 'location_UID', 'created_by'], 'Initial Events')
            
            logger.info("✓ Data validation completed")
            
            # Start transaction
            transaction_started = True
            
            # Insert Users (row_id 0 and 1)
            logger.info("--- Inserting Users ---")
            for user_data in required_users:
                db.session.execute(db.text("""
                    INSERT OR IGNORE INTO users (row_id, username, email, is_admin, display_name, role, created_by, updated_by, created_at, updated_at, is_active)
                    VALUES (:row_id, :username, :email, :is_admin, :display_name, :role, :created_by, :updated_by, :created_at, :updated_at, :is_active)
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
                    'updated_at': datetime.now(),
                    'is_active': True
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
                    INSERT OR IGNORE INTO major_locations (row_id, UID, asset_type, common_name, description, status, created_by, updated_by, created_at, updated_at)
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
                    'location_UID': event_data['location_UID'],
                    'created_by': event_data['created_by'],
                    'updated_by': event_data['created_by'],
                    'created_at': datetime.now(),
                    'updated_at': datetime.now()
                })
            logger.info(f"✓ Inserted {len(initial_events)} initial events")
            
            # Commit all changes
            db.session.commit()
            logger.info("✓ Transaction committed successfully")
            
            # Verify data insertion
            logger.info("--- Verifying data insertion ---")
            from app.models.BaseModels.Users import User
            from app.models.BaseModels.Asset import AssetTypes, Statuses
            from app.models.BaseModels.Locations import MajorLocation
            from app.models.BaseModels.Event import Event, EventTypes
            
            verification_passed = True
            verification_passed &= verify_data_inserted(User, len(required_users), "Users")
            verification_passed &= verify_data_inserted(AssetTypes, len(required_asset_types), "Asset Types")
            verification_passed &= verify_data_inserted(Statuses, len(required_statuses), "Statuses")
            verification_passed &= verify_data_inserted(MajorLocation, len(required_system_locations), "System Locations")
            verification_passed &= verify_data_inserted(EventTypes, len(required_event_types), "Event Types")
            verification_passed &= verify_data_inserted(Event, len(initial_events), "Initial Events")
            
            if verification_passed:
                logger.info("=== Initial data insertion completed successfully ===")
            else:
                raise RuntimeError("Data verification failed - some records were not inserted properly")
                
        except Exception as e:
            logger.error(f"Error during initial data insertion: {e}")
            if transaction_started:
                logger.info("Rolling back transaction...")
                db.session.rollback()
                logger.info("✓ Transaction rolled back")
            raise

def initialize_base_models(app):
    """Initialize BaseModels - this is the new function for explicit initialization"""
    logger = get_logger()
    logger.info("=== Starting BaseModels initialization ===")
    
    try:
        # Extensions are already initialized in create_app, so skip initialization here
        logger.info("✓ Extensions already initialized")
        
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
        
        # Import all models in correct order to ensure they're registered with SQLAlchemy
        logger.info("Importing all models in correct order...")
        try:
            # Step 1: Import BaseModels (foundation tables)
            from app.models.BaseModels.Users import User
            from app.models.BaseModels.Asset import AssetTypes, Statuses, AbstractAsset, AbstractModel
            from app.models.BaseModels.Locations import MajorLocation, MinorLocation
            from app.models.BaseModels.Event import Event, EventTypes
            logger.info("✓ BaseModels imported successfully")
            
            # Step 2: Import Utility models (referenced by Assets)
            from app.models.Utility.Lists import GenericTypes, Dropdowns
            logger.info("✓ Utility models imported successfully")
            
            # Step 3: Import concrete Asset models (depend on Utility models)
            from app.models.Assets.Assets import Asset
            logger.info("✓ Concrete Asset models imported successfully")
            
            logger.info("✓ All models imported successfully in correct order")
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

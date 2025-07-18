from app.utils.logger import get_logger
from app.extensions import db
from datetime import datetime


def create_utility_tables(app):
    """Create Utility models tables using SQLAlchemy's automatic table creation"""
    with app.app_context():
        logger = get_logger()
        logger.info("=== Starting Utility table creation ===")
        
        # Import Utility models only
        logger.info("Importing Utility models...")
        try:
            from app.models.Utility.Attachments import Attachments
            from app.models.Utility.Lists import GenericTypes, Dropdowns
            from app.models.Utility.MiscLocations import MiscLocations
            logger.info("✓ Utility models imported successfully")
        except Exception as e:
            logger.error(f"Error importing Utility models: {e}")
            logger.critical("Critical error: Failed to import required Utility models. Application cannot continue.")
            raise
        
        # Create Utility tables using SQLAlchemy's automatic creation
        try:
            logger.info("Creating Utility tables using SQLAlchemy...")
            db.create_all()
            logger.info("✓ Utility tables created successfully")
        except Exception as e:
            logger.error(f"Failed to create Utility tables: {e}")
            raise
        
        logger.info("=== Utility table creation completed successfully ===")


def insert_utility_initial_data(app):
    """Insert initial data for Utility models"""
    with app.app_context():
        logger = get_logger()
        logger.info("=== Starting Utility initial data insertion ===")
        
        # Import meter types from JSON file
        import json
        import os
        
        meter_types_file = os.path.join(
            os.path.dirname(__file__), 
            '..', 'BaseModels', 'initial_data', 'meter_types.json'
        )
        
        try:
            with open(meter_types_file, 'r') as f:
                meter_data = json.load(f)
            
            # Insert meter types into generic_types table
            logger.info("--- Inserting Meter Types ---")
            for meter_type_data in meter_data['meter_types']:
                db.session.execute(db.text("""
                    INSERT OR IGNORE INTO generic_types (UID, group, value, description, created_by, updated_by, created_at, updated_at)
                    VALUES (:UID, :group, :value, :description, :created_by, :updated_by, :created_at, :updated_at)
                """), {
                    'UID': f"meter_types_{meter_type_data['name']}",
                    'group': 'meter_types',
                    'value': meter_type_data['name'],
                    'description': meter_type_data['description'],
                    'created_by': meter_type_data['created_by'],
                    'updated_by': meter_type_data['created_by'],
                    'created_at': datetime.now(),
                    'updated_at': datetime.now()
                })
            
            logger.info(f"✓ Inserted {len(meter_data['meter_types'])} meter types")
            
        except FileNotFoundError:
            logger.warning(f"Meter types file not found: {meter_types_file}")
        except Exception as e:
            logger.error(f"Error loading meter types: {e}")
        
        # Commit all changes
        db.session.commit()
        logger.info("=== Utility initial data insertion completed successfully ===")


def initialize_utility_models(app):
    """Initialize Utility models"""
    logger = get_logger()
    logger.info("=== Starting Utility models initialization ===")
    
    try:
        # Step 1: Create Utility tables
        create_utility_tables(app)
        
        # Step 2: Insert Utility initial data
        insert_utility_initial_data(app)
        
        logger.info("=== Utility models initialization completed successfully ===")
        
    except Exception as e:
        logger.error(f"=== Utility models initialization FAILED: {e} ===")
        raise 
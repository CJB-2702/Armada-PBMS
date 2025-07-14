from app.utils.logger import get_logger
from app.extensions import db


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
        
        # No initial data required for Utility models at this time
        logger.info("✓ No initial data required for Utility models")
        
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
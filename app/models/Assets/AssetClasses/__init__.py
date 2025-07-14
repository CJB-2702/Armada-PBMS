from app.utils.logger import get_logger
from app.extensions import db


def create_asset_classes_tables(app):
    """Create AssetClasses models tables using SQLAlchemy's automatic table creation"""
    with app.app_context():
        logger = get_logger()
        logger.info("=== Starting AssetClasses table creation ===")
        
        # Import AssetClasses models only
        logger.info("Importing AssetClasses models...")
        try:
            from app.models.Assets.AssetClasses.Vehicles import Vehicle
            logger.info("✓ AssetClasses models imported successfully")
        except Exception as e:
            logger.error(f"Error importing AssetClasses models: {e}")
            logger.critical("Critical error: Failed to import required AssetClasses models. Application cannot continue.")
            raise
        
        # Create AssetClasses tables using SQLAlchemy's automatic creation
        try:
            logger.info("Creating AssetClasses tables using SQLAlchemy...")
            db.create_all()
            logger.info("✓ AssetClasses tables created successfully")
        except Exception as e:
            logger.error(f"Failed to create AssetClasses tables: {e}")
            raise
        
        logger.info("=== AssetClasses table creation completed successfully ===")


def insert_asset_classes_initial_data(app):
    """Insert initial data for AssetClasses models"""
    with app.app_context():
        logger = get_logger()
        logger.info("=== Starting AssetClasses initial data insertion ===")
        
        # No initial data required for AssetClasses models at this time
        logger.info("✓ No initial data required for AssetClasses models")
        
        logger.info("=== AssetClasses initial data insertion completed successfully ===")


def initialize_asset_classes(app):
    """Initialize AssetClasses models"""
    logger = get_logger()
    logger.info("=== Starting AssetClasses models initialization ===")
    
    try:
        # Step 1: Create AssetClasses tables
        create_asset_classes_tables(app)
        
        # Step 2: Insert AssetClasses initial data
        insert_asset_classes_initial_data(app)
        
        logger.info("=== AssetClasses models initialization completed successfully ===")
        
    except Exception as e:
        logger.error(f"=== AssetClasses models initialization FAILED: {e} ===")
        raise 
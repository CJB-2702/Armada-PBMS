from app.utils.logger import get_logger
from app.extensions import db


def create_asset_classes_tables(app):
    """Create AssetClasses models tables using SQLAlchemy's automatic table creation"""
    with app.app_context():
        logger = get_logger()
        logger.info("=== Starting AssetClasses table creation ===")
        
        # Import and create tables for each enabled asset class
        logger.info("Importing AssetClasses models...")
        try:
            # Import Vehicles models for table creation
            from app.models.Assets.AssetClasses.Vehicles import import_vehicles_models
            import_vehicles_models()
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
        
        # Initialize each enabled asset class
        try:
            # Initialize Vehicles if enabled
            from app.models.Assets.AssetClasses.Vehicles import initialize_vehicles_models
            initialize_vehicles_models(app)
            logger.info("✓ AssetClasses initial data insertion completed")
        except Exception as e:
            logger.error(f"Error during AssetClasses initial data insertion: {e}")
            raise
        
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
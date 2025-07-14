from app.utils.logger import get_logger
from app.extensions import db
from datetime import datetime


def create_assets_tables(app):
    """Create Assets models tables using SQLAlchemy's automatic table creation"""
    with app.app_context():
        logger = get_logger()
        logger.info("=== Starting Assets table creation ===")
        
        # Import Assets models only
        logger.info("Importing Assets models...")
        try:
            from app.models.Assets.Assets import Asset
            from app.models.Assets.AssetEvents import AssetEvent
            logger.info("✓ Assets models imported successfully")
        except Exception as e:
            logger.error(f"Error importing Assets models: {e}")
            logger.critical("Critical error: Failed to import required Assets models. Application cannot continue.")
            raise
        
        # Create Assets tables using SQLAlchemy's automatic creation
        try:
            logger.info("Creating Assets tables using SQLAlchemy...")
            db.create_all()
            logger.info("✓ Assets tables created successfully")
        except Exception as e:
            logger.error(f"Failed to create Assets tables: {e}")
            raise
        
        logger.info("=== Assets table creation completed successfully ===")


def insert_assets_initial_data(app):
    """Insert initial data for Assets models"""
    with app.app_context():
        logger = get_logger()
        logger.info("=== Starting Assets initial data insertion ===")
        
        # Import additional statuses from Assets
        from app.models.Assets.Assets import additional_statuses
        
        # Insert additional statuses
        logger.info("--- Inserting Additional Asset Statuses ---")
        for status_data in additional_statuses:
            db.session.execute(db.text("""
                INSERT OR IGNORE INTO types_statuses (value, description, created_by, updated_by, created_at, updated_at)
                VALUES (:value, :description, :created_by, :updated_by, :created_at, :updated_at)
            """), {
                'value': status_data['name'],
                'description': status_data['description'],
                'created_by': 0,  # SYSTEM user
                'updated_by': 0,  # SYSTEM user
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            })
        logger.info(f"✓ Inserted {len(additional_statuses)} additional asset statuses")
        
        # Commit all changes
        db.session.commit()
        logger.info("=== Assets initial data insertion completed successfully ===")


def initialize_assets_models(app):
    """Initialize Assets models"""
    logger = get_logger()
    logger.info("=== Starting Assets models initialization ===")
    
    try:
        # Step 1: Create Assets tables
        create_assets_tables(app)
        
        # Step 2: Insert Assets initial data
        insert_assets_initial_data(app)
        
        logger.info("=== Assets models initialization completed successfully ===")
        
    except Exception as e:
        logger.error(f"=== Assets models initialization FAILED: {e} ===")
        raise

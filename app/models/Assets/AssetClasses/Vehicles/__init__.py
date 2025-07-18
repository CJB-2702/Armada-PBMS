from app.utils.logger import get_logger
from app.extensions import db
from datetime import datetime
import json
from pathlib import Path


def is_vehicles_enabled():
    """Check if Vehicles asset class is enabled in the config"""
    try:
        config_path = Path(__file__).parent.parent.parent.parent.parent / "CONFIG" / "build.json"
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        return config.get("Assets", {}).get("AssetClasses", {}).get("Vehicles", False)
    except Exception as e:
        logger = get_logger()
        logger.warning(f"Could not read config file, defaulting to disabled: {e}")
        return False


def import_vehicles_models():
    """Import Vehicles models for table creation"""
    logger = get_logger()
    logger.info("=== Importing Vehicles models ===")
    
    try:
        from app.models.Assets.AssetClasses.Vehicles.Vehicles import Vehicle, VehicleModel, VehiclePurchaseInfo
        logger.info("✓ Vehicles models imported successfully")
    except Exception as e:
        logger.error(f"Error importing Vehicles models: {e}")
        logger.critical("Critical error: Failed to import required Vehicles models. Application cannot continue.")
        raise


def insert_vehicles_initial_data(app):
    """Insert initial data for Vehicles models"""
    with app.app_context():
        logger = get_logger()
        logger.info("=== Starting Vehicles initial data insertion ===")
        
        # Insert meter types from JSON file
        logger.info("--- Inserting Vehicle Meter Types ---")
        try:
            meter_types_path = Path(__file__).parent / "meter_types.json"
            with open(meter_types_path, 'r') as f:
                meter_types = json.load(f)
            
            for meter_type in meter_types:
                db.session.execute(db.text("""
                    INSERT OR IGNORE INTO generic_types (UID, `group`, value, description, created_by, updated_by, created_at, updated_at)
                    VALUES (:UID, :group, :value, :description, :created_by, :updated_by, :created_at, :updated_at)
                """), {
                    'UID': f"meter_types_{meter_type['name']}",
                    'group': 'meter_types',
                    'value': meter_type['name'],
                    'description': meter_type['description'],
                    'created_by': meter_type.get('created_by', 0),  # SYSTEM user
                    'updated_by': meter_type.get('created_by', 0),  # SYSTEM user
                    'created_at': datetime.now(),
                    'updated_at': datetime.now()
                })
            logger.info(f"✓ Inserted {len(meter_types)} vehicle meter types")
        except Exception as e:
            logger.error(f"Error inserting meter types: {e}")
            raise
        
        # Insert vehicle asset type
        logger.info("--- Inserting Vehicle Asset Type ---")
        try:
            from app.models.Assets.AssetClasses.Vehicles.Vehicles import asset_type
            db.session.execute(db.text("""
                INSERT OR IGNORE INTO types_assets (value, description, created_by, updated_by, created_at, updated_at)
                VALUES (:value, :description, :created_by, :updated_by, :created_at, :updated_at)
            """), {
                'value': asset_type['name'],
                'description': asset_type['description'],
                'created_by': asset_type.get('created_by', 0),  # SYSTEM user
                'updated_by': asset_type.get('created_by', 0),  # SYSTEM user
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            })
            logger.info("✓ Inserted vehicle asset type")
        except Exception as e:
            logger.error(f"Error inserting vehicle asset type: {e}")
            raise
        
        # Commit all changes
        db.session.commit()
        logger.info("=== Vehicles initial data insertion completed successfully ===")


def initialize_vehicles_models(app):
    """Initialize Vehicles models if enabled in config"""
    logger = get_logger()
    logger.info("=== Starting Vehicles models initialization check ===")
    
    # Check if Vehicles is enabled in config
    if not is_vehicles_enabled():
        logger.info("Vehicles asset class is disabled in config. Skipping initialization.")
        return
    
    logger.info("Vehicles asset class is enabled in config. Proceeding with initialization.")
    
    try:
        # Import models for table creation (tables are created by parent module)
        import_vehicles_models()
        
        # Insert Vehicles initial data
        insert_vehicles_initial_data(app)
        
        logger.info("=== Vehicles models initialization completed successfully ===")
        
    except Exception as e:
        logger.error(f"=== Vehicles models initialization FAILED: {e} ===")
        raise

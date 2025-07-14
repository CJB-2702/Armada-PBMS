"""
Centralized database initialization controller
This module manages the proper order of table creation and data insertion
"""

from app.utils.logger import get_logger
from app.extensions import db
from datetime import datetime


class DatabaseInitializer:
    """Controls the database initialization process in the correct order"""
    
    def __init__(self, app):
        self.app = app
        self.logger = get_logger()
        self.initialization_complete = False
    
    def initialize_database(self):
        """Initialize the entire database in the correct order"""
        self.logger.info("=== Starting controlled database initialization ===")
        
        try:
            # Initialize extensions first
            self._initialize_extensions()
            
            # Import all models in the correct dependency order
            self._import_all_models_in_order()
            
            # Create all tables at once (SQLAlchemy handles dependencies)
            self._create_all_tables()
            
            # Insert data in the correct order
            self._insert_data_in_order()
            
            self.initialization_complete = True
            self.logger.info("=== Database initialization completed successfully ===")
            
        except Exception as e:
            self.logger.error(f"=== Database initialization FAILED: {e} ===")
            raise
    
    def _initialize_extensions(self):
        """Initialize Flask extensions"""
        with self.app.app_context():
            from app.models.BaseModels import db, migrate, login_manager
            db.init_app(self.app)
            migrate.init_app(self.app, db)
            login_manager.init_app(self.app)
            self.logger.info("✓ Extensions initialized")
    
    def _import_all_models_in_order(self):
        """Import all models in the correct dependency order"""
        self.logger.info("Importing all models in dependency order...")
        
        # Phase 1: BaseModels (foundation models)
        self.logger.info("Phase 1: Importing BaseModels...")
        from app.models.BaseModels.Users import User
        from app.models.BaseModels.Asset import AssetTypes, Statuses, AbstractAsset
        from app.models.BaseModels.Locations import MajorLocation, MinorLocation
        from app.models.BaseModels.Event import Event, EventTypes
        
        # Phase 2: Utility models
        self.logger.info("Phase 2: Importing Utility models...")
        from app.models.Utility.Attachments import Attachments
        from app.models.Utility.Lists import GenericTypes, Dropdowns
        from app.models.Utility.MiscLocations import MiscLocations
        
        # Phase 3: Assets models
        self.logger.info("Phase 3: Importing Assets models...")
        from app.models.Assets.Assets import Asset
        from app.models.Assets.AssetEvents import AssetEvent
        
        # Phase 4: AssetClasses models
        self.logger.info("Phase 4: Importing AssetClasses models...")
        from app.models.Assets.AssetClasses.Vehicles import Vehicle, VehicleModel, VehiclePurchaseInfo
        
        self.logger.info("✓ All models imported successfully")
    
    def _create_all_tables(self):
        """Create all tables at once"""
        with self.app.app_context():
            self.logger.info("Creating all tables...")
            db.create_all()
            self.logger.info("✓ All tables created successfully")
    
    def _insert_data_in_order(self):
        """Insert initial data in the correct order"""
        with self.app.app_context():
            self.logger.info("Inserting initial data in order...")
            
            # Phase 1: BaseModels data
            self.logger.info("Phase 1: Inserting BaseModels data...")
            from app.models.BaseModels import insert_initial_data
            insert_initial_data(self.app)
            
            # Phase 2: Utility data
            self.logger.info("Phase 2: Inserting Utility data...")
            from app.models.Utility import insert_utility_initial_data
            insert_utility_initial_data(self.app)
            
            # Phase 3: Assets data
            self.logger.info("Phase 3: Inserting Assets data...")
            from app.models.Assets import insert_assets_initial_data
            insert_assets_initial_data(self.app)
            
            # Phase 4: AssetClasses data
            self.logger.info("Phase 4: Inserting AssetClasses data...")
            from app.models.Assets.AssetClasses import insert_asset_classes_initial_data
            insert_asset_classes_initial_data(self.app)
            
            self.logger.info("✓ All initial data inserted successfully")


def initialize_database_controlled(app):
    """Main function to initialize database in controlled order"""
    initializer = DatabaseInitializer(app)
    initializer.initialize_database()
    return initializer

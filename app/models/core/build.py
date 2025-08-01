#!/usr/bin/env python3
"""
Build script for Phase 1 core models
Creates tables in the correct dependency order
"""

from app import db
from app.models.core.user import User
from app.models.core.user_created_base import UserCreatedBase
from app.models.core.major_location import MajorLocation
from app.models.core.asset_type import AssetType
from app.models.core.make_model import MakeModel
from app.models.core.asset import Asset
from app.models.core.event import Event

def build_core_tables():
    """Build all core tables in dependency order (Phase 1A)"""
    print("=== Building Core Tables ===")
    
    try:
        # Step 1: Create User table (independent, no dependencies)
        print("1. Creating User table...")
        User.__table__.create(db.engine, checkfirst=True)
        print("   ✓ User table created")
        
        # Step 2: Create tables that inherit from UserCreatedBase
        # These depend on User table existing
        print("2. Creating MajorLocation table...")
        MajorLocation.__table__.create(db.engine, checkfirst=True)
        print("   ✓ MajorLocation table created")
        
        print("3. Creating AssetType table...")
        AssetType.__table__.create(db.engine, checkfirst=True)
        print("   ✓ AssetType table created")
        
        print("4. Creating MakeModel table...")
        MakeModel.__table__.create(db.engine, checkfirst=True)
        print("   ✓ MakeModel table created")
        
        # Step 3: Create Asset table (depends on MajorLocation, AssetType, MakeModel)
        print("5. Creating Asset table...")
        Asset.__table__.create(db.engine, checkfirst=True)
        print("   ✓ Asset table created")
        
        # Step 4: Create Event table (depends on User and Asset)
        print("6. Creating Event table...")
        Event.__table__.create(db.engine, checkfirst=True)
        print("   ✓ Event table created")
        
        print("\n=== All Core Tables Built Successfully ===")
        return True
        
    except Exception as e:
        print(f"\n=== Core Table Build FAILED ===")
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def initialize_system_data(include_assets=True):
    """Initialize system with required base data (Phase 1B)"""
    print("=== Initializing System Data ===")
    
    try:
        # Load configuration data from centralized location
        from app.models.core.init_data import CoreDataLoader
        data_loader = CoreDataLoader()
        success = data_loader.load_core_data(include_assets=include_assets)
        return success
    except Exception as e:
        print(f"Error initializing system data: {e}")
        return False

def update_system_data():
    """Update system data (if needed for future use)"""
    print("=== Updating System Data ===")
    
    try:
        # Load configuration data from centralized location
        from app.models.core.init_data import CoreDataLoader
        data_loader = CoreDataLoader()
        # For now, just reload the data (could be extended for updates)
        success = data_loader.load_core_data()
        return success
    except Exception as e:
        print(f"Error updating system data: {e}")
        return False

def verify_core_tables():
    """Verify all core tables were created"""
    print("\n=== Verifying Core Tables ===")
    
    try:
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        
        expected_tables = ['users', 'major_locations', 'asset_types', 'make_models', 'assets', 'events']
        
        for table in expected_tables:
            if table in tables:
                print(f"   ✓ Table '{table}' exists")
            else:
                print(f"   ✗ Table '{table}' missing")
                return False
        
        print(f"   ✓ All {len(expected_tables)} expected tables found")
        return True
        
    except Exception as e:
        print(f"   ✗ Verification failed: {e}")
        return False

def show_table_schemas():
    """Show the schema of all created tables"""
    print("\n=== Table Schemas ===")
    
    try:
        inspector = db.inspect(db.engine)
        tables = ['users', 'major_locations', 'asset_types', 'make_models', 'assets', 'events']
        
        for table_name in tables:
            print(f"\nTable: {table_name}")
            columns = inspector.get_columns(table_name)
            for column in columns:
                nullable = "NULL" if column['nullable'] else "NOT NULL"
                print(f"  - {column['name']}: {column['type']} {nullable}")
                
    except Exception as e:
        print(f"Error showing schemas: {e}")

if __name__ == '__main__':
    # This can be run directly for testing
    from app import create_app
    import sys
    
    app = create_app()
    with app.app_context():
        # Check if update mode is requested
        if len(sys.argv) > 1 and sys.argv[1] == '--update':
            print("Running in UPDATE mode...")
            update_success = update_system_data()
            if update_success:
                print("System data update completed successfully")
            else:
                print("System data update failed")
        else:
            # Normal build and initialize mode
            success = build_core_tables()
            if success:
                data_success = initialize_system_data()
                if data_success:
                    verify_core_tables()
                    show_table_schemas()
                else:
                    print("System data initialization failed")
            else:
                print("Core table build failed")
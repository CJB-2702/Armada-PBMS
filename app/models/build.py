#!/usr/bin/env python3
"""
Main build script for all models
Orchestrates the building of tables in the correct order
"""

from app import db
from app.models.core.build import build_core_tables, verify_core_tables, show_table_schemas
from app.models.core.build import initialize_system_data

# Import all core models to ensure they're registered with SQLAlchemy
from app.models.core.user import User
from app.models.core.user_created_base import UserCreatedBase
from app.models.core.major_location import MajorLocation
from app.models.core.asset_type import AssetType
from app.models.core.make_model import MakeModel
from app.models.core.asset import Asset
from app.models.core.event import Event

def build_all_models(build_phase='all'):
    """
    Build all models in the correct dependency order
    
    Args:
        build_phase (str): Build phase to execute
            - 'none': Skip model building (data only)
            - 'phase1': Build only Phase 1 models (Core Foundation Tables)
            - 'phase2': Build Phase 1 and Phase 2 models (Core + Asset Detail Tables)
            - 'all': Build all phases (default)
    """
    if build_phase == 'none':
        print("=== Skipping Model Building ===")
        return True
    
    print("=== Building All Model Categories ===")
    
    try:
        # Phase 1A: Build core tables first
        print("Phase 1A: Building Core Tables")
        if not build_core_tables():
            print("✗ Core table build failed")
            return False
        
        # Verify core tables
        if not verify_core_tables():
            print("✗ Core table verification failed")
            return False
        
        # Show all table schemas
        show_table_schemas()
        
        if build_phase == 'phase1':
            print("\n=== Phase 1 Models Complete ===")
            print("✓ Core tables created")
            print("✓ All dependencies resolved")
            return True
        
        # Phase 2A: Build asset detail tables
        print("\nPhase 2A: Building Asset Detail Tables")
        
        # Import asset build functions only when needed
        from app.models.assets.build import build_asset_models, verify_asset_models, show_asset_table_schemas
        
        if not build_asset_models():
            print("✗ Asset detail table build failed")
            return False
        
        # Verify asset detail tables
        if not verify_asset_models():
            print("✗ Asset detail table verification failed")
            return False
        
        # Show asset detail table schemas
        show_asset_table_schemas()
        
        if build_phase == 'phase2':
            print("\n=== Phase 2 Models Complete ===")
            print("✓ Asset detail tables created")
            print("✓ All dependencies resolved")
            return True
        
        # Future phases would go here
        # Phase 3: Maintenance & Operations
        # Phase 4: Advanced Features
        
        print("\n=== All Models Built Successfully ===")
        print("✓ Core tables created")
        print("✓ Asset detail tables created")
        print("✓ All dependencies resolved")
        print("✓ Ready for data insertion")
        
        return True
        
    except Exception as e:
        print(f"\n=== Model Build FAILED ===")
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def insert_all_data(data_phase='all'):
    """
    Insert all data in the correct dependency order
    
    Args:
        data_phase (str): Data insertion phase to execute
            - 'phase1': Insert only Phase 1 data (Core System Initialization)
            - 'phase2': Insert Phase 1 and Phase 2 data (Core + Asset Detail Data)
            - 'all': Insert all phases data (default)
    """
    print("=== Inserting All Data ===")
    
    try:
        # Phase 1B: Initialize system data
        print("Phase 1B: Initializing System Data")
        if not initialize_system_data():
            print("✗ System initialization failed")
            return False
        
        if data_phase == 'phase1':
            print("\n=== Phase 1 Data Complete ===")
            print("✓ System data initialized")
            return True
        
        # Phase 2B: Initialize asset detail data
        print("\nPhase 2B: Initializing Asset Detail Data")
        
        # Import asset data functions only when needed
        from app.models.assets.build import initialize_asset_detail_data
        
        if not initialize_asset_detail_data():
            print("✗ Asset detail data initialization failed")
            return False
        
        if data_phase == 'phase2':
            print("\n=== Phase 2 Data Complete ===")
            print("✓ Asset detail data initialized")
            return True
        
        # Future phases would go here
        # Phase 3: Maintenance & Operations data
        # Phase 4: Advanced Features data
        
        print("\n=== All Data Inserted Successfully ===")
        print("✓ System data initialized")
        print("✓ Asset detail data initialized")
        print("✓ Ready for use")
        
        return True
        
    except Exception as e:
        print(f"\n=== Data Insertion FAILED ===")
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def verify_all_tables():
    """Verify all tables were created correctly"""
    print("\n=== Verifying All Tables ===")
    
    try:
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        
        # Expected tables for Phase 1
        expected_phase1_tables = ['users', 'major_locations', 'asset_types', 'make_models', 'assets', 'events']
        
        # Expected tables for Phase 2
        expected_phase2_tables = [
            'asset_type_detail_table_sets',
            'model_detail_table_sets',
            'purchase_info',
            'vehicle_registration',
            'toyota_warranty_receipt',
            'emissions_info',
            'model_info'
        ]
        
        print(f"Found {len(tables)} tables in database:")
        for table in tables:
            print(f"  - {table}")
        
        # Check Phase 1 tables
        print(f"\nPhase 1 Tables ({len(expected_phase1_tables)} expected):")
        phase1_missing = []
        for table in expected_phase1_tables:
            if table in tables:
                print(f"  ✓ {table}")
            else:
                print(f"  ✗ {table} (missing)")
                phase1_missing.append(table)
        
        # Check Phase 2 tables
        print(f"\nPhase 2 Tables ({len(expected_phase2_tables)} expected):")
        phase2_missing = []
        for table in expected_phase2_tables:
            if table in tables:
                print(f"  ✓ {table}")
            else:
                print(f"  ✗ {table} (missing)")
                phase2_missing.append(table)
        
        if phase1_missing or phase2_missing:
            print(f"\n✗ Missing tables found")
            return False
        
        print(f"\n✓ All {len(expected_phase1_tables) + len(expected_phase2_tables)} expected tables found")
        return True
        
    except Exception as e:
        print(f"✗ Verification failed: {e}")
        return False

def show_build_summary():
    """Show a summary of the build process"""
    print("\n=== Build Summary ===")
    
    try:
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        
        print(f"Total tables created: {len(tables)}")
        print("Tables by category:")
        
        # Core tables
        core_tables = ['users', 'major_locations', 'asset_types', 'make_models', 'assets', 'events']
        core_count = sum(1 for table in core_tables if table in tables)
        print(f"  - Core tables: {core_count}/{len(core_tables)}")
        
        # Asset detail tables
        asset_detail_tables = [
            'asset_type_detail_table_sets',
            'model_detail_table_sets',
            'purchase_info',
            'vehicle_registration',
            'toyota_warranty_receipt',
            'emissions_info',
            'model_info'
        ]
        asset_detail_count = sum(1 for table in asset_detail_tables if table in tables)
        print(f"  - Asset detail tables: {asset_detail_count}/{len(asset_detail_tables)}")
        
        # Future phases
        print("  - Maintenance tables: 0 (Phase 3)")
        print("  - Other tables: 0 (Future phases)")
        
        return True
        
    except Exception as e:
        print(f"Error showing summary: {e}")
        return False

if __name__ == '__main__':
    # This can be run directly for testing
    from app import create_app
    
    app = create_app()
    with app.app_context():
        success = build_all_models()
        if success:
            verify_all_tables()
            show_build_summary() 
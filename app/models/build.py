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
            - 'phase1': Build only Phase 1 (Core Foundation Tables and System Initialization)
            - 'phase2': Build Phase 1 and Phase 2 (Core + Asset Detail Tables)
            - 'all': Build all phases (default)
    """
    print("=== Building All Model Categories ===")
    
    try:
        # Phase 1A: Build core tables first
        print("Phase 1A: Building Core Tables")
        if not build_core_tables():
            print("✗ Core table build failed")
            return False
        
        # Phase 1B: Initialize system data
        print("Phase 1B: Initializing System Data")
        if not initialize_system_data():
            print("✗ System initialization failed")
            return False
        
        # Verify core tables
        if not verify_core_tables():
            print("✗ Core table verification failed")
            return False
        
        # Show all table schemas
        show_table_schemas()
        
        if build_phase == 'phase1':
            print("\n=== Phase 1 Complete ===")
            print("✓ Core tables created")
            print("✓ System data initialized")
            print("✓ All dependencies resolved")
            return True
        
        # Phase 2: Build asset detail tables
        print("\nPhase 2: Building Asset Detail Tables")
        
        # Import asset build functions only when needed
        from app.models.assets.build import build_asset_models, initialize_asset_detail_data, verify_asset_models, show_asset_table_schemas
        
        if not build_asset_models():
            print("✗ Asset detail table build failed")
            return False
        
        # Phase 2: Initialize asset detail data
        print("Phase 2: Initializing Asset Detail Data")
        if not initialize_asset_detail_data():
            print("✗ Asset detail data initialization failed")
            return False
        
        # Verify asset detail tables
        if not verify_asset_models():
            print("✗ Asset detail table verification failed")
            return False
        
        # Show asset detail table schemas
        show_asset_table_schemas()
        
        if build_phase == 'phase2':
            print("\n=== Phase 2 Complete ===")
            print("✓ Asset detail tables created")
            print("✓ Asset detail data initialized")
            print("✓ All dependencies resolved")
            return True
        
        # Future phases would go here
        # Phase 3: Maintenance & Operations
        # Phase 4: Advanced Features
        
        print("\n=== All Tables Built Successfully ===")
        print("✓ Core tables created")
        print("✓ System data initialized")
        print("✓ Asset detail tables created")
        print("✓ Asset detail data initialized")
        print("✓ All dependencies resolved")
        print("✓ Ready for data insertion")
        
        return True
        
    except Exception as e:
        print(f"\n=== Build FAILED ===")
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
        expected_tables = ['users', 'major_locations', 'asset_types', 'make_models', 'assets', 'events']
        
        print(f"Found {len(tables)} tables in database:")
        for table in tables:
            print(f"  - {table}")
        
        print(f"\nExpected {len(expected_tables)} tables:")
        for table in expected_tables:
            if table in tables:
                print(f"  ✓ {table}")
            else:
                print(f"  ✗ {table} (missing)")
                return False
        
        print(f"\n✓ All {len(expected_tables)} expected tables found")
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
        
        # Future phases
        print("  - Asset detail tables: 0 (Phase 2)")
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
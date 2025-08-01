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

def initialize_system_data():
    """Initialize system with required base data (Phase 1B)"""
    print("=== Initializing System Data ===")
    
    try:
        # Step 1: Create Admin User (if not exists)
        print("1. Creating Admin User...")
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(
                id=1,
                username='admin',
                email='admin@assetmanagement.local',
                is_active=True,
                is_system=False,
                is_admin=True
            )
            admin_user.set_password('admin-password-change-me')
            db.session.add(admin_user)
            db.session.commit()
            print("   ✓ Admin User created (ID: 1)")
        else:
            print("   ✓ Admin User already exists (ID: 1)")
        
        # Step 2: Create System User (if not exists)
        print("2. Creating System User...")
        system_user = User.query.filter_by(username='system').first()
        if not system_user:
            system_user = User(
                id=2,
                username='system',
                email='system@assetmanagement.local',
                is_active=True,
                is_system=True,
                is_admin=False
            )
            system_user.set_password('system-password-not-for-login')
            db.session.add(system_user)
            db.session.commit()
            print("   ✓ System User created (ID: 2)")
        else:
            print("   ✓ System User already exists (ID: 2)")
        
        # Step 3: Create Major Location (if not exists)
        print("3. Creating Major Location...")
        major_location = MajorLocation.query.filter_by(name="SanDiegoHQ").first()
        if not major_location:
            major_location = MajorLocation(
                name="SanDiegoHQ",
                description="Main office location",
                address="San Diego, CA",
                is_active=True,
                created_by_id=system_user.id,
                updated_by_id=system_user.id
            )
            db.session.add(major_location)
            db.session.commit()
            print("   ✓ Major Location 'SanDiegoHQ' created")
        else:
            print("   ✓ Major Location 'SanDiegoHQ' already exists")
        
        # Step 4: Create Asset Type (if not exists)
        print("4. Creating Asset Type...")
        asset_type = AssetType.query.filter_by(name="Vehicle").first()
        if not asset_type:
            asset_type = AssetType(
                name="Vehicle",
                category="Transportation",
                description="Motor vehicles for transportation",
                is_active=True,
                created_by_id=system_user.id,
                updated_by_id=system_user.id
            )
            db.session.add(asset_type)
            db.session.commit()
            print("   ✓ Asset Type 'Vehicle' created")
        else:
            print("   ✓ Asset Type 'Vehicle' already exists")
        
        # Step 5: Create Make/Model (if not exists)
        print("5. Creating Make/Model...")
        make_model = MakeModel.query.filter_by(make="Toyota", model="Corolla").first()
        if not make_model:
            make_model = MakeModel(
                make="Toyota",
                model="Corolla",
                year=2023,
                description="Toyota Corolla 2023 model",
                asset_type_id=asset_type.id,
                is_active=True,
                created_by_id=system_user.id,
                updated_by_id=system_user.id
            )
            db.session.add(make_model)
            db.session.commit()
            print("   ✓ Make/Model 'Toyota Corolla' created")
        else:
            print("   ✓ Make/Model 'Toyota Corolla' already exists")
        
        # Step 6: Create Asset (if not exists)
        print("6. Creating Asset...")
        asset = Asset.query.filter_by(serial_number="VTC0012023001").first()
        if not asset:
            asset = Asset(
                name="VTC-001",
                serial_number="VTC0012023001",
                status="Active",
                major_location_id=major_location.id,
                make_model_id=make_model.id,
                created_by_id=system_user.id,
                updated_by_id=system_user.id
            )
            db.session.add(asset)
            db.session.commit()
            print("   ✓ Asset 'VTC-001' created")
        else:
            print("   ✓ Asset 'VTC-001' already exists")
        
        # Step 7: Create Event (if not exists)
        print("7. Creating Event...")
        event = Event.query.filter_by(event_type="System", description="System initialized with core data").first()
        if not event:
            event = Event(
                event_type="System",
                description="System initialized with core data",
                user_id=system_user.id,
                asset_id=asset.id,
                major_location_id=major_location.id  # Explicitly set major location
            )
            db.session.add(event)
            db.session.commit()
            print("   ✓ Event 'System Initialization' created")
        else:
            print("   ✓ Event 'System Initialization' already exists")
        
        print("\n=== System Data Initialization Complete ===")
        return True
        
    except Exception as e:
        print(f"\n=== System Initialization FAILED ===")
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        db.session.rollback()
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
    
    app = create_app()
    with app.app_context():
        success = build_core_tables()
        if success:
            initialize_system_data()
            verify_core_tables()
            show_table_schemas() 
#!/usr/bin/env python3
"""
Build script for Phase 2 asset detail models
Creates detail table models in the correct dependency order
"""

from app import db

# Import all detail table models to ensure they're registered with SQLAlchemy
from app.models.assets.detail_table_sets.asset_type_detail_table_set import AssetTypeDetailTableSet
from app.models.assets.detail_table_sets.model_detail_table_set import ModelDetailTableSet
from app.models.assets.asset_details.purchase_info import PurchaseInfo
from app.models.assets.asset_details.vehicle_registration import VehicleRegistration
from app.models.assets.asset_details.toyota_warranty_receipt import ToyotaWarrantyReceipt
from app.models.assets.model_details.emissions_info import EmissionsInfo
from app.models.assets.model_details.model_info import ModelInfo

# Import data loader
from app.models.assets.init_data import AssetInitData

def build_asset_models():
    """Build all asset detail table models in dependency order (Phase 2A)"""
    print("=== Building Asset Detail Table Models ===")
    
    try:
        # Step 1: Create detail table set containers (depend on core models)
        print("1. Creating AssetTypeDetailTableSet table...")
        AssetTypeDetailTableSet.__table__.create(db.engine, checkfirst=True)
        print("   ✓ AssetTypeDetailTableSet table created")
        
        print("2. Creating ModelDetailTableSet table...")
        ModelDetailTableSet.__table__.create(db.engine, checkfirst=True)
        print("   ✓ ModelDetailTableSet table created")
        
        # Step 2: Create asset detail tables (depend on assets table)
        print("3. Creating PurchaseInfo table...")
        PurchaseInfo.__table__.create(db.engine, checkfirst=True)
        print("   ✓ PurchaseInfo table created")
        
        print("4. Creating VehicleRegistration table...")
        VehicleRegistration.__table__.create(db.engine, checkfirst=True)
        print("   ✓ VehicleRegistration table created")
        
        print("5. Creating ToyotaWarrantyReceipt table...")
        ToyotaWarrantyReceipt.__table__.create(db.engine, checkfirst=True)
        print("   ✓ ToyotaWarrantyReceipt table created")
        
        # Step 3: Create model detail tables (depend on make_models table)
        print("6. Creating EmissionsInfo table...")
        EmissionsInfo.__table__.create(db.engine, checkfirst=True)
        print("   ✓ EmissionsInfo table created")
        
        print("7. Creating ModelInfo table...")
        ModelInfo.__table__.create(db.engine, checkfirst=True)
        print("   ✓ ModelInfo table created")
        
        print("\n=== All Asset Detail Table Models Built Successfully ===")
        return True
        
    except Exception as e:
        print(f"\n=== Asset Detail Table Build FAILED ===")
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def initialize_asset_detail_data():
    """Initialize asset detail tables with sample data (Phase 2B)"""
    print("=== Initializing Asset Detail Data ===")
    
    try:
        # Load configuration data
        data_loader = AssetInitData()
        success = data_loader.load_asset_data()
        return success
    except Exception as e:
        print(f"Error initializing asset detail data: {e}")
        return False

def initialize_detail_table_sets():
    """Initialize only the detail table set configurations (Phase 3B step 1)"""
    print("=== Initializing Detail Table Set Configurations ===")
    
    try:
        # Load configuration data
        data_loader = AssetInitData()
        success = data_loader.initialize_detail_table_sets()
        return success
    except Exception as e:
        print(f"Error initializing detail table sets: {e}")
        return False

def update_auto_generated_details():
    """Update auto-generated asset detail data with actual data (Phase 3B)"""
    print("=== Updating Auto-Generated Asset Detail Data ===")
    
    try:
        # Load configuration data
        data_loader = AssetInitData()
        success = data_loader.update_auto_generated_details()
        return success
    except Exception as e:
        print(f"Error updating auto-generated asset detail data: {e}")
        return False

def verify_asset_models():
    """Verify all asset detail table models were created"""
    print("\n=== Verifying Asset Detail Table Models ===")
    
    try:
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        
        expected_tables = [
            'asset_type_detail_table_sets',
            'model_detail_table_sets',
            'purchase_info',
            'vehicle_registration',
            'toyota_warranty_receipt',
            'emissions_info',
            'model_info'
        ]
        
        for table in expected_tables:
            if table in tables:
                print(f"   ✓ Table '{table}' exists")
            else:
                print(f"   ✗ Table '{table}' missing")
                return False
        
        print(f"   ✓ All {len(expected_tables)} expected asset detail tables found")
        return True
        
    except Exception as e:
        print(f"   ✗ Verification failed: {e}")
        return False

def show_asset_table_schemas():
    """Show the schema of all created asset detail tables"""
    print("\n=== Asset Detail Table Schemas ===")
    
    try:
        inspector = db.inspect(db.engine)
        tables = [
            'asset_type_detail_table_sets',
            'model_detail_table_sets',
            'purchase_info',
            'vehicle_registration',
            'toyota_warranty_receipt',
            'emissions_info',
            'model_info'
        ]
        
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
            update_success = update_auto_generated_details()
            if update_success:
                print("Auto-generated asset detail data update completed successfully")
            else:
                print("Auto-generated asset detail data update failed")
        else:
            # Normal build and initialize mode
            success = build_asset_models()
            if success:
                data_success = initialize_asset_detail_data()
                if data_success:
                    verify_asset_models()
                    show_asset_table_schemas()
                else:
                    print("Asset detail data initialization failed")
            else:
                print("Asset model build failed")
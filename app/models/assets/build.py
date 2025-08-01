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
        from app.models.core.user import User
        from app.models.core.asset_type import AssetType
        from app.models.core.make_model import MakeModel
        from app.models.core.asset import Asset
        from datetime import date, datetime
        
        # Get system user for creating data
        system_user = User.query.filter_by(username='system').first()
        if not system_user:
            print("   ✗ System user not found!")
            return False
        
        # Get existing asset type and make/model
        vehicle_type = AssetType.query.filter_by(name='Vehicle').first()
        toyota_corolla = MakeModel.query.filter_by(make='Toyota', model='Corolla').first()
        vtc_001 = Asset.query.filter_by(serial_number='VTC0012023001').first()
        
        if not vehicle_type or not toyota_corolla or not vtc_001:
            print("   ✗ Required core data not found!")
            return False
        
        # Step 1: Create Asset Type Detail Table Sets
        print("1. Creating Asset Type Detail Table Sets...")
        
        # Purchase info for vehicles
        purchase_set = AssetTypeDetailTableSet.query.filter_by(
            asset_type_id=vehicle_type.id,
            detail_table_type='purchase_info'
        ).first()
        if not purchase_set:
            purchase_set = AssetTypeDetailTableSet(
                asset_type_id=vehicle_type.id,
                detail_table_type='purchase_info',
                is_asset_detail=True,
                is_active=True,
                created_by_id=system_user.id,
                updated_by_id=system_user.id
            )
            db.session.add(purchase_set)
            print("   ✓ Purchase info detail table set created")
        
        # Vehicle registration for vehicles
        registration_set = AssetTypeDetailTableSet.query.filter_by(
            asset_type_id=vehicle_type.id,
            detail_table_type='vehicle_registration'
        ).first()
        if not registration_set:
            registration_set = AssetTypeDetailTableSet(
                asset_type_id=vehicle_type.id,
                detail_table_type='vehicle_registration',
                is_asset_detail=True,
                is_active=True,
                created_by_id=system_user.id,
                updated_by_id=system_user.id
            )
            db.session.add(registration_set)
            print("   ✓ Vehicle registration detail table set created")
        
        # Emissions info for vehicles (model detail)
        emissions_set = AssetTypeDetailTableSet.query.filter_by(
            asset_type_id=vehicle_type.id,
            detail_table_type='emissions_info'
        ).first()
        if not emissions_set:
            emissions_set = AssetTypeDetailTableSet(
                asset_type_id=vehicle_type.id,
                detail_table_type='emissions_info',
                is_asset_detail=False,
                is_active=True,
                created_by_id=system_user.id,
                updated_by_id=system_user.id
            )
            db.session.add(emissions_set)
            print("   ✓ Emissions info detail table set created")
        
        # Model info for vehicles (model detail)
        model_info_set = AssetTypeDetailTableSet.query.filter_by(
            asset_type_id=vehicle_type.id,
            detail_table_type='model_info'
        ).first()
        if not model_info_set:
            model_info_set = AssetTypeDetailTableSet(
                asset_type_id=vehicle_type.id,
                detail_table_type='model_info',
                is_asset_detail=False,
                is_active=True,
                created_by_id=system_user.id,
                updated_by_id=system_user.id
            )
            db.session.add(model_info_set)
            print("   ✓ Model info detail table set created")
        
        db.session.commit()
        
        # Step 2: Create Model Detail Table Sets for Toyota Corolla
        print("2. Creating Model Detail Table Sets...")
        
        # Toyota warranty receipt for Toyota models
        toyota_warranty_set = ModelDetailTableSet.query.filter_by(
            make_model_id=toyota_corolla.id,
            detail_table_type='toyota_warranty_receipt'
        ).first()
        if not toyota_warranty_set:
            toyota_warranty_set = ModelDetailTableSet(
                make_model_id=toyota_corolla.id,
                detail_table_type='toyota_warranty_receipt',
                is_asset_detail=True,
                is_active=True,
                created_by_id=system_user.id,
                updated_by_id=system_user.id
            )
            db.session.add(toyota_warranty_set)
            print("   ✓ Toyota warranty receipt detail table set created")
        
        db.session.commit()
        
        # Step 3: Create sample detail table data
        print("3. Creating Sample Detail Table Data...")
        
        # Create purchase info for VTC-001
        purchase_info = PurchaseInfo.query.filter_by(asset_id=vtc_001.id).first()
        if not purchase_info:
            purchase_info = PurchaseInfo(
                asset_id=vtc_001.id,
                purchase_date=date(2023, 1, 15),
                purchase_price=25000.00,
                purchase_vendor="Toyota of San Diego",
                purchase_order_number="PO-2023-001",
                warranty_start_date=date(2023, 1, 15),
                warranty_end_date=date(2026, 1, 15),
                purchase_notes="Purchased for fleet use",
                created_by_id=system_user.id,
                updated_by_id=system_user.id
            )
            db.session.add(purchase_info)
            print("   ✓ Purchase info created for VTC-001")
        
        # Create vehicle registration for VTC-001
        vehicle_reg = VehicleRegistration.query.filter_by(asset_id=vtc_001.id).first()
        if not vehicle_reg:
            vehicle_reg = VehicleRegistration(
                asset_id=vtc_001.id,
                license_plate="ABC123",
                registration_number="REG-2023-001",
                registration_expiry=date(2024, 12, 31),
                vin_number="1HGBH41JXMN109186",
                state_registered="CA",
                registration_status="Active",
                insurance_provider="State Farm",
                insurance_policy_number="SF-123456",
                insurance_expiry=date(2024, 6, 30),
                created_by_id=system_user.id,
                updated_by_id=system_user.id
            )
            db.session.add(vehicle_reg)
            print("   ✓ Vehicle registration created for VTC-001")
        
        # Create Toyota warranty receipt for VTC-001
        toyota_warranty = ToyotaWarrantyReceipt.query.filter_by(asset_id=vtc_001.id).first()
        if not toyota_warranty:
            toyota_warranty = ToyotaWarrantyReceipt(
                asset_id=vtc_001.id,
                warranty_receipt_number="TOY-2023-001",
                warranty_type="Basic",
                warranty_mileage_limit=36000,
                warranty_time_limit_months=36,
                dealer_name="Toyota of San Diego",
                dealer_contact="John Smith",
                dealer_phone="(619) 555-0123",
                dealer_email="service@toyotasandiego.com",
                service_history="Initial inspection completed",
                warranty_claims="None",
                created_by_id=system_user.id,
                updated_by_id=system_user.id
            )
            db.session.add(toyota_warranty)
            print("   ✓ Toyota warranty receipt created for VTC-001")
        
        # Create emissions info for Toyota Corolla model
        emissions_info = EmissionsInfo.query.filter_by(make_model_id=toyota_corolla.id).first()
        if not emissions_info:
            emissions_info = EmissionsInfo(
                make_model_id=toyota_corolla.id,
                emissions_standard="EPA",
                emissions_rating="ULEV",
                fuel_type="gasoline",
                mpg_city=32.0,
                mpg_highway=41.0,
                mpg_combined=35.0,
                co2_emissions=250.0,
                emissions_test_date=date(2022, 12, 1),
                emissions_certification="EPA-2023-001",
                created_by_id=system_user.id,
                updated_by_id=system_user.id
            )
            db.session.add(emissions_info)
            print("   ✓ Emissions info created for Toyota Corolla")
        
        # Create model info for Toyota Corolla model
        model_info = ModelInfo.query.filter_by(make_model_id=toyota_corolla.id).first()
        if not model_info:
            model_info = ModelInfo(
                make_model_id=toyota_corolla.id,
                model_year=2023,
                body_style="sedan",
                engine_type="2.0L 4-Cylinder",
                engine_displacement="2.0L",
                transmission_type="automatic",
                drivetrain="FWD",
                seating_capacity=5,
                cargo_capacity=13.1,
                towing_capacity=1500,
                manufacturer_website="https://www.toyota.com/corolla",
                technical_specifications="2.0L Dynamic Force 4-Cylinder engine with 169 hp",
                created_by_id=system_user.id,
                updated_by_id=system_user.id
            )
            db.session.add(model_info)
            print("   ✓ Model info created for Toyota Corolla")
        
        db.session.commit()
        
        print("\n=== Asset Detail Data Initialization Complete ===")
        return True
        
    except Exception as e:
        print(f"\n=== Asset Detail Data Initialization FAILED ===")
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        db.session.rollback()
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
    
    app = create_app()
    with app.app_context():
        success = build_asset_models()
        if success:
            initialize_asset_detail_data()
            verify_asset_models()
            show_asset_table_schemas() 
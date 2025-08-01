#!/usr/bin/env python3
"""
Test script for Phase 3 functionality
"""

from app import create_app, db
from app.models.core.asset import Asset
from app.models.core.user import User
from app.models.core.make_model import MakeModel
from app.models.assets.asset_details.purchase_info import PurchaseInfo
from app.models.assets.asset_details.vehicle_registration import VehicleRegistration
from app.models.assets.asset_details.toyota_warranty_receipt import ToyotaWarrantyReceipt

def test_phase3_functionality():
    """Test Phase 3 automatic detail creation functionality"""
    
    app = create_app()
    with app.app_context():
        print("=== Phase 3 Functionality Test ===")
        
        # Build tables and initialize data first
        print("Building tables and initializing data...")
        from app.models.core.build import build_core_tables, initialize_system_data
        from app.models.assets.build import build_asset_models, initialize_asset_detail_data
        
        if not build_core_tables():
            print("   ✗ Failed to build core tables!")
            return False
        
        if not initialize_system_data():
            print("   ✗ Failed to initialize system data!")
            return False
        
        if not build_asset_models():
            print("   ✗ Failed to build asset models!")
            return False
        
        if not initialize_asset_detail_data():
            print("   ✗ Failed to initialize asset detail data!")
            return False
        
        print("   ✓ Tables built and data initialized\n")
        
        # Enable automatic detail insertion
        Asset.enable_automatic_detail_insertion()
        print(f"Automatic detail insertion enabled: {Asset._automatic_detail_insertion_enabled}")
        
        # Get system user and Toyota Corolla model
        system_user = User.query.filter_by(username='system').first()
        toyota_corolla = MakeModel.query.filter_by(make='Toyota', model='Corolla').first()
        
        if not system_user or not toyota_corolla:
            print("Required data not found!")
            return False
        
        # Create a new test asset to test automatic detail creation
        print("\nCreating new test asset...")
        new_asset = Asset(
            name='Phase 3 Test Asset',
            serial_number='PHASE3TEST001',
            make_model_id=toyota_corolla.id,
            created_by_id=system_user.id
        )
        
        db.session.add(new_asset)
        db.session.commit()
        
        print(f"New asset created with ID: {new_asset.id}")
        
        # Check for auto-generated detail rows
        purchase = PurchaseInfo.query.filter_by(asset_id=new_asset.id).first()
        reg = VehicleRegistration.query.filter_by(asset_id=new_asset.id).first()
        warranty = ToyotaWarrantyReceipt.query.filter_by(asset_id=new_asset.id).first()
        
        print(f"Purchase info auto-created: {purchase is not None}")
        print(f"Vehicle registration auto-created: {reg is not None}")
        print(f"Toyota warranty auto-created: {warranty is not None}")
        
        if purchase:
            print(f"Purchase info ID: {purchase.id}")
        if reg:
            print(f"Vehicle registration ID: {reg.id}")
        if warranty:
            print(f"Toyota warranty ID: {warranty.id}")
        
        # Check VTC-001 asset (should have updated data from Phase 3)
        vtc_asset = Asset.query.filter_by(serial_number='VTC0012023001').first()
        if vtc_asset:
            print(f"\nFound VTC-001 asset: {vtc_asset.name} (ID: {vtc_asset.id})")
            
            purchase = PurchaseInfo.query.filter_by(asset_id=vtc_asset.id).first()
            reg = VehicleRegistration.query.filter_by(asset_id=vtc_asset.id).first()
            warranty = ToyotaWarrantyReceipt.query.filter_by(asset_id=vtc_asset.id).first()
            
            print(f"Purchase info exists: {purchase is not None}")
            print(f"Vehicle registration exists: {reg is not None}")
            print(f"Toyota warranty exists: {warranty is not None}")
            
            if purchase and purchase.purchase_vendor:
                print(f"Purchase vendor: {purchase.purchase_vendor}")
            if reg and reg.license_plate:
                print(f"License plate: {reg.license_plate}")
            if warranty and warranty.warranty_type:
                print(f"Warranty type: {warranty.warranty_type}")
        
        print("\n=== Test Complete ===")

if __name__ == '__main__':
    test_phase3_functionality() 
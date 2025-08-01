#!/usr/bin/env python3
"""
Phase 2 Test Script
Tests the asset detail table system functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models.core.user import User
from app.models.core.asset_type import AssetType
from app.models.core.make_model import MakeModel
from app.models.core.asset import Asset
from app.models.assets.detail_table_sets.asset_type_detail_table_set import AssetTypeDetailTableSet
from app.models.assets.detail_table_sets.model_detail_table_set import ModelDetailTableSet
from app.models.assets.asset_details.purchase_info import PurchaseInfo
from app.models.assets.asset_details.vehicle_registration import VehicleRegistration
from app.models.assets.asset_details.toyota_warranty_receipt import ToyotaWarrantyReceipt
from app.models.assets.model_details.emissions_info import EmissionsInfo
from app.models.assets.model_details.model_info import ModelInfo

def test_phase2_functionality():
    """Test all Phase 2 functionality"""
    print("=== Phase 2 Functionality Test ===")
    
    app = create_app()
    
    with app.app_context():
        try:
            # Test 1: Verify core data exists
            print("\n1. Testing Core Data...")
            system_user = User.query.filter_by(username='system').first()
            vehicle_type = AssetType.query.filter_by(name='Vehicle').first()
            toyota_corolla = MakeModel.query.filter_by(make='Toyota', model='Corolla').first()
            vtc_001 = Asset.query.filter_by(serial_number='VTC0012023001').first()
            
            if not all([system_user, vehicle_type, toyota_corolla, vtc_001]):
                print("   ✗ Core data not found!")
                return False
            
            print("   ✓ Core data verified")
            
            # Test 2: Verify detail table sets
            print("\n2. Testing Detail Table Sets...")
            
            # Asset type detail table sets
            asset_type_sets = AssetTypeDetailTableSet.query.filter_by(asset_type_id=vehicle_type.id).all()
            if len(asset_type_sets) < 4:
                print("   ✗ Asset type detail table sets not found!")
                return False
            
            print(f"   ✓ Found {len(asset_type_sets)} asset type detail table sets")
            
            # Model detail table sets
            model_sets = ModelDetailTableSet.query.filter_by(make_model_id=toyota_corolla.id).all()
            if len(model_sets) < 1:
                print("   ✗ Model detail table sets not found!")
                return False
            
            print(f"   ✓ Found {len(model_sets)} model detail table sets")
            
            # Test 3: Verify asset detail tables
            print("\n3. Testing Asset Detail Tables...")
            
            # Purchase info
            purchase_info = PurchaseInfo.query.filter_by(asset_id=vtc_001.id).first()
            if not purchase_info:
                print("   ✗ Purchase info not found!")
                return False
            print(f"   ✓ Purchase info: {purchase_info.purchase_vendor}")
            
            # Vehicle registration
            vehicle_reg = VehicleRegistration.query.filter_by(asset_id=vtc_001.id).first()
            if not vehicle_reg:
                print("   ✗ Vehicle registration not found!")
                return False
            print(f"   ✓ Vehicle registration: {vehicle_reg.license_plate}")
            
            # Toyota warranty receipt
            toyota_warranty = ToyotaWarrantyReceipt.query.filter_by(asset_id=vtc_001.id).first()
            if not toyota_warranty:
                print("   ✗ Toyota warranty receipt not found!")
                return False
            print(f"   ✓ Toyota warranty: {toyota_warranty.warranty_receipt_number}")
            
            # Test 4: Verify model detail tables
            print("\n4. Testing Model Detail Tables...")
            
            # Emissions info
            emissions_info = EmissionsInfo.query.filter_by(make_model_id=toyota_corolla.id).first()
            if not emissions_info:
                print("   ✗ Emissions info not found!")
                return False
            print(f"   ✓ Emissions info: {emissions_info.emissions_standard}")
            
            # Model info
            model_info = ModelInfo.query.filter_by(make_model_id=toyota_corolla.id).first()
            if not model_info:
                print("   ✗ Model info not found!")
                return False
            print(f"   ✓ Model info: {model_info.body_style}")
            
            # Test 5: Test relationships
            print("\n5. Testing Relationships...")
            
            # Asset to detail tables
            asset_purchase_info = vtc_001.purchaseinfo_details
            if not asset_purchase_info:
                print("   ✗ Asset to purchase info relationship failed!")
                return False
            print("   ✓ Asset to purchase info relationship works")
            
            # Model to detail tables
            model_emissions_info = toyota_corolla.emissionsinfo_details
            if not model_emissions_info:
                print("   ✗ Model to emissions info relationship failed!")
                return False
            print("   ✓ Model to emissions info relationship works")
            
            # Test 6: Test detail table set configuration
            print("\n6. Testing Detail Table Set Configuration...")
            
            # Get asset detail types for vehicle
            asset_detail_types = AssetTypeDetailTableSet.get_asset_detail_types_for_asset_type(vehicle_type.id)
            if len(asset_detail_types) < 2:
                print("   ✗ Asset detail types configuration failed!")
                return False
            print(f"   ✓ Found {len(asset_detail_types)} asset detail types for vehicles")
            
            # Get model detail types for vehicle
            model_detail_types = AssetTypeDetailTableSet.get_model_detail_types_for_asset_type(vehicle_type.id)
            if len(model_detail_types) < 2:
                print("   ✗ Model detail types configuration failed!")
                return False
            print(f"   ✓ Found {len(model_detail_types)} model detail types for vehicles")
            
            # Test 7: Test audit trail
            print("\n7. Testing Audit Trail...")
            
            # Check created_by relationships
            if purchase_info.created_by.username != 'system':
                print("   ✗ Purchase info audit trail failed!")
                return False
            print("   ✓ Purchase info audit trail works")
            
            if emissions_info.created_by.username != 'system':
                print("   ✗ Emissions info audit trail failed!")
                return False
            print("   ✓ Emissions info audit trail works")
            
            # Test 8: Test detail table type identification
            print("\n8. Testing Detail Table Type Identification...")
            
            # Test asset detail identification
            if not PurchaseInfo.is_asset_detail():
                print("   ✗ PurchaseInfo asset detail identification failed!")
                return False
            print("   ✓ PurchaseInfo correctly identified as asset detail")
            
            if PurchaseInfo.is_model_detail():
                print("   ✗ PurchaseInfo model detail identification failed!")
                return False
            print("   ✓ PurchaseInfo correctly identified as not model detail")
            
            # Test model detail identification
            if not EmissionsInfo.is_model_detail():
                print("   ✗ EmissionsInfo model detail identification failed!")
                return False
            print("   ✓ EmissionsInfo correctly identified as model detail")
            
            if EmissionsInfo.is_asset_detail():
                print("   ✗ EmissionsInfo asset detail identification failed!")
                return False
            print("   ✓ EmissionsInfo correctly identified as not asset detail")
            
            print("\n=== All Phase 2 Tests Passed! ===")
            return True
            
        except Exception as e:
            print(f"\n=== Phase 2 Test Failed ===")
            print(f"Error: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

def test_detail_table_queries():
    """Test detail table query operations"""
    print("\n=== Detail Table Query Tests ===")
    
    app = create_app()
    
    with app.app_context():
        try:
            # Test 1: Query assets with their detail information
            print("\n1. Testing Asset Detail Queries...")
            
            assets_with_purchase_info = db.session.query(Asset, PurchaseInfo).join(
                PurchaseInfo, Asset.id == PurchaseInfo.asset_id
            ).all()
            
            if len(assets_with_purchase_info) < 1:
                print("   ✗ Asset with purchase info query failed!")
                return False
            print(f"   ✓ Found {len(assets_with_purchase_info)} assets with purchase info")
            
            # Test 2: Query models with their detail information
            print("\n2. Testing Model Detail Queries...")
            
            models_with_emissions = db.session.query(MakeModel, EmissionsInfo).join(
                EmissionsInfo, MakeModel.id == EmissionsInfo.make_model_id
            ).all()
            
            if len(models_with_emissions) < 1:
                print("   ✗ Model with emissions info query failed!")
                return False
            print(f"   ✓ Found {len(models_with_emissions)} models with emissions info")
            
            # Test 3: Query detail table sets
            print("\n3. Testing Detail Table Set Queries...")
            
            vehicle_detail_sets = AssetTypeDetailTableSet.query.filter_by(
                asset_type_id=AssetType.query.filter_by(name='Vehicle').first().id
            ).all()
            
            if len(vehicle_detail_sets) < 4:
                print("   ✗ Vehicle detail table sets query failed!")
                return False
            print(f"   ✓ Found {len(vehicle_detail_sets)} vehicle detail table sets")
            
            print("\n=== All Detail Table Query Tests Passed! ===")
            return True
            
        except Exception as e:
            print(f"\n=== Detail Table Query Tests Failed ===")
            print(f"Error: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    print("Phase 2 Test Script")
    print("==================")
    
    # Run functionality tests
    success1 = test_phase2_functionality()
    
    # Run query tests
    success2 = test_detail_table_queries()
    
    if success1 and success2:
        print("\n🎉 All Phase 2 tests passed successfully!")
        print("✅ Detail table system is working correctly")
        print("✅ All relationships are properly established")
        print("✅ Audit trail functionality is working")
        print("✅ Query operations are functioning")
    else:
        print("\n❌ Some Phase 2 tests failed")
        print("Please check the error messages above") 
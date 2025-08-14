#!/usr/bin/env python3
"""
Test script for master table implementation
Verifies that the all_asset_details and all_model_details tables work correctly
"""

import sys
from pathlib import Path

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from app import create_app, db
from app.models.assets.all_details import AllAssetDetail, AllModelDetail
from app.models.assets.master_table_utils import (
    get_all_asset_details, 
    get_all_model_details,
    get_detail_table_summary
)
from app.models.core.asset import Asset
from app.models.core.make_model import MakeModel
from app.models.core.user import User

def test_master_tables():
    """Test the master table functionality"""
    app = create_app()
    
    with app.app_context():
        print("Testing master table implementation...")
        
        # Get test data
        assets = Asset.query.limit(2).all()
        make_models = MakeModel.query.limit(2).all()
        users = User.query.limit(1).all()
        
        if not assets or not make_models or not users:
            print("Need test data: assets, make_models, and users")
            return
        
        test_asset = assets[0]
        test_model = make_models[0]
        test_user = users[0]
        
        print(f"Testing with asset: {test_asset.name}")
        print(f"Testing with model: {test_model.name}")
        
        # Test 1: Check existing master records
        print("\n1. Checking existing master records...")
        
        asset_master_records = AllAssetDetail.query.filter_by(asset_id=test_asset.id).all()
        print(f"Found {len(asset_master_records)} asset detail master records")
        
        model_master_records = AllModelDetail.query.filter_by(make_model_id=test_model.id).all()
        print(f"Found {len(model_master_records)} model detail master records")
        
        # Test 2: Test utility functions
        print("\n2. Testing utility functions...")
        
        asset_details = get_all_asset_details(test_asset.id)
        print(f"get_all_asset_details returned {len(asset_details)} records")
        
        model_details = get_all_model_details(test_model.id)
        print(f"get_all_model_details returned {len(model_details)} records")
        
        # Test 3: Test summary function
        print("\n3. Testing summary function...")
        
        asset_summary = get_detail_table_summary(asset_id=test_asset.id)
        print(f"Asset detail summary: {asset_summary}")
        
        model_summary = get_detail_table_summary(make_model_id=test_model.id)
        print(f"Model detail summary: {model_summary}")
        
        # Test 4: Test master table queries
        print("\n4. Testing master table queries...")
        
        # Get all purchase_info records for the asset
        purchase_master_records = AllAssetDetail.query.filter_by(
            asset_id=test_asset.id,
            table_name='purchase_info'
        ).all()
        print(f"Found {len(purchase_master_records)} purchase_info master records")
        
        # Get all model_info records for the model
        model_info_master_records = AllModelDetail.query.filter_by(
            make_model_id=test_model.id,
            table_name='model_info'
        ).all()
        print(f"Found {len(model_info_master_records)} model_info master records")
        
        # Test 5: Test relationship access
        print("\n5. Testing relationship access...")
        
        # Test asset relationship
        asset_with_details = Asset.query.get(test_asset.id)
        if hasattr(asset_with_details, 'all_detail_records'):
            print(f"Asset has {len(asset_with_details.all_detail_records)} detail records")
        else:
            print("Asset does not have all_detail_records relationship")
        
        # Test model relationship
        model_with_details = MakeModel.query.get(test_model.id)
        if hasattr(model_with_details, 'all_detail_records'):
            print(f"Model has {len(model_with_details.all_detail_records)} detail records")
        else:
            print("Model does not have all_detail_records relationship")
        
        print("\nMaster table test completed!")

def test_detail_record_creation():
    """Test creating new detail records to verify automatic master table insertion"""
    app = create_app()
    
    with app.app_context():
        print("\nTesting detail record creation...")
        
        # Get test data
        assets = Asset.query.limit(1).all()
        make_models = MakeModel.query.limit(1).all()
        users = User.query.limit(1).all()
        
        if not assets or not make_models or not users:
            print("Need test data for creation test")
            return
        
        test_asset = assets[0]
        test_model = make_models[0]
        test_user = users[0]
        
        # Test creating a new asset detail record
        try:
            from app.models.assets.asset_details.purchase_info import PurchaseInfo
            
            # Create a test purchase info record
            purchase_info = PurchaseInfo(
                asset_id=test_asset.id,
                purchase_date='2024-01-15',
                purchase_price=25000.00,
                purchase_vendor='Test Vendor',
                created_by_id=test_user.id,
                updated_by_id=test_user.id
            )
            
            db.session.add(purchase_info)
            db.session.commit()
            
            print(f"Created purchase_info record with ID: {purchase_info.id}")
            
            # Check if it was automatically added to master table
            master_record = AllAssetDetail.query.filter_by(
                table_name='purchase_info',
                row_id=purchase_info.id
            ).first()
            
            if master_record:
                print(f"✓ Master record created automatically: {master_record}")
            else:
                print("✗ Master record was not created automatically")
            
            # Clean up
            db.session.delete(purchase_info)
            db.session.commit()
            print("Test record cleaned up")
            
        except Exception as e:
            print(f"Error testing detail record creation: {e}")
            db.session.rollback()

if __name__ == '__main__':
    test_master_tables()
    test_detail_record_creation()

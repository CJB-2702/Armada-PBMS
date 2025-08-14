#!/usr/bin/env python3
"""
Test script for asset and model detail virtual classes
"""

import sys
from pathlib import Path

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from app import create_app, db

def test_detail_virtual_classes():
    """Test the detail virtual classes"""
    app = create_app()
    
    with app.app_context():
        print("Testing detail virtual classes...")
        
        # Test importing the virtual classes
        try:
            from app.models.assets.asset_detail_virtual import AssetDetailVirtual
            from app.models.assets.model_detail_virtual import ModelDetailVirtual
            print("✓ Successfully imported virtual classes")
        except Exception as e:
            print(f"✗ Error importing virtual classes: {e}")
            return
        
        # Test importing concrete detail classes
        try:
            from app.models.assets.asset_details.purchase_info import PurchaseInfo
            from app.models.assets.model_details.model_info import ModelInfo
            print("✓ Successfully imported concrete detail classes")
        except Exception as e:
            print(f"✗ Error importing concrete detail classes: {e}")
            return
        
        # Test creating instances (this should work without the automatic insertion)
        try:
            # Get a test asset and model
            from app.models.core.asset import Asset
            from app.models.core.make_model import MakeModel
            from app.models.core.user import User
            
            test_asset = Asset.query.first()
            test_model = MakeModel.query.first()
            test_user = User.query.first()
            
            if not test_asset or not test_model or not test_user:
                print("✗ Need test data: assets, make_models, and users")
                return
            
            print(f"✓ Using test asset: {test_asset.name}")
            print(f"✓ Using test model: {test_model.make} {test_model.model}")
            
            # Test creating a purchase info instance
            purchase_info = PurchaseInfo(
                asset_id=test_asset.id,
                purchase_date='2024-01-15',
                purchase_price=25000.00,
                purchase_vendor='Test Vendor',
                created_by_id=test_user.id,
                updated_by_id=test_user.id
            )
            print("✓ Successfully created PurchaseInfo instance")
            
            # Test creating a model info instance
            model_info = ModelInfo(
                make_model_id=test_model.id,
                model_year=2024,
                body_style='sedan',
                engine_type='gasoline',
                created_by_id=test_user.id,
                updated_by_id=test_user.id
            )
            print("✓ Successfully created ModelInfo instance")
            
        except Exception as e:
            print(f"✗ Error creating instances: {e}")
            return
        
        print("✓ All detail virtual class tests passed!")

if __name__ == '__main__':
    test_detail_virtual_classes()

#!/usr/bin/env python3
"""
Simple test script to build master table models without data insertion
"""

import sys
from pathlib import Path

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from app import create_app, db

def test_model_build():
    """Test building just the master table models"""
    app = create_app()
    
    with app.app_context():
        print("Testing master table model build...")
        
        # Import the master table models
        try:
            from app.models.assets.all_details import AllAssetDetail, AllModelDetail
            print("✓ Successfully imported AllAssetDetail and AllModelDetail")
        except Exception as e:
            print(f"✗ Error importing master table models: {e}")
            return
        
        # Check if models are properly mapped
        try:
            # Try to query the tables to see if they're mapped
            asset_count = AllAssetDetail.query.count()
            model_count = AllModelDetail.query.count()
            print(f"✓ Models are properly mapped. Asset details: {asset_count}, Model details: {model_count}")
        except Exception as e:
            print(f"✗ Error querying models: {e}")
            return
        
        # Test creating instances
        try:
            # Test creating an AllAssetDetail instance
            test_asset_detail = AllAssetDetail(
                table_name='test_table',
                row_id=1,
                asset_id=1
            )
            print("✓ Successfully created AllAssetDetail instance")
            
            # Test creating an AllModelDetail instance
            test_model_detail = AllModelDetail(
                table_name='test_table',
                row_id=1,
                make_model_id=1
            )
            print("✓ Successfully created AllModelDetail instance")
            
        except Exception as e:
            print(f"✗ Error creating instances: {e}")
            return
        
        print("✓ All model build tests passed!")

if __name__ == '__main__':
    test_model_build()

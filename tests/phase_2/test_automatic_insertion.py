#!/usr/bin/env python3
"""
Test script for automatic master table insertion
"""

import sys
from pathlib import Path

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from app import create_app, db
from datetime import date

def test_automatic_insertion():
    """Test the automatic master table insertion functionality"""
    app = create_app()
    
    with app.app_context():
        logger.debug("Testing automatic master table insertion...")
        
        # Get test data
        from app.models.core.asset import Asset
        from app.models.core.make_model import MakeModel
        from app.models.core.user import User
        from app.models.assets.all_details import AllAssetDetail, AllModelDetail
        
        test_asset = Asset.query.first()
        test_model = MakeModel.query.first()
        test_user = User.query.first()
        
        if not test_asset or not test_model or not test_user:
            logger.debug("✗ Need test data: assets, make_models, and users")
            return
        
        logger.debug(f"✓ Using test asset: {test_asset.name}")
        logger.debug(f"✓ Using test model: {test_model.make} {test_model.model}")
        
        # Check initial state
        initial_asset_details = AllAssetDetail.query.count()
        initial_model_details = AllModelDetail.query.count()
        logger.debug(f"✓ Initial state - Asset details: {initial_asset_details}, Model details: {initial_model_details}")
        
        try:
            # Test creating and saving a purchase info instance
            from app.models.assets.asset_details.purchase_info import PurchaseInfo
            
            purchase_info = PurchaseInfo(
                asset_id=test_asset.id,
                purchase_date=date(2024, 1, 15),
                purchase_price=25000.00,
                purchase_vendor='Test Vendor',
                created_by_id=test_user.id,
                updated_by_id=test_user.id
            )
            
            db.session.add(purchase_info)
            db.session.commit()
            
            # Update the row_id in the master table
            purchase_info.update_row_id()
            
            logger.debug(f"✓ Created purchase_info record with ID: {purchase_info.id}")
            
            # Check if it was automatically added to master table
            master_record = AllAssetDetail.query.filter_by(
                table_name='purchase_info',
                row_id=purchase_info.id
            ).first()
            
            if master_record:
                logger.debug(f"✓ Master record created automatically: {master_record}")
            else:
                logger.debug("✗ Master record was not created automatically")
            
            # Test creating and saving a model info instance
            from app.models.assets.model_details.model_info import ModelInfo
            
            model_info = ModelInfo(
                make_model_id=test_model.id,
                model_year=2024,
                body_style='sedan',
                engine_type='gasoline',
                created_by_id=test_user.id,
                updated_by_id=test_user.id
            )
            
            db.session.add(model_info)
            db.session.commit()
            
            # Update the row_id in the master table
            model_info.update_row_id()
            
            logger.debug(f"✓ Created model_info record with ID: {model_info.id}")
            
            # Check if it was automatically added to master table
            model_master_record = AllModelDetail.query.filter_by(
                table_name='model_info',
                row_id=model_info.id
            ).first()
            
            if model_master_record:
                logger.debug(f"✓ Model master record created automatically: {model_master_record}")
            else:
                logger.debug("✗ Model master record was not created automatically")
            
            # Check final state
            final_asset_details = AllAssetDetail.query.count()
            final_model_details = AllModelDetail.query.count()
            logger.debug(f"✓ Final state - Asset details: {final_asset_details}, Model details: {final_model_details}")
            
            # Clean up
            db.session.delete(purchase_info)
            db.session.delete(model_info)
            db.session.commit()
            logger.debug("✓ Test records cleaned up")
            
        except Exception as e:
            logger.debug(f"✗ Error during automatic insertion test: {e}")
            db.session.rollback()
            return
        
        logger.debug("✓ Automatic insertion test completed!")

if __name__ == '__main__':
    test_automatic_insertion()

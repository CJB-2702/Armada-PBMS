#!/usr/bin/env python3
"""
Test script to verify asset_type_id property fixes for after_insert event listeners
"""

from app import create_app, db
from app.models.core.asset import Asset
from app.models.core.make_model import MakeModel
from app.models.core.asset_type import AssetType
from app.models.core.user import User
from app.models.core.major_location import MajorLocation
from app.logger import get_logger

logger = get_logger("test_asset_type_id_fix")

def test_asset_type_id_in_event_listener():
    """Test that asset_type_id works correctly in after_insert event listeners"""
    app = create_app()
    
    with app.app_context():
        logger.info("Testing Asset Type ID in Event Listener Context")
        logger.info("=" * 50)
        
        # Get or create required data
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            logger.error("❌ Admin user not found")
            return False
        
        # Get or create asset type
        vehicle_type = AssetType.query.filter_by(name='Vehicle').first()
        if not vehicle_type:
            vehicle_type = AssetType(
                name='Vehicle',
                description='General vehicle type',
                created_by_id=admin_user.id,
                updated_by_id=admin_user.id
            )
            db.session.add(vehicle_type)
            db.session.flush()
            logger.info(f"✓ Created vehicle asset type: {vehicle_type.id}")
        
        # Get or create location
        test_location = MajorLocation.query.first()
        if not test_location:
            test_location = MajorLocation(
                name='Test Location',
                description='Test location for asset type ID testing',
                address='123 Test St, Test City, TS 12345',
                created_by_id=admin_user.id,
                updated_by_id=admin_user.id
            )
            db.session.add(test_location)
            db.session.flush()
            logger.info(f"✓ Created test location: {test_location.id}")
        
        # Get or create make/model
        test_model = MakeModel.query.filter_by(make='Toyota', model='Camry').first()
        if not test_model:
            test_model = MakeModel(
                make='Toyota',
                model='Camry',
                year=2024,
                asset_type_id=vehicle_type.id,
                created_by_id=admin_user.id,
                updated_by_id=admin_user.id
            )
            db.session.add(test_model)
            db.session.flush()
            logger.info(f"✓ Created test make/model: {test_model.id} with asset_type_id: {test_model.asset_type_id}")
        
        # Test 1: Verify the property works normally
        logger.info("\n1. Testing asset_type_id property in normal context...")
        test_asset = Asset(
            name='Test Asset for Type ID',
            serial_number='TEST_TYPE_ID_001',
            make_model_id=test_model.id,
            major_location_id=test_location.id,
            created_by_id=admin_user.id,
            updated_by_id=admin_user.id
        )
        
        # Test property before commit
        logger.info(f"   Asset make_model_id: {test_asset.make_model_id}")
        logger.info(f"   Asset asset_type_id (property): {test_asset.asset_type_id}")
        logger.info(f"   Asset asset_type_id (method): {test_asset.get_asset_type_id()}")
        
        # Test 2: Test in event listener context
        logger.info("\n2. Testing asset_type_id in event listener context...")
        
        # Enable automatic detail insertion to trigger event listeners
        Asset.enable_automatic_detail_insertion()
        
        # Add and commit the asset (this will trigger after_insert)
        db.session.add(test_asset)
        db.session.commit()
        
        logger.info(f"   ✓ Asset created with ID: {test_asset.id}")
        logger.info(f"   ✓ Asset make_model_id: {test_asset.make_model_id}")
        logger.info(f"   ✓ Asset asset_type_id (property): {test_asset.asset_type_id}")
        logger.info(f"   ✓ Asset asset_type_id (method): {test_asset.get_asset_type_id()}")
        
        # Test 3: Verify the asset type ID is correct
        expected_asset_type_id = vehicle_type.id
        actual_asset_type_id = test_asset.asset_type_id
        method_asset_type_id = test_asset.get_asset_type_id()
        
        logger.info(f"\n3. Verification:")
        logger.info(f"   Expected asset_type_id: {expected_asset_type_id}")
        logger.info(f"   Actual asset_type_id (property): {actual_asset_type_id}")
        logger.info(f"   Actual asset_type_id (method): {method_asset_type_id}")
        
        if actual_asset_type_id == expected_asset_type_id:
            logger.info("   ✓ Property returns correct asset_type_id")
        else:
            logger.error("   ✗ Property returns incorrect asset_type_id")
            return False
        
        if method_asset_type_id == expected_asset_type_id:
            logger.info("   ✓ Method returns correct asset_type_id")
        else:
            logger.error("   ✗ Method returns incorrect asset_type_id")
            return False
        
        logger.info("\n✓ All tests passed! Asset type ID works correctly in event listener contexts.")
        return True

if __name__ == "__main__":
    test_asset_type_id_in_event_listener()

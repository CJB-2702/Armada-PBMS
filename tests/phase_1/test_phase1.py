#!/usr/bin/env python3
"""
Test script for Phase 1 implementation
Verifies all models and initial data are working correctly
"""

import sys
from pathlib import Path
# Add the parent directory to the Python path so we can import the app module
sys.path.insert(0, str(Path(__file__).parent.parent))

from app import create_app, db
from app.models.core.user import User
from app.models.core.major_location import MajorLocation
from app.models.core.asset_type import AssetType
from app.models.core.make_model import MakeModel
from app.models.core.asset import Asset
from app.models.core.event import Event

def test_phase1_implementation():
    """Test the Phase 1 implementation"""
    app = create_app()
    
    with app.app_context():
        logger.debug("=== Phase 1 Implementation Test ===\n")
        
        # Build tables and initialize data first
        logger.debug("Building tables and initializing data...")
        from app.models.core.build import build_core_tables, initialize_system_data
        
        if not build_core_tables():
            logger.debug("   ✗ Failed to build core tables!")
            return False
        
        if not initialize_system_data():
            logger.debug("   ✗ Failed to initialize system data!")
            return False
        
        logger.debug("   ✓ Tables built and data initialized\n")
        
        # Test 1: Verify Admin User
        logger.debug("1. Testing Admin User...")
        admin_user = User.query.filter_by(id=1).first()
        if admin_user:
            logger.debug(f"   ✓ Admin User found: {admin_user.username} (ID: {admin_user.id})")
            logger.debug(f"   ✓ Is system: {admin_user.is_system}")
            logger.debug(f"   ✓ Is admin: {admin_user.is_admin}")
        else:
            logger.debug("   ✗ Admin User not found!")
            return False
        
        # Test 2: Verify System User
        logger.debug("\n2. Testing System User...")
        system_user = User.query.filter_by(id=0).first()
        if system_user:
            logger.debug(f"   ✓ System User found: {system_user.username} (ID: {system_user.id})")
            logger.debug(f"   ✓ Is system: {system_user.is_system}")
            logger.debug(f"   ✓ Is admin: {system_user.is_admin}")
        else:
            logger.debug("   ✗ System User not found!")
            return False
        
        # Test 3: Verify Major Location
        logger.debug("\n3. Testing Major Location...")
        san_diego = MajorLocation.query.filter_by(name='SanDiegoHQ').first()
        if san_diego:
            logger.debug(f"   ✓ Major Location found: {san_diego.name}")
            logger.debug(f"   ✓ Description: {san_diego.description}")
            logger.debug(f"   ✓ Created by: {san_diego.created_by.username}")
        else:
            logger.debug("   ✗ Major Location not found!")
            return False
        
        # Test 4: Verify Asset Type
        logger.debug("\n4. Testing Asset Type...")
        vehicle_type = AssetType.query.filter_by(name='Vehicle').first()
        if vehicle_type:
            logger.debug(f"   ✓ Asset Type found: {vehicle_type.name}")
            logger.debug(f"   ✓ Category: {vehicle_type.category}")
            logger.debug(f"   ✓ Created by: {vehicle_type.created_by.username}")
        else:
            logger.debug("   ✗ Asset Type not found!")
            return False
        
        # Test 5: Verify Make/Model
        logger.debug("\n5. Testing Make/Model...")
        toyota = MakeModel.query.filter_by(make='Toyota', model='Corolla').first()
        if toyota:
            logger.debug(f"   ✓ Make/Model found: {toyota.make} {toyota.model}")
            logger.debug(f"   ✓ Year: {toyota.year}")
            logger.debug(f"   ✓ Created by: {toyota.created_by.username}")
        else:
            logger.debug("   ✗ Make/Model not found!")
            return False
        
        # Test 6: Verify Asset
        logger.debug("\n6. Testing Asset...")
        vtc_001 = Asset.query.filter_by(serial_number='VTC0012023001').first()
        if vtc_001:
            logger.debug(f"   ✓ Asset found: {vtc_001.name}")
            logger.debug(f"   ✓ Serial Number: {vtc_001.serial_number}")
            logger.debug(f"   ✓ Status: {vtc_001.status}")
            logger.debug(f"   ✓ Location: {vtc_001.major_location.name}")
            logger.debug(f"   ✓ Type: {vtc_001.asset_type.name}")
            logger.debug(f"   ✓ Make/Model: {vtc_001.make_model.make} {vtc_001.make_model.model}")
            logger.debug(f"   ✓ Created by: {vtc_001.created_by.username}")
        else:
            logger.debug("   ✗ Asset not found!")
            return False
        
        # Test 7: Verify Event
        logger.debug("\n7. Testing Event...")
        event = Event.query.filter_by(description='System initialized with core data').first()
        if event:
            logger.debug(f"   ✓ Event found: {event.event_type}")
            logger.debug(f"   ✓ Description: {event.description}")
            logger.debug(f"   ✓ User: {event.user.username}")
            logger.debug(f"   ✓ Asset: {event.asset.name if event.asset else 'None'}")
        else:
            logger.debug("   ✗ Event not found!")
            return False
        
        # Test 8: Test relationships
        logger.debug("\n8. Testing Relationships...")
        assets_at_location = san_diego.assets
        logger.debug(f"   ✓ Assets at SanDiegoHQ: {len(assets_at_location)}")
        for asset in assets_at_location:
            logger.debug(f"      - {asset.name} ({asset.serial_number})")
        
        # Test 9: Test audit trail
        logger.debug("\n9. Testing Audit Trail...")
        logger.debug(f"   ✓ Asset created at: {vtc_001.created_at}")
        logger.debug(f"   ✓ Asset created by: {vtc_001.created_by.username}")
        logger.debug(f"   ✓ Asset updated at: {vtc_001.updated_at}")
        logger.debug(f"   ✓ Asset updated by: {vtc_001.updated_by.username}")
        
        logger.debug("\n=== All Tests Passed! Phase 1 Implementation Successful ===")
        return True

if __name__ == '__main__':
    test_phase1_implementation() 
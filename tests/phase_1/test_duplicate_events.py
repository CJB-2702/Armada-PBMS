#!/usr/bin/env python3
"""
Test script to check for duplicate events when creating assets
"""

from app import create_app, db
from app.models.core.asset import Asset
from app.models.core.event import Event
from app.models.core.user import User
from app.models.core.major_location import MajorLocation
from app.models.core.make_model import MakeModel
import time

def test_duplicate_events():
    """Test for duplicate events when creating assets"""
    app = create_app()
    
    with app.app_context():
        print("Testing for Duplicate Events")
        print("=" * 50)
        
        # Get existing data
        admin_user = User.query.filter_by(username='admin').first()
        location = MajorLocation.query.first()
        make_model = MakeModel.query.first()
        
        if not all([admin_user, location, make_model]):
            print("❌ Missing required data for test")
            return False
        
        print(f"✓ Found admin user: {admin_user.username}")
        print(f"✓ Found location: {location.name}")
        print(f"✓ Found make/model: {make_model.make} {make_model.model}")
        
        # Count events before creating asset
        events_before = Event.query.count()
        print(f"Events before asset creation: {events_before}")
        
        # List all events before
        print("\nEvents before asset creation:")
        for event in Event.query.all():
            print(f"  - {event}")
        
        # Create a new asset with unique serial number
        timestamp = int(time.time())
        serial_number = f"TEST{timestamp}"
        
        print(f"\nCreating new asset with serial number: {serial_number}")
        
        new_asset = Asset(
            name="Test Asset",
            serial_number=serial_number,
            status="Active",
            major_location_id=location.id,
            make_model_id=make_model.id,
            created_by_id=admin_user.id,
            updated_by_id=admin_user.id
        )
        
        # Enable automatic detail insertion (which includes event creation)
        Asset.enable_automatic_detail_insertion()
        
        # Add and commit the asset
        db.session.add(new_asset)
        db.session.commit()
        
        print(f"✓ Asset created with ID: {new_asset.id}")
        
        # Check events after creating asset
        events_after = Event.query.count()
        print(f"Events after asset creation: {events_after}")
        
        # List all events after
        print("\nEvents after asset creation:")
        for event in Event.query.all():
            print(f"  - {event}")
        
        # Check for duplicate events
        asset_creation_events = Event.query.filter_by(
            event_type='Asset Created',
            asset_id=new_asset.id
        ).all()
        
        print(f"\nAsset creation events for asset {new_asset.id}: {len(asset_creation_events)}")
        for event in asset_creation_events:
            print(f"  - {event}")
        
        if len(asset_creation_events) > 1:
            print(f"❌ DUPLICATE EVENTS DETECTED! Found {len(asset_creation_events)} events")
            return False
        elif len(asset_creation_events) == 1:
            print(f"✓ Single event created successfully")
            return True
        else:
            print(f"❌ No asset creation event found")
            return False

if __name__ == "__main__":
    try:
        success = test_duplicate_events()
        if success:
            print("\n" + "=" * 50)
            print("✓ No duplicate events detected!")
        else:
            print("\n" + "=" * 50)
            print("❌ Duplicate events detected!")
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc() 
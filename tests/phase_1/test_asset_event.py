#!/usr/bin/env python3
"""
Test script to verify asset creation event functionality
"""

from app import create_app, db
from app.models.core.asset import Asset
from app.models.core.event import Event
from app.models.core.user import User
from app.models.core.major_location import MajorLocation
from app.models.core.make_model import MakeModel

def test_asset_creation_event():
    """Test that creating an asset automatically creates an event"""
    app = create_app()
    
    with app.app_context():
        print("Testing Asset Creation Event Functionality")
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
        
        # Create a new asset
        print("\nCreating new asset...")
        new_asset = Asset(
            name="Test Asset",
            serial_number="TEST0012024001",
            status="Active",
            major_location_id=location.id,
            make_model_id=make_model.id,
            created_by_id=admin_user.id,
            updated_by_id=admin_user.id
        )
        
        # Enable automatic detail insertion (which also enables event creation)
        Asset.enable_automatic_detail_insertion()
        
        # Add and commit the asset
        db.session.add(new_asset)
        db.session.commit()
        
        print(f"✓ Asset created with ID: {new_asset.id}")
        
        # Check if event was created
        events_after = Event.query.count()
        print(f"Events after asset creation: {events_after}")
        
        if events_after > events_before:
            print("✓ Event was created successfully!")
            
            # Get the latest event
            latest_event = Event.query.order_by(Event.id.desc()).first()
            print(f"Latest event: {latest_event}")
            print(f"Event type: {latest_event.event_type}")
            print(f"Event description: {latest_event.description}")
            print(f"Event user_id: {latest_event.user_id}")
            print(f"Event asset_id: {latest_event.asset_id}")
            print(f"Event major_location_id: {latest_event.major_location_id}")
            
            return True
        else:
            print("❌ No event was created")
            return False

if __name__ == "__main__":
    try:
        success = test_asset_creation_event()
        if success:
            print("\n" + "=" * 50)
            print("✓ Asset creation event test passed!")
        else:
            print("\n" + "=" * 50)
            print("❌ Asset creation event test failed!")
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc() 
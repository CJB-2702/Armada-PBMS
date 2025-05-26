from app import db
from app.models.user import User
from app.models.location import Location
from app.models.asset_type import AssetType
from app.models.asset import Asset, AssetDetail
from app.models.event import Event
import json
from pathlib import Path
from datetime import datetime, timedelta

def load_asset_types():
    """Load default asset types from JSON file if none exist"""
    if AssetType.query.first() is None:
        current_dir = Path(__file__).parent
        json_path = current_dir / 'default_data' / 'FHWA_asset_types.json'
        
        try:
            data = json.loads(json_path.read_text())
                
            for type_data in data['asset_types']:
                asset_type = AssetType(**type_data)
                db.session.add(asset_type)
            
            db.session.commit()
            print("Default asset types loaded successfully!")
            return True
        except Exception as e:
            print(f"Error loading default asset types: {e}")
            db.session.rollback()
            return False
    return True

def load_users(force=False):
    """Load default users if the first user in the JSON file doesn't exist or if force=True"""
    current_dir = Path(__file__).parent
    json_path = current_dir / 'default_data' / 'default_users.json'
    
    try:
        data = json.loads(json_path.read_text())
        first_user_data = data['users'][0]
        
        if force or not User.query.filter_by(user_id=first_user_data['user_id']).first():
            for user_data in data['users']:
                user = User(**user_data)
                db.session.add(user)
            
            db.session.commit()
            print("Default users loaded successfully!")
            return True
    except Exception as e:
        print(f"Error loading default users: {e}")
        db.session.rollback()
        return False
    return True

def load_locations(force=False):
    """Load default locations if the first location in the JSON file doesn't exist or if force=True"""
    current_dir = Path(__file__).parent
    json_path = current_dir / 'default_data' / 'default_locations.json'
    
    try:
        data = json.loads(json_path.read_text())
        first_location_data = data['locations'][0]
        
        if force or not Location.query.filter_by(location_id=first_location_data['location_id']).first():
            for location_data in data['locations']:
                location = Location(**location_data)
                db.session.add(location)
            
            db.session.commit()
            print("Default locations loaded successfully!")
            return True
    except Exception as e:
        print(f"Error loading default locations: {e}")
        db.session.rollback()
        return False
    return True

def load_assets(force=False):
    """Load default assets if the first asset in the JSON file doesn't exist or if force=True"""
    current_dir = Path(__file__).parent
    json_path = current_dir / 'default_data' / 'default_assets.json'
    
    try:
        data = json.loads(json_path.read_text())
        first_asset_data = data['assets'][0]
        
        if force or not Asset.query.filter_by(asset_id=first_asset_data['asset_id']).first():
            for asset_data in data['assets']:
                details = asset_data.pop('details')
                asset_type_code = asset_data.pop('asset_type_code')
                asset_type = AssetType.query.filter_by(code=asset_type_code).first()
                
                asset = Asset(
                    common_name=asset_data['common_name'],
                    asset_type_id=asset_type.type_id if asset_type else None,
                    status=asset_data['status']
                )
                db.session.add(asset)
                db.session.flush()  # Get the asset_id
                
                # Convert date string to date object
                if 'date_delivered' in details:
                    details['date_delivered'] = datetime.strptime(details['date_delivered'], '%Y-%m-%d').date()
                
                details['asset_id'] = asset.asset_id
                asset_details = AssetDetail(**details)
                db.session.add(asset_details)
            
            db.session.commit()
            print("Default assets loaded successfully!")
            return True
    except Exception as e:
        print(f"Error loading default assets: {e}")
        db.session.rollback()
        return False
    return True

def load_events(force=False):
    """Load default events if the first event in the JSON file doesn't exist or if force=True"""
    current_dir = Path(__file__).parent
    json_path = current_dir / 'default_data' / 'default_events.json'
    
    try:
        data = json.loads(json_path.read_text())
        first_event_data = data['events'][0]
        
        if force or not Event.query.filter_by(event_id=first_event_data['event_id']).first():
            for event_data in data['events']:
                # Convert days_ago to actual datetime
                days_ago = event_data.pop('days_ago')
                event_data['created_at'] = datetime.now() - timedelta(days=days_ago)
                
                event = Event(**event_data)
                db.session.add(event)
            
            db.session.commit()
            print("Default events loaded successfully!")
            return True
    except Exception as e:
        print(f"Error loading default events: {e}")
        db.session.rollback()
        return False
    return True

def create_admin_user():
    if not User.query.filter_by(user_id=1).first():
        admin = User(user_id=1, username='admin', display_name='System Administrator', role='admin')
        db.session.add(admin)
        db.session.commit()
        print('Admin user created.')

def create_meta_asset():
    if not Asset.query.filter_by(asset_id=1).first():
        meta_asset = Asset(asset_id=1, common_name='Meta Asset', asset_type_id=None, status='meta')
        db.session.add(meta_asset)
        db.session.commit()
        print('Meta asset created.')

def create_default_location():
    if not Location.query.filter_by(location_id=1).first():
        default_location = Location(location_id=1, unique_name='DEFAULT_LOC', common_name='Default Location')
        db.session.add(default_location)
        db.session.commit()
        print('Default location created.')

def load_all_default_data(debug=False):
    """Load all default data into the database"""
    # Always load asset types first as they are required for assets
    if not load_asset_types():
        return False
    
    # Always create admin user, meta asset, and default location
    create_admin_user()
    create_meta_asset()
    create_default_location()
    
    # Only load other data if debug is True
    if debug:
        # Force load default data in debug mode
        load_users(force=True)
        load_locations(force=True)
        load_assets(force=True)
        load_events(force=True)
    
    return True

def print_all_debug():
    """Print all data in the database for debugging"""
    print("\n--- USERS ---")
    for user in User.query.all():
        print(user)
    print("\n--- LOCATIONS ---")
    for loc in Location.query.all():
        print(loc)
    print("\n--- ASSET TYPES ---")
    for atype in AssetType.query.all():
        print(atype)
    print("\n--- ASSETS ---")
    for asset in Asset.query.all():
        print(asset)
        if asset.details:
            print("   Details:", asset.details.to_dict())
    print("\n--- EVENTS ---")
    for event in Event.query.order_by(Event.created_at.desc()).all():
        print(f"Event: {event.title} ({event.event_type})")
        print(f"   Asset: {event.asset.common_name if event.asset else 'None'}")
        print(f"   Created: {event.created_at}")
        print(f"   Description: {event.description}")
        print("   ---") 
from app import db
from app.models.user import User
from app.models.location import Location
from app.models.asset_type import AssetType
from app.models.asset import Asset, AssetDetail
import json
from pathlib import Path
from datetime import datetime

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

def load_users():
    """Load default users if none exist"""
    if User.query.first() is None:
        current_dir = Path(__file__).parent
        json_path = current_dir / 'default_data' / 'default_users.json'
        
        try:
            data = json.loads(json_path.read_text())
                
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

def load_locations():
    """Load default locations if none exist"""
    if Location.query.first() is None:
        current_dir = Path(__file__).parent
        json_path = current_dir / 'default_data' / 'default_locations.json'
        
        try:
            data = json.loads(json_path.read_text())
                
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

def load_assets():
    """Load default assets if none exist"""
    if Asset.query.first() is None:
        current_dir = Path(__file__).parent
        json_path = current_dir / 'default_data' / 'default_assets.json'
        
        try:
            data = json.loads(json_path.read_text())
                
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

def load_all_default_data(debug=False):
    """Load all default data into the database"""
    # Always load asset types first as they are required for assets
    if not load_asset_types():
        return False
    
    # Only load other data if debug is True
    if debug:
        if not load_users():
            return False
        if not load_locations():
            return False
        if not load_assets():
            return False
    
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
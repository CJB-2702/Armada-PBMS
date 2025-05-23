from app import create_app, db
from app.models.user import User
from app.models.asset import Asset
from app.models.location import Location
from app.models.asset_type import AssetType

def init_debug_database():
    """Initialize the database with default data for development"""
    app = create_app()
    
    with app.app_context():
        # Load default data in order of dependencies
        AssetType.load_default_types()
        User.load_default_users()
        Location.load_default_locations()
        Asset.load_default_assets()
        
        print("Debug database initialized successfully!")

if __name__ == '__main__':
    init_debug_database() 
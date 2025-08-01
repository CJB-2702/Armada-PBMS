from app import db
from app.models.core.user import User
from app.models.core.major_location import MajorLocation
from app.models.core.asset_type import AssetType
from app.models.core.make_model import MakeModel
from app.models.core.asset import Asset
from app.models.core.event import Event

def initialize_system_data():
    """Initialize the system with required base data"""
    
    # Check if system user already exists
    system_user = User.query.filter_by(id=0).first()
    if not system_user:
        # Create System User (ID=0)
        system_user = User(
            id=0,
            username='system',
            email='system@assetmanagement.local',
            is_system=True,
            is_admin=False,
            is_active=True
        )
        system_user.set_password('system-password-not-used')
        db.session.add(system_user)
        db.session.commit()
        print("Created System User (ID=0)")
    
    # Check if admin user already exists
    admin_user = User.query.filter_by(id=1).first()
    if not admin_user:
        # Create Admin User (ID=1)
        admin_user = User(
            id=1,
            username='admin',
            email='admin@assetmanagement.local',
            is_system=False,
            is_admin=True,
            is_active=True
        )
        admin_user.set_password('admin123')
        db.session.add(admin_user)
        db.session.commit()
        print("Created Admin User (ID=1)")
    
    # Check if SanDiegoHQ location already exists
    san_diego_location = MajorLocation.query.filter_by(name='SanDiegoHQ').first()
    if not san_diego_location:
        # Create Major Location: "SanDiegoHQ"
        san_diego_location = MajorLocation(
            name='SanDiegoHQ',
            description='Main office location',
            address='San Diego, CA',
            created_by_id=0,
            updated_by_id=0
        )
        db.session.add(san_diego_location)
        db.session.commit()
        print("Created Major Location: SanDiegoHQ")
    
    # Check if Vehicle asset type already exists
    vehicle_type = AssetType.query.filter_by(name='Vehicle').first()
    if not vehicle_type:
        # Create Asset Type: "Vehicle"
        vehicle_type = AssetType(
            name='Vehicle',
            category='Transportation',
            description='Motor vehicles for transportation',
            created_by_id=0,
            updated_by_id=0
        )
        db.session.add(vehicle_type)
        db.session.commit()
        print("Created Asset Type: Vehicle")
    
    # Check if Toyota Corolla make/model already exists
    toyota_corolla = MakeModel.query.filter_by(make='Toyota', model='Corolla').first()
    if not toyota_corolla:
        # Create Model: "Toyota Corolla"
        toyota_corolla = MakeModel(
            make='Toyota',
            model='Corolla',
            year=2023,
            description='Toyota Corolla 2023 model',
            asset_type_id=vehicle_type.id,
            created_by_id=0,
            updated_by_id=0
        )
        db.session.add(toyota_corolla)
        db.session.commit()
        print("Created Make/Model: Toyota Corolla")
    
    # Check if VTC-001 asset already exists
    vtc_001 = Asset.query.filter_by(serial_number='VTC0012023001').first()
    if not vtc_001:
        # Create Asset: "VTC-001"
        vtc_001 = Asset(
            name='VTC-001',
            serial_number='VTC0012023001',
            status='Active',
            major_location_id=san_diego_location.id,
            make_model_id=toyota_corolla.id,
            created_by_id=0,
            updated_by_id=0
        )
        db.session.add(vtc_001)
        db.session.commit()
        print("Created Asset: VTC-001")
    
    # Check if initial event already exists
    initial_event = Event.query.filter_by(description='Adding Generic text').first()
    if not initial_event:
        # Create Event: "Adding Generic text"
        initial_event = Event(
            event_type='System',
            description='Adding Generic text',
            user_id=0,
            asset_id=vtc_001.id
        )
        db.session.add(initial_event)
        db.session.commit()
        print("Created Event: Adding Generic text")
    
    print("System initialization completed successfully!") 
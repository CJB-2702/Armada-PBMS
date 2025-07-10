from app.models.BaseModels.Asset import Asset
from app.models.BaseModels.ProtoClasses import UserCreated
from app.extensions import db
from app.utils.logger import get_logger

logger = get_logger()

Required_system_location = [
    {
        "UID": "SYSTEM",
        "common_name": "System Location",
        "description": "Virtual system location for internal system operations REQUIRED FOR SYSTEM OPERATIONS",
        "status": "active",
        "created_by": 0,
        "location_id": 0
    }
]

class MajorLocation(Asset):
    __tablename__ = 'MajorLocations'

    Country = db.Column(db.String(100))
    State = db.Column(db.String(100))
    City = db.Column(db.String(100))
    Address = db.Column(db.String(100))
    ZipCode = db.Column(db.Integer)
    Misc = db.Column(db.String(100))
    
    def __init__(self, UID, common_name, description, status, created_by=0, Country=None, State=None, City=None, Address=None, ZipCode=None, Misc=None, location_id=None):
        super().__init__(UID, "MajorLocation", common_name, description, status, created_by)
        if location_id is not None:
            self.row_id = location_id
        self.Country = Country
        self.State = State
        self.City = City
        self.Address = Address
        self.ZipCode = ZipCode
        self.Misc = Misc
    

class MinorLocation(Asset):
    __tablename__ = 'MinorLocations'

    # Foreign key will be added after initialization to avoid circular dependencies
    major_location_id = db.Column(db.Integer, nullable=True)
    Building = db.Column(db.String(100))
    Room = db.Column(db.String(100))
    xyz_orgin_type = db.Column(db.String(100))
    x = db.Column(db.Float)
    y = db.Column(db.Float)
    z = db.Column(db.Float)
    bin = db.Column(db.String(100))
    bin_type = db.Column(db.String(100))

    def __init__(self, UID, common_name, description, status, created_by=0, major_location_id=None, Building=None, Room=None, xyz_orgin_type=None, x=None, y=None, z=None, bin=None, bin_type=None):
        super().__init__(UID, "MinorLocation", common_name, description, status, created_by)
        self.major_location_id = major_location_id
        self.Building = Building
        self.Room = Room
        self.xyz_orgin_type = xyz_orgin_type
        self.x = x
        self.y = y
        self.z = z
        self.bin = bin
        self.bin_type = bin_type


def ensure_required_system_location():
    """Ensure required system location exists in the database"""
    logger.info("Starting System Location initialization...")
    logger.info(f"Required system locations to create: {len(Required_system_location)}")
    
    for location_data in Required_system_location:
        try:
            logger.info(f"Checking for system location: {location_data['UID']}")
            existing_location = MajorLocation.query.filter_by(UID=location_data['UID']).first()
            if not existing_location:
                logger.info(f"Creating system location: {location_data['common_name']}")
                location = MajorLocation(
                    UID=location_data['UID'],
                    common_name=location_data['common_name'],
                    description=location_data['description'],
                    status=location_data['status'],
                    created_by=location_data['created_by'],
                    location_id=location_data['location_id']
                )
                db.session.add(location)
                logger.info(f"✓ Created required system location: {location_data['common_name']}")
            else:
                logger.info(f"✓ System location already exists: {location_data['common_name']}")
        except Exception as e:
            logger.error(f"Error creating system location: {e}")
            continue
    
    try:
        db.session.commit()
        logger.info("✓ System location database commit successful")
    except Exception as e:
        logger.error(f"Error committing system location to database: {e}")
        db.session.rollback()
        raise
    
    # Verify final count
    final_count = MajorLocation.query.count()
    logger.info(f"Final system location count: {final_count}")
    logger.info("✓ Required system location check completed")


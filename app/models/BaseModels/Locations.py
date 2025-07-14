from app.models.BaseModels.Asset import AbstractAsset
from app.models.BaseModels.ProtoClasses import UserCreated
from app.extensions import db
from app.utils.logger import get_logger

logger = get_logger()

required_system_locations = [
    {
        "row_id": 0,
        "UID": "SYSTEM",
        "common_name": "System Location",
        "description": "Virtual system location for internal system operations REQUIRED FOR SYSTEM OPERATIONS",
        "status": "Active",
        "created_by": 0
    },
    {
        "row_id": 1,
        "UID": "UNASSIGNED",
        "common_name": "Unassigned",
        "description": "Unassigned location for assets that have not been assigned to a location",
        "status": "Active",
        "created_by": 0
    }
]

class Location(AbstractAsset):
    """Abstract base class for all location types"""
    __abstract__ = True
    
    # Common location fields
    Country = db.Column(db.String(100))
    State = db.Column(db.String(100))
    City = db.Column(db.String(100))
    Address = db.Column(db.String(100))
    ZipCode = db.Column(db.Integer)
    Misc = db.Column(db.String(100))
    
    def __init__(self, UID, common_name, description, status, created_by=0, 
                 Country=None, State=None, City=None, Address=None, ZipCode=None, Misc=None):
        super().__init__(UID, "Location", common_name, description, status, created_by)
        self.Country = Country
        self.State = State
        self.City = City
        self.Address = Address
        self.ZipCode = ZipCode
        self.Misc = Misc

class MajorLocation(Location):
    __tablename__ = 'major_locations'
    
    def __init__(self, UID, common_name, description, status, created_by=0, 
                 Country=None, State=None, City=None, Address=None, ZipCode=None, Misc=None):
        super().__init__(UID, common_name, description, status, created_by, 
                        Country, State, City, Address, ZipCode, Misc)
        # Override asset_type for major locations
        self.asset_type = "MajorLocation"

    def delete(self):
        if self.UID in ["SYSTEM", "UNASSIGNED"]:
            raise ValueError("Cannot delete system location - it is required for system operations")
        db.session.delete(self)
        db.session.commit()
    
class MinorLocation(AbstractAsset):
    __tablename__ = 'minor_locations'

    major_location_uid = db.Column(db.String(50), db.ForeignKey('major_locations.UID'), nullable=False)
    Building = db.Column(db.String(100))
    Room = db.Column(db.String(100))
    xyz_orgin_type = db.Column(db.String(100))
    x = db.Column(db.Float)
    y = db.Column(db.Float)
    z = db.Column(db.Float)
    ml_bin = db.Column(db.String(100)) # Minor Location Bin, "bin" is a reserved word
    ml_bin_type = db.Column(db.String(100))

    def __init__(self, common_name, description, status, created_by=0, UID=None, major_location_uid="UNASSIGNED", Building=None, Room=None, xyz_orgin_type=None, x=None, y=None, z=None, ml_bin=None, ml_bin_type=None):
        # If no UID provided, use "PENDING" and it will be set to row_id after insert
        uid_to_use = UID if UID is not None else "PENDING"
        super().__init__(uid_to_use, "MinorLocation", common_name, description, status, created_by)
        self.major_location_uid = major_location_uid
        self.Building = Building
        self.Room = Room
        self.xyz_orgin_type = xyz_orgin_type
        self.x = x
        self.y = y
        self.z = z
        self.ml_bin = ml_bin
        self.ml_bin_type = ml_bin_type

# Event listener to set UID to row_id after insert if UID was "PENDING"
@db.event.listens_for(MinorLocation, 'after_insert')
def set_uid_after_insert(mapper, connection, target):
    if target.UID == "PENDING":
        target.UID = str(target.row_id)
        # Update the database with the new UID
        db.session.execute(
            db.text("UPDATE minor_locations SET UID = :uid WHERE row_id = :row_id"),
            {'uid': str(target.row_id), 'row_id': target.row_id}
        )
        db.session.commit()



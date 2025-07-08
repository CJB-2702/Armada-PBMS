from app.models.BaseModels.Asset import Asset
from app.models.BaseModels.ProtoClasses import UserCreated
from app.extensions import db

#left for refrence"
"""
    UID = db.Column(db.String(50), nullable=False, unique=True)
    asset_type = db.Column(db.String(50), db.ForeignKey('types_assets.value'), default='General')
    common_name = db.Column(db.String(100))
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), default='active')
"""
class MajorLocation(Asset):
    __tablename__ = 'MajorLocations'

    Country = db.Column(db.String(100))
    State = db.Column(db.String(100))
    City = db.Column(db.String(100))
    Address = db.Column(db.String(100))
    ZipCode = db.Column(db.Integer)
    Misc = db.Column(db.String(100))
    def __init__(self, UID, common_name, description, status, created_by=0, Country=None, State=None, City=None, Address=None, ZipCode=None, Misc=None):
        super().__init__(UID, "MajorLocation", common_name, description, status, created_by)
        self.Country = Country
        self.State = State
        self.City = City
        self.Address = Address
        self.ZipCode = ZipCode
        self.Misc = Misc
    

class MinorLocation(Asset):
    __tablename__ = 'MinorLocations'

    major_location_id = db.Column(db.Integer, db.ForeignKey('MajorLocations.row_id'))
    Room = db.Column(db.Float)
    xyz_orgin_type = db.Column(db.String(100))
    x = db.Column(db.Float)
    y = db.Column(db.Float)
    z = db.Column(db.Float)
    bin = db.Column(db.String(100))
    bin_type= db.Column(db.String(100))

    def __init__(self, UID, common_name, description, status, created_by=0, major_location_id=None, Room=None, xyz_orgin_type=None, x=None, y=None, z=None, bin=None, bin_type=None):
        super().__init__(UID, "MinorLocation", common_name, description, status, created_by)
        self.major_location_id = major_location_id
        self.Room = Room
        self.xyz_orgin_type = xyz_orgin_type
        self.x = x
        self.y = y
        self.z = z
        self.bin = bin
        self.bin_type = bin_type
    
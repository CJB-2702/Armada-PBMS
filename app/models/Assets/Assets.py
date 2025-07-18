from app.models.BaseModels.Asset import AbstractAsset, AbstractModel
from app.models.BaseModels.Locations import MinorLocation, MajorLocation
from app.extensions import db



additional_statuses = [
    {
        "name": "Active-C",
        "description": "Active and in use, but requires containments"
    },
    {
        "name": "Available-C",
        "description": "Available and ready to be used, but requires containments"
    },
    {
        "name": "Unavailable-C",
        "description": "Unavailable and not ready to be used, requires containments and is only partially functional"
    },
]

class Asset(AbstractAsset):
    __tablename__ = 'assets'

    home_majorlocation_UID = db.Column(db.String(100), db.ForeignKey('major_locations.UID'), nullable=True, default='UNASSIGNED')
    parent_asset_UID = db.Column(db.String(100), db.ForeignKey('assets.UID'))
    current_majorlocation_UID = db.Column(db.String(100), db.ForeignKey('major_locations.UID'), nullable=False)
    current_minorlocation_UID = db.Column(db.String(100), db.ForeignKey('minor_locations.UID'))
    hours_operated = db.Column(db.Float)
    meter_1 = db.Column(db.Float) 
    meter_1_type = db.Column(db.String(100),db.ForeignKey('generic_types.value'))
    meter_2 = db.Column(db.Float)
    meter_2_type = db.Column(db.String(100),db.ForeignKey('generic_types.value'))

    def __init__(self, 
            UID, asset_type, common_name, description, status,
            parent_asset_UID=None,
            current_majorlocation_UID=None, current_minorlocation_UID=None,
            hours_operated=None,
            meter_1=None, meter_1_type=None,
            meter_2=None, meter_2_type=None,
            created_by=0
        ):
        super().__init__(UID, asset_type, common_name, description, status, created_by)
        self.parent_asset_UID = parent_asset_UID
        self.current_majorlocation_UID = current_majorlocation_UID or self.home_majorlocation_UID
        self.current_minorlocation_UID = current_minorlocation_UID
        self.hours_operated = hours_operated
        self.meter_1 = meter_1
        self.meter_1_type = meter_1_type
        self.meter_2 = meter_2 
        self.meter_2_type = meter_2_type

    def __repr__(self):
        return f"<Asset {self.UID}>"

    @staticmethod
    def validate_meter_type(meter_type):
        """Validate that a meter type exists in grouped_types"""
        if meter_type:
            from app.models.Utility.Lists import GenericTypes
            valid_types = db.session.query(GenericTypes.value)\
                .filter(getattr(GenericTypes, 'group') == 'meter_types')\
                .all()
            valid_types = [t[0] for t in valid_types]
            if meter_type not in valid_types:
                raise ValueError(f"Invalid meter type: {meter_type}. Must be one of: {valid_types}")

    @staticmethod
    def validate_location_hierarchy(major_location_UID, minor_location_UID):
        """Validate that the minor location belongs to the major location"""
        if minor_location_UID:
            minor_loc = MinorLocation.query.filter_by(UID=minor_location_UID).first()
            if not minor_loc or minor_loc.major_location_uid != major_location_UID:
                raise ValueError(f"Minor location {minor_location_UID} must belong to major location {major_location_UID}")

    @classmethod
    def before_insert(cls, mapper, connection, target):
        """Validate meter types and location hierarchy before insert"""
        cls.validate_meter_type(target.meter_1_type)
        cls.validate_meter_type(target.meter_2_type)
        cls.validate_location_hierarchy(target.current_majorlocation_UID, target.current_minorlocation_UID)


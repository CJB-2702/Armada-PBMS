from app.models.BaseModels.Locations import Location
from app.extensions import db

class MiscLocations(Location):
    __tablename__ = 'misc_locations'
    
    # Add unique columns to make this a distinct table
    location_type = db.Column(db.String(100), nullable=False, default="misc")
    contact_person = db.Column(db.String(100))
    contact_phone = db.Column(db.String(100))
    contact_email = db.Column(db.String(100))
    business_hours = db.Column(db.String(200))
    notes = db.Column(db.Text)
    
    def __init__(self, UID, common_name, description, status, created_by=0, 
                 Country=None, State=None, City=None, Address=None, ZipCode=None, Misc=None,
                 location_type="misc", contact_person=None, contact_phone=None, 
                 contact_email=None, business_hours=None, notes=None):
        super().__init__(UID, common_name, description, status, created_by, 
                        Country, State, City, Address, ZipCode, Misc)
        # Override asset_type for misc locations
        self.asset_type = "MiscLocation"
        self.location_type = location_type
        self.contact_person = contact_person
        self.contact_phone = contact_phone
        self.contact_email = contact_email
        self.business_hours = business_hours
        self.notes = notes

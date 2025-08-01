from app.models.core.user_created_base import UserCreatedBase
from app import db

class Asset(UserCreatedBase, db.Model):
    __tablename__ = 'assets'
    
    name = db.Column(db.String(100), nullable=False)
    serial_number = db.Column(db.String(100), unique=True, nullable=False)
    status = db.Column(db.String(50), default='Active')
    major_location_id = db.Column(db.Integer, db.ForeignKey('major_locations.id'), nullable=True)
    make_model_id = db.Column(db.Integer, db.ForeignKey('make_models.id'))
    meter1 = db.Column(db.Float, nullable=True)
    meter2 = db.Column(db.Float, nullable=True)
    meter3 = db.Column(db.Float, nullable=True)
    meter4 = db.Column(db.Float, nullable=True)
    tags = db.Column(db.JSON, nullable=True) # try not to use this if at all possible, left because sometimes users find a good reason.
    
    # Relationships
    major_location = db.relationship('MajorLocation', overlaps="assets")
    make_model = db.relationship('MakeModel', overlaps="assets")
    
    @property
    def asset_type(self):
        """Get the asset type through the make_model relationship"""
        if self.make_model and self.make_model.asset_type:
            return self.make_model.asset_type
        return None
    
    def __repr__(self):
        return f'<Asset {self.name} ({self.serial_number})>' 
from app.models.core.user_created_base import UserCreatedBase
from app import db

class Asset(UserCreatedBase, db.Model):
    __tablename__ = 'assets'
    
    name = db.Column(db.String(100), nullable=False)
    serial_number = db.Column(db.String(100), unique=True, nullable=False)
    status = db.Column(db.String(50), default='Active')
    major_location_id = db.Column(db.Integer, db.ForeignKey('major_locations.id'), nullable=True)
    asset_type_id = db.Column(db.Integer, db.ForeignKey('asset_types.id'), nullable=True)
    make_model_id = db.Column(db.Integer, db.ForeignKey('make_models.id'), nullable=True)
    
    # Relationships are defined in the base class and other models
    
    def __repr__(self):
        return f'<Asset {self.name} ({self.serial_number})>' 
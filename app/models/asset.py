from app import db
from datetime import datetime
from app.models.event import Event
from app.utils.event_logger import log_event

class Asset(db.Model):
    __tablename__ = 'assets'
    
    asset_id = db.Column(db.Integer, primary_key=True)
    common_name = db.Column(db.String(100), nullable=False)
    asset_type_id = db.Column(db.Integer, db.ForeignKey('asset_types.type_id'))
    status = db.Column(db.String(20), nullable=False, default='active')
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    # Relationships
    asset_type = db.relationship('AssetType', backref='assets')
    details = db.relationship('AssetDetail', backref='asset', uselist=False, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'asset_id': self.asset_id,
            'common_name': self.common_name,
            'asset_type_id': self.asset_type_id,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f'<Asset {self.common_name}>'

    @staticmethod
    @log_event('asset_created', 'New Asset Created', 'Asset was created')
    def create_asset_event(asset_id, created_by):
        """Create an event when a new asset is created"""
        return {'asset_id': asset_id, 'created_by': created_by}

class AssetDetail(db.Model):
    __tablename__ = 'asset_details'
    
    asset_id = db.Column(db.Integer, db.ForeignKey('assets.asset_id'), primary_key=True)
    make = db.Column(db.String(50))
    model = db.Column(db.String(50))
    equipment_identifier = db.Column(db.String(50))
    year_manufactured = db.Column(db.Integer)
    date_delivered = db.Column(db.Date)
    location_id = db.Column(db.Integer, db.ForeignKey('locations.location_id'))
    meter1_reading = db.Column(db.Float)
    meter1_type = db.Column(db.String(20))
    fuel_type = db.Column(db.String(20))
    weight = db.Column(db.Float)
    registration_category = db.Column(db.String(50))

    def to_dict(self):
        return {
            'make': self.make,
            'model': self.model,
            'equipment_identifier': self.equipment_identifier,
            'year_manufactured': self.year_manufactured,
            'date_delivered': self.date_delivered.isoformat() if self.date_delivered else None,
            'location_id': self.location_id,
            'meter1_reading': self.meter1_reading,
            'meter1_type': self.meter1_type,
            'fuel_type': self.fuel_type,
            'weight': self.weight,
            'registration_category': self.registration_category
        }

    def __repr__(self):
        return f'<AssetDetail for {self.asset.common_name}>' 
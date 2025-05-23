from app import db
from datetime import datetime
import json
from pathlib import Path

class Asset(db.Model):
    __tablename__ = 'assets'
    
    asset_id = db.Column(db.Integer, primary_key=True)
    common_name = db.Column(db.String(100), nullable=False)
    asset_type_id = db.Column(db.Integer, db.ForeignKey('asset_types.type_id'))
    status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    # Relationships
    details = db.relationship('AssetDetail', backref='asset', uselist=False)
    asset_type = db.relationship('AssetType', backref='assets')

    def to_dict(self):
        return {
            'asset_id': self.asset_id,
            'common_name': self.common_name,
            'asset_type': self.asset_type.name if self.asset_type else None,
            'status': self.status,
            'details': self.details.to_dict() if self.details else None
        }

    def __repr__(self):
        return f'<Asset {self.common_name}>'

    @classmethod
    def load_default_assets(cls):
        """Load default assets from JSON file if none exist"""
        if cls.query.first() is None:
            current_dir = Path(__file__).parent
            json_path = current_dir / 'default_data' / 'default_assets.json'
            
            try:
                data = json.loads(json_path.read_text())
                    
                for asset_data in data['assets']:
                    details = asset_data.pop('details')
                    asset_type_code = asset_data.pop('asset_type_code')
                    asset_type = AssetType.query.filter_by(code=asset_type_code).first()
                    
                    asset = cls(
                        common_name=asset_data['common_name'],
                        asset_type_id=asset_type.type_id if asset_type else None,
                        status=asset_data['status']
                    )
                    db.session.add(asset)
                    db.session.flush()  # Get the asset_id
                    
                    # Convert date string to date object
                    if 'date_delivered' in details:
                        details['date_delivered'] = datetime.strptime(details['date_delivered'], '%Y-%m-%d').date()
                    
                    details['asset_id'] = asset.asset_id
                    asset_details = AssetDetail(**details)
                    db.session.add(asset_details)
                
                db.session.commit()
                print("Default assets loaded successfully!")
            except Exception as e:
                print(f"Error loading default assets: {e}")
                db.session.rollback()

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